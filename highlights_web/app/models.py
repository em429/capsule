import sqlite3
from flask import current_app

def get_db_connection():
    # conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn = sqlite3.connect(f'file:{current_app.config["DB_PATH"]}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def get_random_annotations():
    query = """
    SELECT a.id, a.searchable_text, b.title, b.id as book_id
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
        "searchable_text": row["searchable_text"], 
        "title": row["title"], 
        "book_id": row["book_id"]
    } for row in rows]

def get_books_with_annotations():
    query = """
    SELECT DISTINCT b.id, b.title
    FROM books b
    JOIN annotations a ON a.book = b.id
    WHERE a.searchable_text != ''
    ORDER BY b.title;
    """
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    
    return [{"id": row["id"], "title": row["title"]} for row in rows]

def get_book_annotations(book_id):
    query = """
    SELECT a.id, a.searchable_text, b.title
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
            "text": row["searchable_text"]
        } for row in rows]
    }
