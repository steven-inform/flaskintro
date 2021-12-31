# Flask documentation online
# https://flask.palletsprojects.com/en/2.0.x/

from flask import Flask, flash, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mysqldb import MySQL
from var_dump import var_dump
import views

app = Flask(__name__)
app.secret_key = 'GSjzfZGs1IbA83I1huht'

# SQLite config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'covid19'

# to get rows as dictionaries, not tuples
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# some routes in views
app.add_url_rule('/other', view_func=views.other)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['GET','POST'])
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
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error deleting task'


# update
@app.route('/update/<int:id>', methods=['GET', 'POST'])
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
@app.route('/login', methods=['GET','POST'])
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

# test mysql
@app.route('/gemeenten', methods=['GET'])
def gemeenten():
    cur = mysql.connection.cursor()

    # cur.execute("""SELECT * FROM gemeente WHERE det_id = %s""", (id,))
    cur.execute("""SELECT * FROM gemeente""")
    data = cur.fetchall()
    cur.close()  # Closing the cursor

    # var_dump(data)
    return render_template('gemeenten.html', data=data)





if __name__ == "__main__":
    app.run(debug=True)
