import json
import os

# Path to the user_data.json file
USER_DATA_FILE = os.path.join('data', 'user_data.json')

def load_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}  # Return empty dict if the file doesn't exist
    with open(USER_DATA_FILE, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file)

def create_user(username, password):
    data = load_data()
    
    if username in data:
        return False  # User already exists
    
    # Initialize user data with an empty history
    data[username] = {
        "username": username,
        "password": password,
        "history": []  # Add the history key
    }
    save_data(data)
    return True

def get_user(username):
    data = load_data()
    return data.get(username)

def update_user_history(username, product_description):
    data = load_data()
    
    if username in data:
        data[username]["history"].append(product_description)  # Append to user's history
        save_data(data)
