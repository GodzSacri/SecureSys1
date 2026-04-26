SecureSys - Complete Project Explanation

Project Overview
SecureSys is a secure web-based messaging platform that allows users to send and receive encrypted messages, share files, and manage communications securely. The system features end-to-end encryption, JWT authentication, OTP verification, and an admin dashboard for monitoring user activity.


Architecture
The project follows a client-server architecture with clear separation:

text
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Frontend (HTML/CSS/JS)                  │    │
│  │  - Login/Register Page                               │    │
│  │  - Inbox (View messages)                             │    │
│  │  - Compose (Send messages)                           │    │
│  │  - Sent (View sent messages)                         │    │
│  │  - Admin Dashboard                                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/HTTPS (REST API)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (Flask API)                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    API Endpoints                     │    │
│  │  - Authentication (login/register)                   │    │
│  │  - Messaging (send/receive)                          │    │
│  │  - OTP (request/verify)                              │    │
│  │  - Admin (monitoring)                                │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    Services                          │    │
│  │  - JWT Token Management                              │    │
│  │  - AES-256-GCM Encryption                            │    │
│  │  - Email Service (SMTP)                              │    │
│  │  - File Upload Service                               │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE (MySQL)                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  users table    - User accounts & roles              │    │
│  │  messages table - Encrypted messages & attachments   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘


 User Flow
1. Registration Process
text
User → Login Page → Click "Register" → Fill Form 
  → Email Validation → Captcha Verification 
  → Submit → Account Created → Redirect to Login
2. Login Process
text
User → Enter Credentials → Captcha Verification 
  → JWT Token Generated → Stored in localStorage 
  → Redirect to Inbox (or Admin if admin role)
3. Sending a Message
text
User → Compose Page → Enter Recipient Email 
  → Email Validation (checks if user exists) 
  → Write Subject & Message → Optional File Attachments 
  → Toggle Encryption → Send 
  → Message Encrypted (AES-256-GCM) → Stored in Database
4. Reading a Message
text
User → Click on Message → OTP Modal Appears 
  → Request OTP (sent to email) → Enter OTP Code 
  → Verify OTP → Message Decrypted & Displayed 
  → Can Reply to Message
5. Admin Monitoring
text
Admin → Login → Admin Dashboard 
  → View Online Users (last 5 minutes)
  → View Suspicious Activity (multiple IPs)
  → View Doctor Weekly Message Stats
  → Register New Users (doctor/client role)
🔐 Security Layers
1. Authentication Layer (JWT)
javascript
// Token stored in localStorage
localStorage.setItem('access_token', token);

// Included in every API request
headers: { 'Authorization': `Bearer ${token}` }
2. Encryption Layer (AES-256-GCM)
python
# Encryption
encrypted = MessageEncryption.encrypt_message(message)

# Decryption (requires OTP)
decrypted = MessageEncryption.decrypt_message(encrypted)
3. OTP Layer (Email Verification)
text
1. User requests OTP
2. 6-digit code generated (expires in 5 minutes)
3. Sent via email using SMTP
4. Must be entered before viewing messages
4. Database Security
Passwords hashed with bcrypt

Messages stored encrypted

Prepared statements prevent SQL injection

📁 File Structure Explained
Frontend (main branch)
text
frontend/
├── static/                    # Static assets
│   ├── mess.css              # Main styling (gradients, layouts, modals)
│   └── mess.js               # Core JavaScript (API calls, auth, UI)
└── templates/                # HTML pages
    ├── login.html            # Login/Register with captcha
    ├── inbox.html            # Display received messages
    ├── compose.html          # Compose and send messages
    ├── sent.html             # Display sent messages
    ├── admin.html            # Admin dashboard (online users, stats)
    └── viewmessage.html      # Single message view with reply
Backend (backend branch)
text
backend/
├── app.py                    # Main Flask application (all endpoints)
├── requirements.txt          # Python dependencies
└── uploads/                  # Encrypted file storage

database/
└── securesysv4.sql          # Database schema
🔧 Key Components Explained
1. JWT Authentication
python
# Token creation (backend)
access_token = create_access_token(identity=email)

# Token validation
@jwt_required()
def protected_endpoint():
    user = get_jwt_identity()
