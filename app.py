from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from collections import defaultdict
from auth import auth_bp

# Konfiguráció
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key')

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Auth blueprint regisztrálása
app.register_blueprint(auth_bp)

def get_db_connection():
    return engine.connect()

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    type_filter = request.args.get('type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    conn = get_db_connection()
    query = "SELECT * FROM transactions WHERE 1=1"
    params = {}

    if type_filter:
        query += " AND type = :type"
        params['type'] = type_filter
    if date_from:
        query += " AND date >= :date_from"
        params['date_from'] = date_from
    if date_to:
        query += " AND date <= :date_to"
        params['date_to'] = date_to

    query += " ORDER BY date DESC"
    transactions = conn.execute(text(query), params).fetchall()

    income_total = conn.execute(text("SELECT SUM(amount) FROM transactions WHERE type = 'income'")).scalar() or 0
    expense_total = conn.execute(text("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")).scalar() or 0
    balance = income_total - expense_total

    conn.close()
    return render_template('index.html',
                           transactions=transactions,
                           income_total=income_total,
                           expense_total=expense_total,
                           balance=balance,
                           type_filter=type_filter,
                           date_from=date_from,
                           date_to=date_to)

@app.route('/stats')
def stats():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    rows = conn.execute(text('SELECT date, amount, type FROM transactions')).fetchall()
    conn.close()

    data = defaultdict(lambda: {'income': 0, 'expense': 0})
    for row in rows:
        month = str(row['date'])[:7]
        data[month][row['type']] += float(row['amount'])

    sorted_data = sorted(data.items())
    labels = [month for month, _ in sorted_data]
    incomes = [val['income'] for _, val in sorted_data]
    expenses = [val['expense'] for _, val in sorted_data]

    return render_template('stats.html', labels=labels, incomes=incomes, expenses=expenses)

@app.route('/add', methods=['POST'])
def add():
    amount = request.form['amount']
    description = request.form['description']
    type_ = request.form['type']
    date = request.form['date']

    with engine.begin() as conn:
        conn.execute(text('''
            INSERT INTO transactions (amount, description, type, date)
            VALUES (:amount, :description, :type, :date)
        '''), {
            'amount': amount,
            'description': description,
            'type': type_,
            'date': date
        })

    return redirect('/')

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    with engine.begin() as conn:
        conn.execute(text('DELETE FROM transactions WHERE id = :id'), {'id': id})
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn = get_db_connection()
    result = conn.execute(text('SELECT * FROM transactions WHERE id = :id'), {'id': id})
    transaction = result.fetchone()
    conn.close()
    if transaction is None:
        return 'Nem található tétel', 404
    return render_template('edit.html', transaction=transaction)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    amount = request.form['amount']
    description = request.form['description']
    type_ = request.form['type']
    date = request.form['date']

    with engine.begin() as conn:
        conn.execute(text('''
            UPDATE transactions
            SET amount = :amount, description = :description, type = :type, date = :date
            WHERE id = :id
        '''), {
            'amount': amount,
            'description': description,
            'type': type_,
            'date': date,
            'id': id
        })

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

