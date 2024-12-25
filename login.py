from flask import session

# Sample user data for authentication
users = {
    'admin@example.com': 'password123'
}

def login(email, password):
    if email in users and users[email] == password:
        session['logged_in'] = True
        return True
    return False

def is_logged_in():
    return session.get('logged_in', False)

def logout():
    session.pop('logged_in', None)
