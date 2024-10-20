import sqlite3
from flask import current_app
from datetime import datetime, timedelta
import random
import json

from app.utils import is_favorite, toggle_favorite, load_state, get_last_read, chapter_array_to_str, is_read


def get_db_connection():
    conn = sqlite3.connect(f'file:{current_app.config["DB_PATH"]}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_random_annotations(favorite_filter=None, read_filter=None):
    query = """
    SELECT a.id, JSON_EXTRACT(a.annot_data, '$.highlighted_text') as highlighted_text,
           JSON_EXTRACT(a.annot_data, '$.notes') as notes,
           JSON_EXTRACT(a.annot_data, '$.spine_index') as spine_index,
           JSON_EXTRACT(a.annot_data, '$.start_cfi') as start_cfi,
           JSON_EXTRACT(a.annot_data, '$.toc_family_titles') as chapter_array,
           a.timestamp, b.title, b.id as book_id
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE JSON_EXTRACT(a.annot_data, '$.highlighted_text') != ''
    ORDER BY RANDOM()
    LIMIT 1000;
    """

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()

    annotations = [
        {
            "id": row["id"],
            "text": row["highlighted_text"],
            "notes": row["notes"],
            "spine_index": row["spine_index"],
            "start_cfi": row["start_cfi"],
            "book_title": row["title"],
            "book_id": row["book_id"],
            "timestamp": row["timestamp"],
            "chapter_name": chapter_array_to_str(row["chapter_array"]),
            "is_favorite": is_favorite(row["id"]),
            "last_read": get_last_read(row["id"]),
        }
        for row in rows
    ]

    filtered_annotations = filter_annotations(annotations, favorite_filter, read_filter)
    return random.sample(filtered_annotations, min(3, len(filtered_annotations)))


def get_books_with_annotations():
    query = """
    SELECT b.id, b.title, COUNT(a.id) AS annotation_count
    FROM books b
    JOIN annotations a ON a.book = b.id
    WHERE JSON_EXTRACT(a.annot_data, '$.highlighted_text') != ''
    GROUP BY b.id, b.title
    ORDER BY b.title;
    """

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()

    return [
        {
            "book_id": row["id"],
            "book_title": row["title"],
            "annotation_count": row["annotation_count"],
        }
        for row in rows
    ]


def get_book_annotations(book_id, favorite_filter=None, read_filter=None):
    query = """
    SELECT a.id, JSON_EXTRACT(a.annot_data, '$.highlighted_text') as highlighted_text,
           JSON_EXTRACT(a.annot_data, '$.notes') as notes,
           JSON_EXTRACT(a.annot_data, '$.spine_index') as spine_index,
           JSON_EXTRACT(a.annot_data, '$.start_cfi') as start_cfi,
           JSON_EXTRACT(a.annot_data, '$.toc_family_titles') as chapter_array,
           a.timestamp, b.title, b.id as book_id
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE a.book = ? AND JSON_EXTRACT(a.annot_data, '$.highlighted_text') != ''
    ORDER BY a.timestamp;
    """

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (book_id,))
        rows = cur.fetchall()

    if not rows:
        return None

    annotations = [
        {
            "book_title": rows[0]["title"],
            "book_id": rows[0]["book_id"],
            "id": row["id"],
            "text": row["highlighted_text"],
            "notes": row["notes"],
            "spine_index": row["spine_index"],
            "start_cfi": row["start_cfi"],
            "timestamp": row["timestamp"],
            "chapter_name": chapter_array_to_str(row["chapter_array"]),
            "is_favorite": is_favorite(row["id"]),
            "last_read": get_last_read(row["id"]),
        }
        for row in rows
    ]

    filtered_annotations = filter_annotations(annotations, favorite_filter, read_filter)

    return {
        "book_title": rows[0]["title"],
        "book_id": rows[0]["book_id"],
        "annotations": filtered_annotations,
    }


def get_favorited_annotations():
    query = """
    SELECT a.id, JSON_EXTRACT(a.annot_data, '$.highlighted_text') as highlighted_text,
           JSON_EXTRACT(a.annot_data, '$.notes') as notes,
           JSON_EXTRACT(a.annot_data, '$.spine_index') as spine_index,
           JSON_EXTRACT(a.annot_data, '$.start_cfi') as start_cfi,
           JSON_EXTRACT(a.annot_data, '$.toc_family_titles') as chapter_array,
           a.timestamp, b.id as book_id, b.title as book_title
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE JSON_EXTRACT(a.annot_data, '$.highlighted_text') != ''
    ORDER BY b.title, a.timestamp;
    """

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()

    favorited_annotations = {}

    for row in rows:
        if is_favorite(row["id"]):
            book_id = row["book_id"]
            if book_id not in favorited_annotations:
                favorited_annotations[book_id] = {
                    "book_title": row["book_title"],
                    "annotations": [],
                }
            favorited_annotations[book_id]["annotations"].append(
                {
                    "id": row["id"],
                    "book_id": row["book_id"],
                    "text": row["highlighted_text"],
                    "notes": row["notes"],
                    "spine_index": row["spine_index"],
                    "start_cfi": row["start_cfi"],
                    "timestamp": row["timestamp"],
                    "is_favorite": True,
                    "last_read": get_last_read(row["id"]),
                    "chapter_name": chapter_array_to_str(row["chapter_array"]),
                }
            )

    return favorited_annotations


