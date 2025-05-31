from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import bcrypt
from datetime import timedelta
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# Enhanced CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost", "http://127.0.0.1"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="securesysv2"
    )

# Improved login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "msg": "Missing JSON data"}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"success": False, "msg": "Email and password are required"}), 400

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        db.close()

        if not user:
            return jsonify({"success": False, "msg": "Invalid credentials"}), 401

        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({"success": False, "msg": "Invalid credentials"}), 401

        access_token = create_access_token(identity=email)
        
        return jsonify({
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "email": email
        }), 200

    except Exception as e:
        return jsonify({"success": False, "msg": f"Login error: {str(e)}"}), 500

# Fixed inbox endpoint
@app.route('/api/inbox', methods=['GET'])
@jwt_required()
def get_inbox_messages():
    try:
        user_email = get_jwt_identity()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # Fixed query - using sender_email instead of sender_id
        cursor.execute("""
            SELECT id, sender_email, recipient_email, subject, body, 
                   timestamp, is_encrypted, encrypted_key
            FROM messages 
            WHERE recipient_email = %s 
            ORDER BY timestamp DESC
        """, (user_email,))
        
        messages = cursor.fetchall()
        db.close()
        
        # Convert timestamp to string for JSON serialization
        for message in messages:
            if message['timestamp']:
                message['timestamp'] = message['timestamp'].isoformat()
        
        return jsonify({
            "success": True,
            "messages": messages
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"Failed to load inbox: {str(e)}"
        }), 500

# Add sent messages endpoint
@app.route('/api/sent', methods=['GET'])
@jwt_required()
def get_sent_messages():
    try:
        user_email = get_jwt_identity()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, sender_email, recipient_email, subject, body, 
                   timestamp, is_encrypted, encrypted_key
            FROM messages 
            WHERE sender_email = %s 
            ORDER BY timestamp DESC
        """, (user_email,))
        
        messages = cursor.fetchall()
        db.close()
        
        # Convert timestamp to string for JSON serialization
        for message in messages:
            if message['timestamp']:
                message['timestamp'] = message['timestamp'].isoformat()
        
        return jsonify({
            "success": True,
            "messages": messages
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"Failed to load sent messages: {str(e)}"
        }), 500

# Add send message endpoint
@app.route('/api/send', methods=['POST'])
@jwt_required()
def send_message():
    try:
        user_email = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "msg": "Missing JSON data"}), 400
        
        recipient_email = data.get('recipient_email')
        subject = data.get('subject')
        body = data.get('body')
        is_encrypted = data.get('is_encrypted', 0)
        encrypted_key = data.get('encrypted_key')
        
        if not recipient_email or not subject or not body:
            return jsonify({"success": False, "msg": "Recipient, subject, and body are required"}), 400
        
        # Check if recipient exists
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT email FROM users WHERE email = %s", (recipient_email,))
        recipient = cursor.fetchone()
        
        if not recipient:
            db.close()
            return jsonify({"success": False, "msg": "Recipient not found"}), 404
        
        # Insert message
        cursor.execute("""
            INSERT INTO messages (sender_email, recipient_email, subject, body, is_encrypted, encrypted_key)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_email, recipient_email, subject, body, is_encrypted, encrypted_key))
        
        db.commit()
        db.close()
        
        return jsonify({
            "success": True,
            "msg": "Message sent successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"Failed to send message: {str(e)}"
        }), 500

# Add user validation endpoint
@app.route('/api/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    try:
        user_email = get_jwt_identity()
        return jsonify({
            "success": True,
            "email": user_email
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": "Invalid token"
        }), 401

# Frontend routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/inbox')
def inbox_page():
    return render_template('inbox.html')

@app.route('/compose')
def compose_page():
    return render_template('compose.html')

@app.route('/sent')
def sent_page():
    return render_template('sent.html')

# Add this to handle the initial load
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)