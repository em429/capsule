import os

class Config:
    DEFAULT_DB_PATH = os.path.join(os.path.expanduser("~"), "R", "books", "metadata.db")
    DB_PATH = os.getenv("BOOKS_DB_PATH", DEFAULT_DB_PATH)
    FAVORITES_FILE = 'favorites.json'
