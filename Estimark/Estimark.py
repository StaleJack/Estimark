import streamlit as st
import json
from pathlib import Path

# Set the page config as the first command in the main script
st.set_page_config(layout="wide")

# Load user data from the JSON file
def load_user_data():
    user_data_file = Path("user_data.json")
    if user_data_file.exists():
        with open(user_data_file, "r") as file:
            return json.load(file)
    else:
        return {}

# Save updated user data to the JSON file
def save_user_data(data):
    with open("user_data.json", "w") as file:
        json.dump(data, file)

# Initialize session state
if "user" not in st.session_state:
    st.session_state["user"] = {}

# Login/Signup forms
st.sidebar.header("Login or Sign Up")

# Function to log in the user
def login(username, password):
    users = load_user_data()
    if username in users and users[username]["password"] == password:
        st.session_state["user"] = {"username": username}
        st.success("Logged in successfully!")
    else:
        st.error("Invalid username or password")

# Function to register a new user
def signup(username, password):
    if len(username) < 3:
        st.error("Username must be at least 3 characters.")
        return
    users = load_user_data()
    if username in users:
        st.error("Username already exists.")
    else:
        users[username] = {"password": password}
        save_user_data(users)
        st.session_state["user"] = {"username": username}
        st.success("Account created and logged in successfully!")

# Input forms for login and signup
username = st.sidebar.text_input("Username", key="login_username")
password = st.sidebar.text_input("Password", type="password", key="login_password")

if st.sidebar.button("Login", key="login_button"):
    login(username, password)

if st.sidebar.button("Sign Up", key="signup_button"):
    signup(username, password)

# Display logged-in username or prompt to log in
if "username" in st.session_state.get("user", {}):
    st.sidebar.write(f"Logged in as: {st.session_state['user'].get('username', 'Guest')}")
else:
    st.sidebar.write("Please log in or sign up.")

# Center the logo in the main content area using more columns
logo_path = Path("static/logo.png")
if logo_path.is_file():
    cols = st.columns(10)  # Create nine columns
    with cols[4]:  # Use the fifth column (index 4)
        st.image(str(logo_path), width=200)  # Adjust width as needed
else:
    st.write("Logo not found in the specified path.")

# Center the slogan
st.markdown(
    """
    <div style="text-align: center;">
        <h3>Your research hub for entrepreneurial support</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Display Home.png at the bottom of the page
home_image_path = Path("static/Home.png")
if home_image_path.is_file():
    st.image(str(home_image_path), use_column_width=True)
else:
    st.write("Home image not found in the specified path.")