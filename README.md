## capsule

Small, one-pager webapp that displays annotations made across your Calibre library.

- The frontpage displays 3 random annotations.
- There is a list with all the books that have annotations
- Each book can be viewed, with all annotations in order

Set `BOOKS_DB_PATH` env var to the location of your Calibre `metadata.db` file. It should be in the root of your calibre library folder.

### To run it:

You must have python3 installed, with pip.

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

BOOKS_DB_PATH=/path/to/metadata.db python3 app.py
```

