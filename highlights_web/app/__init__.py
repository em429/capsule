from flask import Flask, render_template, jsonify, abort
from config import Config
from app.models import get_random_annotations, get_books_with_annotations, get_book_annotations, get_favorited_annotations
from app.utils import is_favorite, toggle_favorite, to_datetime

app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env.filters['to_datetime'] = to_datetime

@app.route('/', methods=['GET'])
def index():
    annotations = get_random_annotations()
    for annotation in annotations:
        annotation['is_favorite'] = is_favorite(annotation['id'])
    return render_template('index.html', annotations=annotations)

@app.route('/books', methods=['GET'])
def books_list():
    books = get_books_with_annotations()
    return render_template('books.html', books=books)

@app.route('/book/<int:book_id>', methods=['GET'])
def book_annotations(book_id):
    book_data = get_book_annotations(book_id)
    if book_data is None:
        abort(404)
    for annotation in book_data['annotations']:
        annotation['is_favorite'] = is_favorite(annotation['id'])
    return render_template('book.html', book_data=book_data)

@app.route('/toggle_favorite/<int:annotation_id>', methods=['POST'])
def toggle_favorite_route(annotation_id):
    success = toggle_favorite(annotation_id)
    return jsonify({"success": success})

@app.route('/favorites', methods=['GET'])
def favorites():
    favorited_annotations = get_favorited_annotations()
    return render_template('favorites.html', favorited_annotations=favorited_annotations)