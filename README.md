## Capsule for Calibre

Capsule is a webapp for encountering book highlights from the past. It can also aid with reviewing books deliberately.

It's purpose is to aid recall and facilitate serendipity.

I built Capsule because I wasn't reviewing any of my (4500+) highlights I made in my Calibre library. Lots of great insights, ideas, food for thought, mostly being slowly forgotten.

The best way to use Capsule is to run it 24/7 on a server, and open it on your phone whenever you have a few mins. (great alternative to news, social media, etc.)

I know solutions like Readwise exist; but I'd rather not lock my data and invest lots of time into a commercial, closed source webapp that could diseapper any day. Also, I'd rather have my highlights linked to the books they are in and to their exact location using epubcfi. Which is how Calibre stores things.

### Main Features:

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

BOOKS_DB_PATH=/path/to/calibre/metadata.db python3 app.py
```

### Feature Roadmap

- [x] ability to favorite highlights, favorites page
- [x] timestamps, linked to focused view of hl
- [x] annotation count next to book list items
- [x] focused mode
- [x] jump to focused view of book on click
- [x] automatic dark mode
- [x] flashback section
- [x] open book in Calibre epub-viewer
- [ ] display notes next to highlights, if any
- [ ] page showing all highlights that have notes
- [ ] jump to highlight location when opening with epub-viewer
- [ ] use ajax for focused view to avoid full-page refresh
- [ ] keyboard nav in focused view
