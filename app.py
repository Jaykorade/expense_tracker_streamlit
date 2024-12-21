import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# Create a connection to SQLite database (or create the database if it doesn't exist)
conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

# Create tables to store users and expenses (if they don't exist)
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    password TEXT
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    user_id TEXT,
                    date TEXT,
                    category TEXT,
                    amount REAL
                )''')
conn.commit()

# Function to hash a password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check if the user exists and the password matches
def check_user_credentials(user_id, password):
    hashed_password = hash_password(password)
    cursor.execute('SELECT * FROM users WHERE user_id = ? AND password = ?', (user_id, hashed_password))
    user = cursor.fetchone()
    return user is not None

# Function to create a new user
def create_user(user_id, password):
    hashed_password = hash_password(password)
    cursor.execute('INSERT INTO users (user_id, password) VALUES (?, ?)', (user_id, hashed_password))
    conn.commit()

# Function to save expense entry to database
def save_expense(user_id, date, category, amount):
    cursor.execute('INSERT INTO expenses (user_id, date, category, amount) VALUES (?, ?, ?, ?)',
                   (user_id, date.strftime('%Y-%m-%d'), category, amount))
    conn.commit()

# Function to load user's expense data from the database
def load_expenses(user_id):
    query = 'SELECT * FROM expenses WHERE user_id = ?'
    df = pd.read_sql(query, conn, params=(user_id,))
    return df

# Login page
def login_page():
    st.title("Login or Sign Up")
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type='password')


    if st.button("Login"):
        if check_user_credentials(user_id, password):
            st.session_state.user_id = user_id
            st.success("Login successful!")
        else:
            st.error("Invalid credentials. Please try again.")

    if st.button("Sign Up"):
        if user_id and password:
            create_user(user_id, password)
            st.success("Account created successfully!")
        else:
            st.error("Please provide a User ID and Password to sign up.")

# Main app layout
def main_app():
    st.title("Daily Expense Tracker")

    # Check if user is logged in
    if 'user_id' in st.session_state:
        user_id = st.session_state.user_id
        st.header(f"Welcome, {user_id}")

        # Display current expenses
        st.subheader("Your Expense Log")
        expenses_df = load_expenses(user_id)
        if not expenses_df.empty:
            st.dataframe(expenses_df)
        else:
            st.write("No expenses recorded yet.")

        # Input new expense
        st.subheader("Add a New Expense")
        date = st.date_input("Date", datetime.today())
        category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Others"])
        amount = st.number_input("Amount", min_value=0.01, format="%.2f")

        if st.button("Save Expense"):
            if amount > 0:
                save_expense(user_id, date, category, amount)
                st.success(f"Expense of {amount} in {category} saved successfully!")
            else:
                st.warning("Please enter a valid amount.")

        # Expense summary
        st.subheader("Expense Summary")
        total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
        st.write(f"Total Expenses: ${total_expenses:.2f}")
    else:
        login_page()

# Run the main app
if __name__ == "__main__":
    main_app()
