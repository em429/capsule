import json
import os
from datetime import datetime

from flask import current_app, url_for


def to_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    return datetime.fromtimestamp(value).strftime(format)


def load_state():
    state_file = current_app.config["STATE_FILE"]
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    state_file = current_app.config["STATE_FILE"]
    with open(state_file, "w") as f:
        json.dump(state, f)


def is_favorite(annotation_id):
    state = load_state()
    return state.get(str(annotation_id), {}).get("favorite", False)


def toggle_favorite(annotation_id):
    state = load_state()
    annotation_id_str = str(annotation_id)

    if annotation_id_str not in state:
        state[annotation_id_str] = {"favorite": False, "last_read": None}

    state[annotation_id_str]["favorite"] = not state[annotation_id_str]["favorite"]

    save_state(state)
    return True


def update_last_read(annotation_id):
    state = load_state()
    annotation_id_str = str(annotation_id)

    if annotation_id_str not in state:
        state[annotation_id_str] = {"favorite": False, "last_read": None}

    state[annotation_id_str]["last_read"] = datetime.now().timestamp()

    save_state(state)
    return state[annotation_id_str]["last_read"]


def get_last_read(annotation_id):
    state = load_state()
    last_read = state.get(str(annotation_id), {}).get("last_read", None)
    if last_read:
        return float(last_read)
    return None


def is_read(annotation_id):
    return bool(get_last_read(annotation_id))


def generate_calibre_url(book_id, spine_index, start_cfi):
    return f"calibre://view-book/books/{book_id}/EPUB?open_at=epubcfi(/{(spine_index + 1) * 2}{start_cfi})"


# Calibre stores chapter title as a json array, this function joins it into a string
def chapter_array_to_str(array):
    return " ".join(json.loads(array) if array else [])
