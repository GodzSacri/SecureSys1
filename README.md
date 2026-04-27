# 📘 SecureSys - Complete Project Documentation

## 1. Project Overview

**SecureSys** is a secure web-based messaging platform that allows users to send and receive encrypted messages, share files, and manage communications securely. The system features end-to-end encryption, JWT authentication, OTP verification, and an admin dashboard for monitoring user activity.

---

## 2. System Architecture

The project follows a **client-server architecture** with clear separation of concerns:
┌─────────────────────────────────────────────────────────────┐
│ CLIENT (Browser) │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Frontend (HTML/CSS/JS) │ │
│ │ - Login/Register Page │ │
│ │ - Inbox (View messages) │ │
│ │ - Compose (Send messages) │ │
│ │ - Sent (View sent messages) │ │
│ │ - Admin Dashboard │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
│ HTTP/HTTPS (REST API)
▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND (Flask API) │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ API Endpoints │ │
│ │ - Authentication (login/register) │ │
│ │ - Messaging (send/receive) │ │
│ │ - OTP (request/verify) │ │
│ │ - Admin (monitoring) │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Services │ │
│ │ - JWT Token Management │ │
│ │ - AES-256-GCM Encryption │ │
│ │ - Email Service (SMTP) │ │
│ │ - File Upload Service │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ DATABASE (MySQL) │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ users table - User accounts & roles │ │
│ │ messages table - Encrypted messages & attachments │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

## 3. User Flow

### 3.1 Registration Process
User → Login Page → Click "Register" → Fill Form
→ Email Validation → Captcha Verification
→ Submit → Account Created → Redirect to Login

### 3.2 Login Process
User → Enter Credentials → Captcha Verification
→ JWT Token Generated → Stored in localStorage
→ Redirect to Inbox (or Admin if admin role)

### 3.3 Sending a Message
User → Compose Page → Enter Recipient Email
→ Email Validation (checks if user exists)
→ Write Subject & Message → Optional File Attachments
→ Toggle Encryption → Send
→ Message Encrypted (AES-256-GCM) → Stored in Database

### 3.4 Reading a Message
User → Click on Message → OTP Modal Appears
→ Request OTP (sent to email) → Enter OTP Code
→ Verify OTP → Message Decrypted & Displayed
→ Can Reply to Message

### 3.5 Admin Monitoring
Admin → Login → Admin Dashboard
→ View Online Users (last 5 minutes)
→ View Suspicious Activity (multiple IPs)
→ View Doctor Weekly Message Stats
→ Register New Users (doctor/client role)

text

---

## 4. Security Layers

| Layer | Technology | Implementation |
|-------|-----------|----------------|
| **Authentication** | JWT | Token stored in localStorage, included in every API request |
| **Encryption** | AES-256-GCM | Military-grade symmetric encryption for messages and files |
| **OTP Verification** | 6-digit code | Sent via email, expires in 5 minutes |
| **Password Security** | bcrypt | Hashed before database storage |
| **SQL Injection** | Parameterized queries | Prepared statements throughout |
| **File Security** | Secure filenames | Extension whitelist, encrypted before storage |

### Code Examples

