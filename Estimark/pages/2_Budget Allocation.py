import streamlit as st
import requests
import json
import os

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

st.title("Budget Allocation for Product")

# Show user's product history if logged in
product_description = st.text_input("Enter Product Description:", "")
if "username" in st.session_state.get("user", {}):
    users = load_user_data()
    user_products = users[st.session_state["user"]["username"]].get("history", [])
    selected_product = st.selectbox("Select a Product from History(optional):", [""] + user_products, index=0)
    
    # Use selected product description if one is chosen
    if selected_product:
        product_description = selected_product

# Product and budget input
total_budget = st.number_input("Enter Total Budget:", min_value=0.0, step=0.01)

# Function to get allocation from AI
def allocate_budget(product_description, total_budget):
    url = "https://api.cohere.ai/v1/generate"
    headers = {
        "Authorization": "Bearer OnGJ23fCsgHfE6XBRA9pRF03vf431T6NV0hQy73R",  # Your API key
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": (
             f"Consider typical industry costs and the complexity of the product. If the budget is not under 50% of the average cost of similar products, respond with 'It is not possible to create this product with that budget.' "           
            f"Given a product description of '{product_description}', "
            f"analyze the market and provide a budget allocation for the following categories: Marketing, Research and Development, Operations, Staffing. "
            f"The total budget is {total_budget}. "
            f"Limit the response to under 300 words, but it doesn't have to be that long. "
            f"Format the response as bullet points with short one-sentence reasoning for each allocation if feasible."
            f"make sure all the categories add up to the entire budget"
        ),
        "model": "command-xlarge-nightly",
        "max_tokens": 600,
        "temperature": 0.0
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        response_data = response.json()
        allocation_text = response_data['generations'][0]['text'].strip()
        
        return [line for line in allocation_text.splitlines() if line.strip()]
        
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        st.error(f"An error occurred: {err}")
    return []

if st.button("Allocate Budget"):
    if product_description and total_budget > 0:
        allocation_result = allocate_budget(product_description, total_budget)
        
        if allocation_result:
            st.write("### Budget Allocation:")
            for line in allocation_result:
                st.write(f"- {line}")
        else:
            st.write("Error: Could not get allocation results.")
    else:
        st.write("Please enter a product description and total budget.")
