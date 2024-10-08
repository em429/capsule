## Capsule

Small, Flask webapp for reviwing Calibre annotations (ebook-viewer). Annotations are presented in a variety of ways to aid recall and improve serendipity.

### Features:

- The frontpage displays 3 random annotations
- The books page displays a list of all books with highlights, a 'flashback in time' seciton, and recent books
- Focused mode shows a single annotation at a time. Can be filtered to single book.
- Each book has it's own page with all highlights displayed.
- Ability to favorite highlights, and a favorites page.

Set `BOOKS_DB_PATH` env var to the location of your Calibre `metadata.db` file. It should be in the root of your calibre library folder.

### How to run:

You must have python3 installed, with pip.

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

BOOKS_DB_PATH=/path/to/metadata.db python3 app.py
```

