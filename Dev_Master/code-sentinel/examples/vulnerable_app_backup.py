"""
Example Vulnerable Application

This file contains INTENTIONALLY INSECURE code to demonstrate
Code-Sentinel's detection and fixing capabilities.

DO NOT USE THIS CODE IN PRODUCTION!
"""

import os
import sqlite3
import pickle
import hashlib
import yaml
from flask import Flask, request, redirect, Markup

app = Flask(__name__)

# CRITICAL: Hardcoded credentials (CWE-798)
API_KEY = "sk_live_51HqJ8k2eZvKYlo2C9dPJ0Qx"
DATABASE_PASSWORD = "SuperSecret123!"
DATABASE_URL = "postgresql://admin:password123@localhost/mydb"

# MEDIUM: Debug mode enabled (CWE-489)
DEBUG = True
app.debug = True


# CRITICAL: SQL Injection via string concatenation (CWE-89)
@app.route('/user/<user_id>')
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    result = cursor.fetchone()
    return str(result)


# CRITICAL: SQL Injection via concatenation (CWE-89)
@app.route('/search')
def search():
    term = request.args.get('q', '')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Vulnerable to SQL injection
    query = "SELECT * FROM users WHERE name = '" + term + "'"
    cursor.execute(query)
    
    return str(cursor.fetchall())


# HIGH: XSS via unsafe HTML rendering (CWE-79)
@app.route('/profile/<username>')
def profile(username):
    # Vulnerable to XSS
    return Markup(f"<h1>Profile: {username}</h1>")


# MEDIUM: Unsafe redirect (CWE-601)
@app.route('/redirect')
def unsafe_redirect():
    # Vulnerable to open redirect
    next_url = request.args.get('next')
    return redirect(next_url)


# CRITICAL: Command injection (CWE-78)
@app.route('/ping/<host>')
def ping_host(host):
    # Vulnerable to command injection
    result = os.system(f"ping -c 1 {host}")
    return f"Ping result: {result}"


# CRITICAL: Insecure deserialization (CWE-502)
@app.route('/load_session', methods=['POST'])
def load_session():
    data = request.data
    # Vulnerable to arbitrary code execution
    session = pickle.loads(data)
    return str(session)


# HIGH: Weak hash algorithm (CWE-327)
def hash_password(password):
    # Using MD5 for passwords (very weak!)
    return hashlib.md5(password.encode()).hexdigest()


# HIGH: YAML unsafe load (CWE-502)
def load_config(config_file):
    with open(config_file, 'r') as f:
        # Vulnerable to arbitrary code execution
        config = yaml.load(f)
    return config


# HIGH: SSRF via user-controlled URL (CWE-918)
@app.route('/fetch')
def fetch_url():
    import requests
    url = request.args.get('url')
    # Vulnerable to SSRF
    response = requests.get(url)
    return response.text


# MEDIUM: Logging sensitive data (CWE-532)
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Logging password (bad!)
    print(f"Login attempt: {username} with password {password}")
    
    # Also using weak hash
    hashed = hashlib.sha1(password.encode()).hexdigest()
    
    return "Login processed"


# HIGH: Path traversal (CWE-22)
@app.route('/download/<filename>')
def download_file(filename):
    # Vulnerable to path traversal
    filepath = f"/data/{filename}"
    with open(filepath, 'r') as f:
        content = f.read()
    return content


# CRITICAL: Hardcoded encryption key (CWE-321)
def encrypt_data(data):
    from Crypto.Cipher import AES
    # Hardcoded key (very bad!)
    key = b"hardcoded_key123"
    cipher = AES.new(key, AES.MODE_CBC)
    return cipher.encrypt(data)


# CRITICAL: Shell injection via subprocess (CWE-78)
def run_backup(backup_path):
    import subprocess
    # Vulnerable to shell injection
    subprocess.call(f"tar -czf backup.tar.gz {backup_path}", shell=True)


if __name__ == '__main__':
    # Running with debug in production (bad!)
    app.run(host='0.0.0.0', port=5000, debug=True)
