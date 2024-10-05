import json
import os
from flask import current_app

def load_favorites():
    favorites_file = current_app.config['FAVORITES_FILE']
    if os.path.exists(favorites_file):
        with open(favorites_file, 'r') as f:
            return json.load(f)
    return {}

def save_favorites(favorites):
    favorites_file = current_app.config['FAVORITES_FILE']
    with open(favorites_file, 'w') as f:
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