def get_all_annotations(favorite_filter=None, read_filter=None):
    query = """
    SELECT a.id, JSON_EXTRACT(a.annot_data, '$.highlighted_text') as highlighted_text,
           JSON_EXTRACT(a.annot_data, '$.notes') as notes,
           JSON_EXTRACT(a.annot_data, '$.spine_index') as spine_index,
           JSON_EXTRACT(a.annot_data, '$.start_cfi') as start_cfi,
           JSON_EXTRACT(a.annot_data, '$.toc_family_titles') as chapter_array,
           a.timestamp, b.id as book_id, b.title as book_title
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE JSON_EXTRACT(a.annot_data, '$.highlighted_text') != ''
    ORDER BY a.timestamp DESC, b.title;
    """

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()

    annotations = [
        {
            "id": row["id"],
            "text": row["highlighted_text"],
            "notes": row["notes"],
            "spine_index": row["spine_index"],
            "start_cfi": row["start_cfi"],
            "timestamp": row["timestamp"],
            "book_id": row["book_id"],
            "book_title": row["book_title"],
            "chapter_name": chapter_array_to_str(row["chapter_array"]),
            "is_favorite": is_favorite(row["id"]),
            "last_read": get_last_read(row["id"]),
        }
        for row in rows
    ]

    return filter_annotations(annotations, favorite_filter, read_filter)


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
            JSON_EXTRACT(a.annot_data, '$.highlighted_text') != ''
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

    return [
        {
            "book_id": row["book_id"],
            "book_title": row["book_title"],
            "latest_annotation": row["latest_annotation"],
        }
        for row in rows
    ]


def get_flashback_annotations():
    years_ago = random.choice([1, 2, 3])
    current_date = datetime.now()
    target_date = current_date.replace(year=current_date.year - years_ago)
    date_range = 10  # Days before and after the target date

    query = """
    SELECT DISTINCT b.id as book_id, b.title as book_title, a.id as annotation_id,
           JSON_EXTRACT(a.annot_data, '$.highlighted_text') as highlighted_text,
           JSON_EXTRACT(a.annot_data, '$.notes') as notes,
           JSON_EXTRACT(a.annot_data, '$.spine_index') as spine_index,
           JSON_EXTRACT(a.annot_data, '$.start_cfi') as start_cfi,
           JSON_EXTRACT(a.annot_data, '$.toc_family_titles') as chapter_array,
           a.timestamp
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE JSON_EXTRACT(a.annot_data, '$.highlighted_text') != ''
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
        flashback_books.append(
            {
                "book_id": row["book_id"],
                "book_title": row["book_title"],
                "annotation_id": row["annotation_id"],
                "text": row["highlighted_text"],
                "notes": row["notes"],
                "spine_index": row["spine_index"],
                "start_cfi": row["start_cfi"],
                "timestamp": row["timestamp"],
                "chapter_name": chapter_array_to_str(row["chapter_array"]),
                "is_favorite": is_favorite(row["annotation_id"]),
                "last_read": get_last_read(row["annotation_id"]),
            }
        )

    return {"years_ago": years_ago, "books": flashback_books}


def get_highlights_with_notes(favorite_filter=None, read_filter=None):
    query = """
    SELECT a.id, JSON_EXTRACT(a.annot_data, '$.highlighted_text') as highlighted_text,
           JSON_EXTRACT(a.annot_data, '$.notes') as notes,
           JSON_EXTRACT(a.annot_data, '$.spine_index') as spine_index,
           JSON_EXTRACT(a.annot_data, '$.start_cfi') as start_cfi,
           JSON_EXTRACT(a.annot_data, '$.toc_family_titles') as chapter_array,
           a.timestamp, b.id as book_id, b.title as book_title
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE JSON_EXTRACT(a.annot_data, '$.highlighted_text') != ''
      AND JSON_EXTRACT(a.annot_data, '$.notes') != ''
    ORDER BY b.title, a.timestamp;
    """

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()

    highlights_with_notes = {}

    for row in rows:
        annotation = {
            "id": row["id"],
            "book_id": row["book_id"],
            "text": row["highlighted_text"],
            "notes": row["notes"],
            "spine_index": row["spine_index"],
            "start_cfi": row["start_cfi"],
            "timestamp": row["timestamp"],
            "is_favorite": is_favorite(row["id"]),
            "last_read": get_last_read(row["id"]),
            "chapter_name": chapter_array_to_str(row["chapter_array"]),
        }
        
        if filter_annotation(annotation, favorite_filter, read_filter):
            book_id = row["book_id"]
            if book_id not in highlights_with_notes:
                highlights_with_notes[book_id] = {
                    "book_title": row["book_title"],
                    "annotations": [],
                }
            highlights_with_notes[book_id]["annotations"].append(annotation)

    return highlights_with_notes


def filter_annotations(annotations, favorite_filter, read_filter):
    return [
        annotation for annotation in annotations
        if filter_annotation(annotation, favorite_filter, read_filter)
    ]


def filter_annotation(annotation, favorite_filter, read_filter):
    if favorite_filter is not None and annotation["is_favorite"] != favorite_filter:
        return False
    if read_filter is not None and is_read(annotation["id"]) != read_filter:
        return False
    return True
