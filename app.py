from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('expense.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET'])
def index():
    type_filter = request.args.get('type')  # 'income' vagy 'expense' vagy None
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    conn = get_db_connection()
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if type_filter:
        query += " AND type = ?"
        params.append(type_filter)
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)

    query += " ORDER BY date DESC"
    transactions = conn.execute(query, params).fetchall()

    income_total = conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'").fetchone()[0] or 0
    expense_total = conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'").fetchone()[0] or 0
    balance = income_total - expense_total

    conn.close()
    return render_template(
        'index.html',
        transactions=transactions,
        income_total=income_total,
        expense_total=expense_total,
        balance=balance,
        type_filter=type_filter,
        date_from=date_from,
        date_to=date_to
    )

@app.route('/add', methods=['POST'])
def add():
    amount = request.form['amount']
    description = request.form['description']
    type_ = request.form['type']
    date = request.form['date']

    conn = get_db_connection()
    conn.execute('INSERT INTO transactions (amount, description, type, date) VALUES (?, ?, ?, ?)',
                 (amount, description, type_, date))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM transactions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET'])
def edit(id):
    conn = get_db_connection()
    transaction = conn.execute('SELECT * FROM transactions WHERE id = ?', (id,)).fetchone()
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

    conn = get_db_connection()
    conn.execute('''
        UPDATE transactions
        SET amount = ?, description = ?, type = ?, date = ?
        WHERE id = ?
    ''', (amount, description, type_, date, id))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

