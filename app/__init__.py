from flask import Flask, render_template, jsonify, abort, request, url_for, redirect, session
from config import Config
from app.models import (
    get_random_annotations,
    get_books_with_annotations,
    get_book_annotations,
    get_favorited_annotations,
    get_all_annotations,
    get_recent_books,
    get_flashback_annotations,
    get_highlights_with_notes,
)
from app.utils import is_favorite, toggle_favorite, to_datetime, generate_calibre_url, update_last_read

app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env.filters["to_datetime"] = to_datetime
app.jinja_env.filters["generate_calibre_url"] = generate_calibre_url


def get_filter_params():
    favorite_filter = session.get('favorite_filter')
    read_filter = session.get('read_filter')
    
    return favorite_filter, read_filter


@app.route("/", methods=["GET"])
def index():
    favorite_filter, read_filter = get_filter_params()
    annotations = get_random_annotations(favorite_filter, read_filter)
    return render_template("index.html", annotations=annotations, favorite_filter=favorite_filter, read_filter=read_filter)


@app.route("/books", methods=["GET"])
def books_list():
    books = get_books_with_annotations()
    recent_books = get_recent_books()
    flashback_data = get_flashback_annotations()
    return render_template(
        "books.html",
        recent_books=recent_books,
        books=books,
        flashback_data=flashback_data
    )


@app.route("/book/<int:book_id>", methods=["GET"])
def book_annotations(book_id):
    favorite_filter, read_filter = get_filter_params()
    book_data = get_book_annotations(book_id, favorite_filter, read_filter)
    if book_data is None:
        abort(404)
    return render_template("book.html", book_data=book_data, favorite_filter=favorite_filter, read_filter=read_filter)


@app.route("/toggle_favorite/<int:annotation_id>", methods=["POST"])
def toggle_favorite_route(annotation_id):
    success = toggle_favorite(annotation_id)
    return jsonify({"success": success})


@app.route("/update_last_read/<int:annotation_id>", methods=["POST"])
def update_last_read_route(annotation_id):
    new_timestamp = update_last_read(annotation_id)
    return jsonify({"success": True, "new_timestamp": new_timestamp})


@app.route("/favorites", methods=["GET"])
def favorites():
    favorited_annotations = get_favorited_annotations()
    return render_template(
        "favorites.html", favorited_annotations=favorited_annotations
    )


@app.route("/focused", methods=["GET"])
def focused_view():
    book_id = request.args.get("book_id", type=int)
    annotation_id = request.args.get("annotation_id", type=int)
    index = request.args.get("index", 0, type=int)

    if book_id:
        book_data = get_book_annotations(book_id)
        if book_data is None:
            abort(404)
        annotations = book_data["annotations"]
        book_title = book_data["book_title"]
    else:
        annotations = get_all_annotations()
        book_title = "All Books"

    total = len(annotations)

    if annotation_id:
        index = next(
            (i for i, a in enumerate(annotations) if a["id"] == annotation_id), 0
        )
    elif index < 0:
        index = 0
    elif index >= total:
        index = total - 1

    current_annotation = annotations[index]

    return render_template(
        "focused.html",
        annotation=current_annotation,
        index=index,
        total=total,
        book_id=book_id,
        book_title=book_title,
    )


@app.route("/focus/<int:annotation_id>", methods=["GET"])
def focus_annotation(annotation_id):
    book_id = request.args.get("book_id", type=int)
    return redirect(
        url_for("focused_view", book_id=book_id, annotation_id=annotation_id)
    )


@app.route("/highlights_with_notes", methods=["GET"])
def highlights_with_notes():
    favorite_filter, read_filter = get_filter_params()
    annotations = get_highlights_with_notes(favorite_filter, read_filter)
    return render_template("highlights_with_notes.html", annotations=annotations, favorite_filter=favorite_filter, read_filter=read_filter)


@app.route('/toggle_filter/<filter_type>')
def toggle_filter(filter_type):
    current_value = session.get(f'{filter_type}_filter')
    
    if current_value is None:
        session[f'{filter_type}_filter'] = True
    elif current_value is True:
        session[f'{filter_type}_filter'] = False
    else:
        session.pop(f'{filter_type}_filter', None)
    
    return '', 204  # No content response