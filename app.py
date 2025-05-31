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

# Protected endpoints with better error handling
@app.route('/api/inbox', methods=['GET'])
@jwt_required()
def get_inbox_messages():
    try:
        user_email = get_jwt_identity()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT m.*, u.email as sender_email 
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.recipient_email = %s 
            ORDER BY m.timestamp DESC
        """, (user_email,))
        
        messages = cursor.fetchall()
        db.close()
        
        return jsonify({
            "success": True,
            "messages": messages
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"Failed to load inbox: {str(e)}"
        }), 500

# Frontend routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/inbox')
@jwt_required()
def inbox_page():
    return render_template('inbox.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)