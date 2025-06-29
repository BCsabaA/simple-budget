from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from . import auth_bp
import sqlite3

def get_user(username):
    conn = sqlite3.connect('expense.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user(username)
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('index'))
        else:
            flash('Hibás felhasználónév vagy jelszó', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))
