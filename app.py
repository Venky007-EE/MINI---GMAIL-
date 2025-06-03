from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for session management

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT NOT NULL UNIQUE,
                 password TEXT NOT NULL)''')
    # Emails table
    c.execute('''CREATE TABLE IF NOT EXISTS emails (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 sender TEXT NOT NULL,
                 recipient TEXT NOT NULL,
                 subject TEXT,
                 body TEXT,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Check if user is logged in
def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            flash('Signup successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists.')
        finally:
            conn.close()
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['email'] = user[1]
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

# Home route (Inbox)
@app.route('/')
@login_required
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM emails WHERE recipient = ? ORDER BY timestamp DESC", (session['email'],))
    emails = c.fetchall()
    conn.close()
    return render_template('index.html', emails=emails, user_email=session['email'])

# Compose email route
@app.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    if request.method == 'POST':
        sender = session['email']
        recipient = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO emails (sender, recipient, subject, body) VALUES (?, ?, ?, ?)",
                 (sender, recipient, subject, body))
        conn.commit()
        conn.close()
        flash('Email sent successfully!')
        return redirect(url_for('index'))
    return render_template('compose.html', user_email=session['email'])

# Reply to email route
@app.route('/reply/<int:email_id>', methods=['GET', 'POST'])
@login_required
def reply(email_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
    email = c.fetchone()
    
    if request.method == 'POST':
        sender = session['email']
        recipient = email[2]  # Original sender becomes recipient
        subject = f"Re: {email[3]}"
        body = request.form['body']
        
        c.execute("INSERT INTO emails (sender, recipient, subject, body) VALUES (?, ?, ?, ?)",
                 (sender, recipient, subject, body))
        conn.commit()
        conn.close()
        flash('Reply sent successfully!')
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('reply.html', email=email, user_email=session['email'])

# Forward email route
@app.route('/forward/<int:email_id>', methods=['GET', 'POST'])
@login_required
def forward(email_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
    email = c.fetchone()
    
    if request.method == 'POST':
        sender = session['email']
        recipient = request.form['recipient']
        subject = f"Fwd: {email[3]}"
        body = f"-------- Forwarded Message --------\nFrom: {email[1]}\n\n{email[4]}"
        
        c.execute("INSERT INTO emails (sender, recipient, subject, body) VALUES (?, ?, ?, ?)",
                 (sender, recipient, subject, body))
        conn.commit()
        conn.close()
        flash('Email forwarded successfully!')
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('compose.html', email=email, forward=True, user_email=session['email'])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)