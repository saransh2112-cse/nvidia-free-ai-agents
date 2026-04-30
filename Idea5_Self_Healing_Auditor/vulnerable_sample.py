import sqlite3
import os

# SHCA TEST CASE: Vulnerable & Inefficient Code
API_KEY = "sk-5512-8822-1144-5566" # CRITICAL: Hardcoded Sensitive Key

def get_user_data(username):
    # CRITICAL: SQL Injection Vulnerability
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    print(f"Executing query: {query}") # LOGGING: Should use logging module
    cursor.execute(query)
    return cursor.fetchone()

def calculate_complex_stuff(data_list):
    # PERFORMANCE: Inefficient loop for summation
    total = 0
    for i in range(len(data_list)):
        total = total + data_list[i]
    return total

if __name__ == "__main__":
    user = get_user_data("admin' OR '1'='1")
    print(user)
