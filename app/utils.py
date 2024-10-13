import json
import os
from datetime import datetime

from flask import current_app, url_for


def to_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    return datetime.fromtimestamp(value).strftime(format)


def load_favorites():
    favorites_file = current_app.config["FAVORITES_FILE"]
    if os.path.exists(favorites_file):
        with open(favorites_file, "r") as f:
            return json.load(f)
    return {}


def save_favorites(favorites):
    favorites_file = current_app.config["FAVORITES_FILE"]
    with open(favorites_file, "w") as f:
        json.dump(favorites, f)


def is_favorite(annotation_id):
    favorites = load_favorites()
    return str(annotation_id) in favorites


def toggle_favorite(annotation_id):
    favorites = load_favorites()
    annotation_id_str = str(annotation_id)

    if annotation_id_str in favorites:
        del favorites[annotation_id_str]
    else:
        favorites[annotation_id_str] = True

    save_favorites(favorites)
    return True


def generate_calibre_url(book_id, spine_index, start_cfi):
    return f"calibre://view-book/books/{book_id}/EPUB?open_at=epubcfi(/{(spine_index + 1) * 2}{start_cfi})"


# Calibre stores chapter title as a json array, this function joins it into a string
def chapter_array_to_str(array):
    return " ".join(json.loads(array) if array else [])