2. Message Encryption
python
class MessageEncryption:
    # AES-256-GCM encryption
    def encrypt_message(message):
        iv = secrets.token_bytes(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        # Returns base64 encoded encrypted message
    
    def decrypt_message(encrypted):
        # Decrypts using same key
3. OTP System
python
# Generate 6-digit OTP
otp_code = str(secrets.randbelow(1000000)).zfill(6)

# Store with expiration
otp_store[email] = {"otp": otp_code, "expires_at": expires_at}

# Send via email using SMTP
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.sendmail(SMTP_EMAIL, email, msg.as_string())
4. File Upload
python
# Secure filename
filename = secure_filename(file.filename)

# Encrypt before saving
encrypted_data = MessageEncryption.encrypt_file(file_data)

# Save to uploads folder
with open(filepath, 'wb') as f:
    f.write(encrypted_data)
🎨 Frontend Features
Captcha Protection (Login/Register)
javascript
// Simple math captcha
const a = Math.floor(Math.random() * 10) + 1;
const b = Math.floor(Math.random() * 10) + 1;
captchaAnswer = a + b;
Email Validation
javascript
// Real-time email validation
emailInput.addEventListener("input", async () => {
    const exists = await API.checkEmail(email);
    if (exists) {
        showEmailValidation("✓ Recipient found", false);
    } else {
        showEmailValidation("✗ No user found", true);
    }
});
Notification System
javascript
// Auto-dismissing notifications
function showNotification(message, isError) {
    notification.textContent = message;
    notification.classList.add('show');
    setTimeout(() => notification.classList.remove('show'), 3000);
}

Database Schema Explanation
Users Table
Column	Type	Description
id	INT	Primary key
email	VARCHAR(255)	User's email (unique)
password_hash	VARCHAR(255)	bcrypt hashed password
role	ENUM	admin, doctor, or client
last_active	DATETIME	Last activity timestamp
last_ip	VARCHAR(45)	Last IP address
created_at	DATETIME	Account creation date
Messages Table
Column	Type	Description
id	INT	Primary key
sender_email	VARCHAR(255)	Who sent the message
recipient_email	VARCHAR(255)	Who received the message
subject	TEXT	Message subject (encrypted)
body	TEXT	Message content (encrypted)
timestamp	DATETIME	When message was sent
is_encrypted	TINYINT	1 if encrypted, 0 if plain
attachment_path	VARCHAR(255)	Path to encrypted file
🔄 API Communication Flow
javascript
// Frontend API call
const response = await API.fetch("/api/inbox");
const data = await response.json();

// Backend handler
@app.route('/api/inbox', methods=['GET'])
@jwt_required()
def get_inbox_messages():
    user_email = get_jwt_identity()
    messages = get_messages_from_db(user_email)
    return jsonify({"success": True, "messages": messages})
🚀 Deployment Strategy
Two-Branch Strategy
text
main branch (frontend)     → Deploy to Vercel/Netlify
backend branch (backend)   → Deploy to Render/Heroku
Environment Variables
text
# Backend (.env)
JWT_SECRET_KEY=your_secret_key
ENCRYPTION_KEY=32_byte_key_here
DB_HOST=your_database_host
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Frontend (config)
API_URL=https://your-backend.onrender.com
📈 Admin Features
Online Users Monitoring
Tracks users active in last 5 minutes

Shows email, role, last active time, IP address

Suspicious Activity Detection
Identifies users with multiple IPs in last hour

Helps detect account sharing or compromise

Doctor Statistics
Weekly message counts for doctor role

Helps track doctor engagement

🛡️ Security Best Practices Implemented
Password Storage: bcrypt hashing (not plain text)

Message Encryption: AES-256-GCM (military grade)

Token Security: JWT with 1-hour expiration

OTP Verification: 6-digit code, 5-minute expiry

SQL Injection Prevention: Parameterized queries

File Security: Secure filenames, extension whitelist

CORS Protection: Restrict allowed origins

Session Management: Auto-logout on 401 responses

📝 Error Handling
javascript
// Frontend error handling
try {
    await API.fetch("/api/endpoint");
} catch (error) {
    UI.showNotification(error.message, true);
}

// Backend error handling
try:
    # operation
except Exception as e:
    return jsonify({"success": False, "msg": str(e)}), 500
🎯 System Requirements
For Development
Python 3.9+

MySQL 8.0+

Modern web browser

Git

For Production
Vercel account (frontend)

Render/Heroku account (backend)

MySQL database (AWS RDS, PlanetScale, etc.)

SMTP email service (Gmail, SendGrid, etc.)

📊 Performance Considerations
Database Indexes: On email, sender_email, recipient_email

JWT Stateless: No session storage needed

Encryption: Done client-side where possible

File Uploads: Max size limited, encrypted before storage

Caching: Cache-control headers prevent sensitive data caching

🔮 Future Enhancements
Group Chats: Multiple recipients

Read Receipts: Track message views

Message Search: Search encrypted messages

Two-Factor Authentication: Additional security layer

Mobile Apps: React Native / Flutter versions

WebSocket: Real-time message delivery

Message Deletion: Self-destructing messages

Dark Mode: Theme switching

📚 Conclusion
SecureSys is a complete, production-ready secure messaging platform that demonstrates:

Full-stack development with Flask and vanilla JavaScript

Industry-standard security practices

Clean separation of concerns

Modern authentication and encryption

Admin monitoring capabilities

Responsive, user-friendly interface

The system is ready for deployment and can be extended with additional features as needed.
