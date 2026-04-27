from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect
from flask_cors import CORS
import mysql.connector
import bcrypt
from datetime import datetime, timedelta
import os
import sys
from functools import wraps
import hashlib
import secrets
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from werkzeug.utils import secure_filename

# OTP LIB 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# CRITICAL: Set the correct paths to your frontend files
TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'frontend', 'templates')
STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'frontend', 'static')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Debug print to verify paths
print("=" * 50)
print(f"Template folder: {TEMPLATE_FOLDER}")
print(f"Template folder exists: {os.path.exists(TEMPLATE_FOLDER)}")
if os.path.exists(TEMPLATE_FOLDER):
    print(f"Templates found: {os.listdir(TEMPLATE_FOLDER)}")
print("=" * 50)

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask app with CORRECT paths
app = Flask(__name__, 
            template_folder=TEMPLATE_FOLDER,
            static_folder=STATIC_FOLDER)

# ==================== FIXED CORS CONFIGURATION ====================
# Enable CORS for Vercel frontend and local development
CORS(app, 
     origins=[
         "http://localhost:3000",
         "http://localhost:5000",
         "http://127.0.0.1:3000",
         "http://127.0.0.1:5000",
         "https://securesystem-wcd6.vercel.app",
         "https://*.vercel.app",
         "https://*.onrender.com"
     ],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Authorization", "Content-Type", "Accept"],
     expose_headers=["Authorization", "Content-Type"],
     supports_credentials=True,
     max_age=3600)

# Alternative: Add CORS headers to all responses (backup solution)
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', 
                         request.headers.get('Origin', 'https://securesystem-wcd6.vercel.app'))
    response.headers.add('Access-Control-Allow-Headers', 
                         'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# ==================== FIXED DATABASE CONNECTION ====================
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'sql12.freesqldatabase.com'),
        user=os.environ.get('DB_USER', 'sql12824556'),
        password=os.environ.get('DB_PASSWORD', 'bvwi12De5Z'),
        database=os.environ.get('DB_NAME', 'sql12824556')
    )

