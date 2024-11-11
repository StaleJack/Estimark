import streamlit as st
import requests
import json
import os

# Define the Cohere API key
cohere_api_key = "OnGJ23fCsgHfE6XBRA9pRF03vf431T6NV0hQy73R"

# Path to the user_data.json file
USER_DATA_FILE = "user_data.json"

# Load user data from the JSON file
def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}  # Return empty dict if the file doesn't exist
    with open(USER_DATA_FILE, "r") as file:
        return json.load(file)

# Save updated user data to the JSON file
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file)

# Initialize session state for user
if "user" not in st.session_state:
    st.session_state["user"] = {}

# Login/Signup forms
st.sidebar.header("Login or Sign Up")

# Function to log in the user
def login(username, password):
    users = load_user_data()
    if username in users and users[username]["password"] == password:
        st.session_state["user"] = {"username": username, "history": users[username].get("history", [])}
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
        users[username] = {"password": password, "history": []}
        save_user_data(users)
        st.session_state["user"] = {"username": username, "history": []}
        st.success("Account created and logged in successfully!")

# Input forms for login and signup
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    login(username, password)

if st.sidebar.button("Sign Up"):
    signup(username, password)

# Display logged-in username or prompt to log in
if "username" in st.session_state.get("user", {}):
    st.sidebar.write(f"Logged in as: {st.session_state['user'].get('username', 'Guest')}")
else:
    st.sidebar.write("Please log in or sign up.")

st.title("Product Analysis")

# Product analysis input and history dropdown
product_description = st.text_area("Enter Product Description:", "")
if "username" in st.session_state.get("user", {}):
    users = load_user_data()
    user_products = users[st.session_state["user"]["username"]].get("history", [])
    selected_product = st.selectbox("Select a Product from History:", [""] + user_products, index=0)
    
    # Use selected product description if one is chosen
    if selected_product:
        product_description = selected_product

# Function to get analysis from Cohere API
def analyze_product(product_description):
    url = "https://api.cohere.ai/v1/generate"
    headers = {
        "Authorization": f"Bearer {cohere_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": (
            f"Analyze this product: {product_description}. "
            f"Provide insights in the following categories: Target Audience, Performance, Engagement, Feasibility, Competitors, Suggestions for Improvement, Worth Creating, and Suggested Price. "
            f"Keep the response under 200 words and ensure clarity."
        ),
        "model": "command-xlarge-nightly",
        "max_tokens": 700,
        "temperature": 0.1
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_data = response.json()
        if 'generations' in response_data and len(response_data['generations']) > 0:
            return response_data['generations'][0]['text'].strip()
        else:
            return "Error: No text found in the response."
    else:
        return f"Error: Status Code: {response.status_code}"

if st.button("Analyze"):
    if product_description:
        # Save the product description in the user history
        if "username" in st.session_state.get("user", {}):
            username = st.session_state["user"]["username"]
            users = load_user_data()
            if username in users:
                users[username].setdefault("history", []).append(product_description)
                
                # Limit history to 5 items
                if len(users[username]["history"]) > 5:
                    users[username]["history"] = users[username]["history"][-5:]
                
                save_user_data(users)
                st.session_state["user"]["history"] = users[username]["history"]
        
        # Run the analysis
        analysis_result = analyze_product(product_description)
        
        # Display analysis result
        st.write("### Analysis Result:")
        st.write(analysis_result)

        # Add an orange line underneath the analysis result
        st.markdown("<hr style='border: 1px solid orange;'>", unsafe_allow_html=True)
    else:
        st.write("Please enter a product description.")

# Display the user's analysis history
if "username" in st.session_state.get("user", {}):
    st.write("### Analysis History")
    for desc in st.session_state["user"].get("history", []):
        # Create a button for each product description
        if st.button(desc[:30]):  # Show first 30 characters of description
            # Show the analysis for the clicked description
            analysis_result = analyze_product(desc)
            st.write("### Analysis Result:")
            st.write(analysis_result)
