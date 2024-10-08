import sqlite3
from flask import current_app
from datetime import datetime, timedelta
import random

from app.utils import is_favorite, toggle_favorite, load_favorites


def get_db_connection():
    # conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn = sqlite3.connect(f'file:{current_app.config["DB_PATH"]}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def get_random_annotations():
    query = """
    SELECT a.id, a.searchable_text, a.timestamp, b.title, b.id as book_id
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE a.searchable_text != ''
    ORDER BY RANDOM()
    LIMIT 3;
    """
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    
    return [{
        "id": row["id"],
        "text": row["searchable_text"], 
        "title": row["title"], 
        "book_id": row["book_id"],
        "timestamp": row["timestamp"]
    } for row in rows]

def get_books_with_annotations():
    query = """
    SELECT b.id, b.title, COUNT(a.id) AS annotation_count
    FROM books b
    JOIN annotations a ON a.book = b.id
    WHERE a.searchable_text != ''
    GROUP BY b.id, b.title
    ORDER BY b.title;
    """
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    
    return [{"id": row["id"], "title": row["title"], "annotation_count": row["annotation_count"]} for row in rows]


def get_book_annotations(book_id):
    query = """
    SELECT a.id, a.searchable_text, a.timestamp, b.title
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE a.book = ? AND a.searchable_text != ''
    ORDER BY a.timestamp;
    """
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (book_id,))
        rows = cur.fetchall()
    
    if not rows:
        return None
    
    return {
        "title": rows[0]["title"],
        "annotations": [{
            "id": row["id"],
            "text": row["searchable_text"],
            "timestamp": row["timestamp"]
        } for row in rows]
    }

def get_favorited_annotations():
    query = """
    SELECT a.id, a.searchable_text, a.timestamp, b.id as book_id, b.title as book_title
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE a.searchable_text != ''
    ORDER BY b.title, a.timestamp;
    """
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    
    favorites = load_favorites()
    favorited_annotations = {}
    
    for row in rows:
        if str(row['id']) in favorites:
            book_id = row['book_id']
            if book_id not in favorited_annotations:
                favorited_annotations[book_id] = {
                    'title': row['book_title'],
                    'annotations': []
                }
            favorited_annotations[book_id]['annotations'].append({
                'id': row['id'],
                'text': row['searchable_text'],
                'timestamp': row['timestamp'],
                'is_favorite': True,
            })
    
    return favorited_annotations

def get_all_annotations():
    query = """
    SELECT a.id, a.searchable_text, a.timestamp, b.id as book_id, b.title as book_title
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE a.searchable_text != ''
    ORDER BY a.timestamp DESC, b.title;
    """
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    
    return [{
        "id": row["id"],
        "text": row["searchable_text"],
        "timestamp": row["timestamp"],
        "book_id": row["book_id"],
        "book_title": row["book_title"]
    } for row in rows]

def get_recent_books():
    query = """
    WITH RankedBooks AS (
        SELECT 
            b.id AS book_id,
            b.title AS book_title,
            MAX(a.timestamp) AS latest_annotation,
            ROW_NUMBER() OVER (ORDER BY MAX(a.timestamp) DESC) AS rank
        FROM 
            books b
            JOIN annotations a ON b.id = a.book
        WHERE 
            a.searchable_text != ''
        GROUP BY 
            b.id, b.title
    )
    SELECT book_id, book_title, latest_annotation
    FROM RankedBooks
    WHERE rank <= 3
    ORDER BY latest_annotation DESC;
    """
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    
    return [{
        "id": row["book_id"],
        "title": row["book_title"],
        "latest_annotation": row["latest_annotation"]
    } for row in rows]

def get_flashback_annotations():
    years_ago = random.choice([1, 2, 3])
    current_date = datetime.now()
    target_date = current_date.replace(year=current_date.year - years_ago)
    date_range = 10  # Days before and after the target date

    query = """
    SELECT DISTINCT b.id as book_id, b.title as book_title, a.id as annotation_id, a.searchable_text, a.timestamp
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE a.searchable_text != ''
      AND a.timestamp BETWEEN ? AND ?
    ORDER BY RANDOM()
    LIMIT 1;
    """

    start_date = target_date - timedelta(days=date_range)
    end_date = target_date + timedelta(days=date_range)

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (start_date.timestamp(), end_date.timestamp()))
        rows = cur.fetchall()

    flashback_books = []
    for row in rows:
        flashback_books.append({
            "book_id": row["book_id"],
            "book_title": row["book_title"],
            "annotation_id": row["annotation_id"],
            "text": row["searchable_text"],
            "timestamp": row["timestamp"]
        })

    return {
        "years_ago": years_ago,
        "books": flashback_books
    }