# OTP storage
otp_store = {}
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', "kyru.roque.ui@phinmaed.com")
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', "wgbj qekv jjtj qnks")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        email = get_jwt_identity()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        db.close()
        if not user or user['role'] != 'admin':
            return jsonify({"success": False, "msg": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

# Encryption Configuration
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'SecureSys2024EncryptKey!!ABCDE')[:32].encode()

class MessageEncryption:
    @staticmethod
    def encrypt_message(message, key=None):
        if key is None:
            key = ENCRYPTION_KEY
        iv = secrets.token_bytes(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(message.encode('utf-8')) + encryptor.finalize()
        return base64.b64encode(iv + ciphertext + encryptor.tag).decode('utf-8')

    @staticmethod
    def decrypt_message(encrypted_message, key=None):
        if key is None:
            key = ENCRYPTION_KEY
        try:
            data = base64.b64decode(encrypted_message)
            iv, tag = data[:12], data[-16:]
            ciphertext = data[12:-16]
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            return (decryptor.update(ciphertext) + decryptor.finalize()).decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return "[Decryption Failed]"

    @staticmethod
    def encrypt_file(file_data, key=None):
        if key is None:
            key = ENCRYPTION_KEY
        iv = secrets.token_bytes(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(file_data) + encryptor.finalize()
        return iv + ciphertext + encryptor.tag

    @staticmethod
    def decrypt_file(encrypted_data, key=None):
        if key is None:
            key = ENCRYPTION_KEY
        try:
            iv = encrypted_data[:12]
            tag = encrypted_data[-16:]
            ciphertext = encrypted_data[12:-16]
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None

    @staticmethod
    def hash_sha256(text):
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

# ==================== TEST ROUTES ====================
@app.route('/test')
def test():
    return "Flask is working! Your server is running."

@app.route('/debug')
def debug():
    return f"""
    <html>
    <body>
        <h1>Debug Info</h1>
        <p>Template folder: {app.template_folder}</p>
        <p>Template folder exists: {os.path.exists(app.template_folder)}</p>
        <p>Files in template folder: {os.listdir(app.template_folder) if os.path.exists(app.template_folder) else 'NOT FOUND'}</p>
        <hr>
        <a href="/">Go to Login</a> | <a href="/test">Test</a>
    </body>
    </html>
    """

# ==================== API ENDPOINTS ====================
@app.route('/api/login', methods=['POST'])
def login():
    db = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "msg": "Missing JSON data"}), 400

        email = data.get('email')
        password = data.get('password')
        ip_address = request.remote_addr

        if not email or not password:
            return jsonify({"success": False, "msg": "Email and password are required"}), 400

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user or not user.get('password_hash'):
            return jsonify({"success": False, "msg": "Invalid credentials"}), 401

        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({"success": False, "msg": "Invalid credentials"}), 401

        cursor.execute(
            "UPDATE users SET last_active = NOW(), last_ip = %s WHERE email = %s",
            (ip_address, email)
        )
        db.commit()

        access_token = create_access_token(identity=email)
        return jsonify({
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "email": email,
            "role": user['role']
        }), 200

    except Exception as e:
        return jsonify({"success": False, "msg": f"Login error: {str(e)}"}), 500
    finally:
        if db:
            db.close()

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "msg": "Missing JSON data"}), 400

        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'client').lower()

        if not email or not password:
            return jsonify({"success": False, "msg": "Email and password are required"}), 400

        if role not in ['admin', 'doctor', 'client']:
            role = 'client'

        if role == 'admin':
            return jsonify({"success": False, "msg": "Cannot register as admin"}), 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            db.close()
            return jsonify({"success": False, "msg": "Email already registered"}), 409

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
            (email, hashed_password, role)
        )
        db.commit()
        db.close()

        return jsonify({"success": True, "msg": f"User registered successfully as {role}"}), 201

    except Exception as e:
        return jsonify({"success": False, "msg": f"Registration error: {str(e)}"}), 500

@app.route('/api/inbox', methods=['GET'])
@jwt_required()
def get_inbox_messages():
    try:
        user_email = get_jwt_identity()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, sender_email, recipient_email, subject, body, 
                   timestamp, is_encrypted, encrypted_key, attachment_path
            FROM messages 
            WHERE recipient_email = %s 
            ORDER BY timestamp DESC
        """, (user_email,))
        
        messages = cursor.fetchall()
        db.close()
        
        for message in messages:
            if message['timestamp']:
                message['timestamp'] = message['timestamp'].isoformat()
            
            if message['is_encrypted']:
                message['subject'] = MessageEncryption.decrypt_message(message['subject'])
                message['body'] = MessageEncryption.decrypt_message(message['body'])
                message['decrypted'] = True
            else:
                message['decrypted'] = False
        
        return jsonify({
            "success": True,
            "messages": messages
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"Failed to load inbox: {str(e)}"
        }), 500

# [REST OF YOUR API ENDPOINTS - they remain the same]
# (Include all your other routes here: /api/sent, /api/send, /api/encryption-status, etc.)

# ==================== FRONTEND ROUTES ====================
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    return render_template("admin.html")

@app.route('/inbox')
def inbox_page():
    return render_template('inbox.html')

@app.route('/compose')
def compose_page():
    return render_template('compose.html')

@app.route('/sent')
def sent_page():
    return render_template('sent.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    static_folder = os.path.join(PROJECT_ROOT, 'frontend', 'static')
    return send_from_directory(static_folder, filename)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# ==================== MAIN ENTRY POINT ====================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    print("=" * 50)
    print("SecureSys Backend API Server")
    print("=" * 50)
    print(f"Server running on: http://0.0.0.0:{port}")
    print(f"Test: http://0.0.0.0:{port}/test")
    print(f"Debug: http://0.0.0.0:{port}/debug")
    print(f"Debug mode: {debug_mode}")
    print("=" * 50)
    
    app.run(debug=debug_mode, port=port, host='0.0.0.0')
