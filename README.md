# CipherChat — Backend

FastAPI backend for CipherChat, a full-stack end-to-end encrypted chat application.

## Live API
Base URL: `https://cipherchat-backend-fuqa.onrender.com`
Interactive docs: `https://cipherchat-backend-fuqa.onrender.com/docs`

## Stack
- **FastAPI** — REST API and WebSocket server
- **SQLAlchemy** + **SQLite** — database ORM and storage
- **python-jose** — JWT authentication
- **bcrypt** — password hashing
- **Uvicorn** — ASGI server

## Security
- Passwords are bcrypt-hashed — never stored in plaintext
- JWTs are signed with a secret key and expire after a set time
- The server stores only ciphertext and IV — it never sees plaintext messages
- Encryption and decryption happen entirely in the browser

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /health | No | Server health check |
| POST | /auth/register | No | Create a new account |
| POST | /auth/login | No | Returns a JWT token |
| GET | /auth/me | Yes | Returns current user info |
| POST | /rooms | Yes | Create a room |
| GET | /rooms | Yes | List your rooms |
| POST | /rooms/join | Yes | Join a room via invite code |
| GET | /rooms/{id}/messages | Yes | Get last 50 messages |
| POST | /rooms/{id}/keys | Yes | Publish your public key |
| GET | /rooms/{id}/keys | Yes | Get all public keys in a room |
| WS | /ws/{id}?token= | Yes | WebSocket for real-time messaging |

## Local Setup

```bash
git clone https://github.com/DannyphantomX2/cipherchat-backend.git
cd cipherchat-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Run tests:
```bash
python -m pytest tests/test_phase1.py -v
```

## Database Schema

| Table | Key Columns |
|---|---|
| users | id, username, email, hashed_password |
| rooms | id, name, invite_code, created_by |
| room_members | room_id, user_id |
| messages | id, room_id, sender_id, recipients (JSON ciphertext) |
| room_keys | room_id, user_id, public_key |

## Known Limitations
- SQLite resets on Render redeploy — use PostgreSQL for production
- Render free tier sleeps after 15 minutes of inactivity
- 3+ person rooms use first shared key only
