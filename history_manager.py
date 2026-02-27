import streamlit as st
import json
import datetime

def get_user_history_file():
    """Retourne le chemin du fichier d'historique pour l'utilisateur connecté."""
    if st.session_state.get("username"):
        return f"{st.session_state['username']}_history.json"
    return "anonymous_history.json" # Fallback for when no user is logged in

def save_history():
    """Sauvegarde l'historique de l'utilisateur dans son fichier JSON dédié."""
    history_file = get_user_history_file()
    if not history_file:
        return
        
    history_to_save = []
    for entry in st.session_state.get('history', []):
        entry_copy = entry.copy()
        if 'image' in entry_copy:
            del entry_copy['image']
        if 'timestamp' in entry_copy and isinstance(entry_copy['timestamp'], datetime.datetime):
            entry_copy['timestamp'] = entry_copy['timestamp'].isoformat()
        history_to_save.append(entry_copy)
    
    with open(history_file, 'w') as f:
        json.dump(history_to_save, f, indent=4)

def load_history():
    """Charge l'historique de l'utilisateur depuis son fichier JSON."""
    history_file = get_user_history_file()
    if not history_file:
        return []
    try:
        with open(history_file, 'r') as f:
            history_from_file = json.load(f)
            for entry in history_from_file:
                if 'timestamp' in entry and isinstance(entry['timestamp'], str):
                    entry['timestamp'] = datetime.datetime.fromisoformat(entry['timestamp'])
            return history_from_file
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def clear_history():
    """Efface le fichier d'historique de l'utilisateur en y écrivant une liste vide."""
    history_file = get_user_history_file()
    if not history_file:
        return
    
    with open(history_file, 'w') as f:
        json.dump([], f)

