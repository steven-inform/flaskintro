# Flask documentation online
# https://flask.palletsprojects.com/en/2.0.x/
from todo import *
from flask import Flask, flash, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from var_dump import var_dump
import views
import config

flaskapp = Flask(__name__)
flaskapp.secret_key = config.SECRET_KEY

# SQLite config
flaskapp.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(flaskapp)

# MySQL config
flaskapp.config['MYSQL_HOST'] = config.MYSQL_HOST
flaskapp.config['MYSQL_USER'] = config.MYSQL_USER
flaskapp.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
flaskapp.config['MYSQL_DB'] = config.MYSQL_DB

# to get rows as dictionaries, not tuples
flaskapp.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(flaskapp)

# some routes in views
flaskapp.add_url_rule('/other', view_func=views.other)


# class Todo

@flaskapp.route('/', methods=['GET', 'POST'])
def index():
    session['email'] = "steven@inform.be"
    flash("Dit is een flash bericht", category='message')

    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'Error adding task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks, email=session['email'])


# delete
@flaskapp.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    print(task_to_delete)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error deleting task'


# update
@flaskapp.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task_to_update = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task_to_update.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Error updating task'

    else:
        return render_template('update.html', task=task_to_update)


# login
@flaskapp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or \
                request.form['password'] != 'secret':
            error = 'Invalid credentials'
        else:
            flash('You were successfully logged in')
            return redirect(url_for('index'))

    return render_template('login.html', error=error)


# gemeenten
@flaskapp.route('/gemeenten/', methods=['GET'])
def gemeenten():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM gemeente""")
    data = cur.fetchall()
    cur.close()  # Closing the cursor

    # var_dump(data)
    return render_template('gemeenten.html', data=data)


# gemeente
@flaskapp.route('/gemeente/<id>', methods=['GET'])
def gemeente(id):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM gemeente WHERE det_id = %s""", (id,))
    data = cur.fetchall()
    cur.close()  # Closing the cursor

    return render_template('gemeenten.html', data=data)


# gemeenten/delete
@flaskapp.route('/gemeenten/delete/<id>', methods=['GET'])
def gemeente_delete(id):
    cur = mysql.connection.cursor()
    cur.execute("""DELETE FROM gemeente WHERE det_id = %s""", (id,))
    mysql.connection.commit()
    cur.close()  # Closing the cursor

    return str(cur.rowcount) + " record(s) deleted"


if __name__ == "__main__":
    flaskapp.run(debug=True)
