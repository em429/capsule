# Select all
SELECT a.searchable_text, b.title
FROM annotations a
JOIN books b ON a.book = b.id
WHERE a.searchable_text != '';

# Select 3 random
SELECT a.searchable_text, b.title
FROM annotations a
JOIN books b ON a.book = b.id
WHERE a.searchable_text != ''
ORDER BY RANDOM()
LIMIT 3;