**JWT Implementation (Frontend):**
```javascript
// Token stored in localStorage
localStorage.setItem('access_token', token);

// Included in every API request
headers: { 'Authorization': `Bearer ${token}` }
Encryption Layer (Backend):

python
# Encryption
encrypted = MessageEncryption.encrypt_message(message)

# Decryption (requires OTP)
decrypted = MessageEncryption.decrypt_message(encrypted)

5. File Structure
Frontend (main branch)

frontend/
├── static/
│   ├── mess.css              # Main styling (gradients, layouts, modals)
│   └── mess.js               # Core JavaScript (API calls, auth, UI)
└── templates/
    ├── login.html            # Login/Register with captcha
    ├── inbox.html            # Display received messages
    ├── compose.html          # Compose and send messages
    ├── sent.html             # Display sent messages
    ├── admin.html            # Admin dashboard
    └── viewmessage.html      # Single message view with reply
Backend (backend branch)

backend/
├── app.py                    # Main Flask application (all endpoints)
├── requirements.txt          # Python dependencies
└── uploads/                  # Encrypted file storage

database/
└── securesysv4.sql          # Database schema

6. Database Schema
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

7. API Communication Flow
┌─────────────┐      HTTP Request       ┌─────────────┐      SQL Query      ┌─────────────┐
│   Frontend  │ ──────────────────────→ │   Backend   │ ─────────────────→ │  Database   │
│  (Browser)  │   (POST /api/inbox)     │   (Flask)   │   (SELECT ...)     │   (MySQL)   │
│             │                         │             │                    │             │
│             │ ←────────────────────── │             │ ←───────────────── │             │
│             │   JSON Response         │             │   Result Set       │             │
└─────────────┘                         └─────────────┘                    └─────────────┘

Example API Call (Frontend)
const response = await API.fetch("/api/inbox");
const data = await response.json();

Example Handler (Backend)
@app.route('/api/inbox', methods=['GET'])
@jwt_required()
def get_inbox_messages():
    user_email = get_jwt_identity()
    messages = get_messages_from_db(user_email)
    return jsonify({"success": True, "messages": messages})

8. Frontend Features
Captcha Protection (Login/Register)
// Simple math captcha
const a = Math.floor(Math.random() * 10) + 1;
const b = Math.floor(Math.random() * 10) + 1;
captchaAnswer = a + b;
Real-time Email Validation
javascript
emailInput.addEventListener("input", async () => {
    const exists = await API.checkEmail(email);
    if (exists) {
        showEmailValidation("✓ Recipient found", false);
    } else {
        showEmailValidation("✗ No user found", true);
    }
});

Notification System
function showNotification(message, isError) {
    notification.textContent = message;
    notification.classList.add('show');
    setTimeout(() => notification.classList.remove('show'), 3000);
}

9. Admin Dashboard Features
Feature	Description
Online Users Monitoring	Tracks users active in last 5 minutes, shows email, role, last active time, IP address
Suspicious Activity Detection	Identifies users with multiple IPs in last hour to detect account sharing
Doctor Statistics	Weekly message counts for doctor role to track engagement
10. Deployment Strategy
Two-Branch Strategy
Branch	Content	Deployment Target
main	Frontend (HTML/CSS/JS)	Vercel / Netlify
backend	Backend (Flask API)	Render / Heroku
Environment Variables
Backend (.env):

env
JWT_SECRET_KEY=your_secret_key
ENCRYPTION_KEY=32_byte_key_here
DB_HOST=your_database_host
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
Frontend (config):

javascript
const API_URL = 'https://your-backend.onrender.com';

11. Security Best Practices Implemented
Practice	Implementation
Password Storage	bcrypt hashing (not plain text)
Message Encryption	AES-256-GCM (military grade)
Token Security	JWT with 1-hour expiration
OTP Verification	6-digit code, 5-minute expiry
SQL Injection Prevention	Parameterized queries
File Security	Secure filenames, extension whitelist
CORS Protection	Restrict allowed origins
Session Management	Auto-logout on 401 responses

12. Error Handling
Frontend
javascript
try {
    await API.fetch("/api/endpoint");
} catch (error) {
    UI.showNotification(error.message, true);
}
Backend
python
try:
    # operation
except Exception as e:
    return jsonify({"success": False, "msg": str(e)}), 500

13. System Requirements
Development
Python 3.9+
MySQL 8.0+
Modern web browser
Git

Production
Vercel account (frontend)
Render/Heroku account (backend)
MySQL database (AWS RDS, PlanetScale, etc.)
SMTP email service (Gmail, SendGrid, etc.)

14. Performance Considerations
Area                  Optimization
Database	            Indexes on email, sender_email, recipient_email
Sessions	            JWT stateless - no session storage needed
Encryption	           Done client-side where possible
File Uploads	         Max size limited, encrypted before storage
Caching	               ache-control headers prevent sensitive data caching

15. Future Enhancements
Group Chats - Multiple recipients
Read Receipts - Track message views
Message Search - Search encrypted messages
Two-Factor Authentication - Additional security layer
Mobile Apps - React Native / Flutter versions
WebSocket - Real-time message delivery
Self-Destructing Messages - Automatic deletion after viewing
Dark Mode - Theme switching

16. Conclusion
SecureSys is a complete, production-ready secure messaging platform that demonstrates:

✅ Full-stack development with Flask and vanilla JavaScript
✅ Industry-standard security practices
✅ Clean separation of concerns
✅ Modern authentication and encryption
✅ Admin monitoring capabilities
✅ Responsive, user-friendly interface
The system is ready for deployment and can be extended with additional features as needed.

📚 Appendices
A. Technology Stack Summary
Layer	           Technologies
Frontend         HTML5, CSS3, Vanilla JavaScript
Backend	         Python Flask, JWT, bcrypt
Database	       MySQL 8.0
Encryption	     ES-256-GCM, Web Crypto API
Deployment	     Vercel (frontend), Render (backend)

B. Key Files Reference
File	                                     Purpose
frontend/templates/login.html	             User authentication interface
frontend/templates/inbox.html	             Message receiving view
frontend/templates/compose.html            Message creation interface
frontend/static/mess.js	                   Core frontend logic
backend/app.py	                           All Flask API endpoints
database/securesysv4.sql	                 Complete database schema
