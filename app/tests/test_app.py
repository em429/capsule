import unittest
from app import app
from app.models import (
    get_random_annotations,
    get_books_with_annotations,
    get_book_annotations,
    get_favorited_annotations,
    get_all_annotations,
    get_recent_books,
    get_flashback_annotations
)
from app.utils import is_favorite, toggle_favorite, load_favorites
import json

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'random', response.data)

    def test_books_list_route(self):
        response = self.client.get('/books')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Flashback', response.data)
        self.assertIn(b'Recently Annotated Books', response.data)
        self.assertIn(b'All books with highlights', response.data)

    def test_book_annotations_route(self):
        # Assuming there's at least one book with ID 1
        response = self.client.get('/book/55')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'focus', response.data)

    def test_toggle_favorite_route(self):
        # Assuming there's an annotation with ID 1
        response = self.client.post('/toggle_favorite/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('success', data)

    def test_favorites_route(self):
        response = self.client.get('/favorites')
        self.assertEqual(response.status_code, 200)
        #self.assertIn(b'Favorites', response.data)

    def test_focused_view_route(self):
        # Test with book_id
        response = self.client.get('/focused?book_id=55&index=0')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Next >', response.data)

        # Test without book_id
        response = self.client.get('/focused?index=0')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Next >', response.data)

    def test_get_random_annotations(self):
        with app.app_context():
            annotations = get_random_annotations()
            self.assertEqual(len(annotations), 3)
            for annotation in annotations:
                self.assertIn('id', annotation)
                self.assertIn('text', annotation)
                self.assertIn('title', annotation)
                self.assertIn('book_id', annotation)
                self.assertIn('timestamp', annotation)

    def test_get_books_with_annotations(self):
        with app.app_context():
            books = get_books_with_annotations()
            self.assertTrue(len(books) > 0)
            for book in books:
                self.assertIn('id', book)
                self.assertIn('title', book)
                self.assertIn('annotation_count', book)

    def test_get_book_annotations(self):
        with app.app_context():
            # Assuming there's at least one book with ID 1
            book_data = get_book_annotations(55)
            self.assertIsNotNone(book_data)
            self.assertIn('title', book_data)
            self.assertIn('id', book_data)
            self.assertIn('annotations', book_data)
            self.assertTrue(len(book_data['annotations']) > 0)

    def test_get_favorited_annotations(self):
        with app.app_context():
            favorited = get_favorited_annotations()
            self.assertIsInstance(favorited, dict)
            for book_id, book_data in favorited.items():
                self.assertIn('title', book_data)
                self.assertIn('annotations', book_data)
                self.assertTrue(len(book_data['annotations']) > 0)

    def test_get_all_annotations(self):
        with app.app_context():
            annotations = get_all_annotations()
            self.assertTrue(len(annotations) > 0)
            for annotation in annotations:
                self.assertIn('id', annotation)
                self.assertIn('text', annotation)
                self.assertIn('timestamp', annotation)
                self.assertIn('book_id', annotation)
                self.assertIn('book_title', annotation)

    def test_get_recent_books(self):
        with app.app_context():
            recent_books = get_recent_books()
            self.assertEqual(len(recent_books), 3)
            for book in recent_books:
                self.assertIn('id', book)
                self.assertIn('title', book)
                self.assertIn('latest_annotation', book)

    def test_get_flashback_annotations(self):
        with app.app_context():
            flashback = get_flashback_annotations()
            self.assertIn('years_ago', flashback)
            self.assertIn('books', flashback)
            self.assertTrue(len(flashback['books']) > 0)

    def test_favorites_functionality(self):
        with app.app_context():
            # Test toggling favorites
            annotation_id = 12  # Assuming there's an annotation with ID 12
            initial_state = is_favorite(annotation_id)
            toggle_favorite(annotation_id)
            self.assertNotEqual(initial_state, is_favorite(annotation_id))
            toggle_favorite(annotation_id)
            self.assertEqual(initial_state, is_favorite(annotation_id))

            # Test loading favorites
            favorites = load_favorites()
            self.assertIsInstance(favorites, dict)

if __name__ == '__main__':
    unittest.main()
