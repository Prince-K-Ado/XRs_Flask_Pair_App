from flask import Flask , render_template , redirect , url_for , request , flash , abort , session # type: ignore
from functools import wraps
import sqlite3

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
           flash('Please log in to access this page.', 'warning')
           return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_super_secret_key'
@app.route('/') 
@login_required
def index(): 
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

# Route for handling the login page logic (user: admin, pw: admin) 
@app.route('/login', methods=['GET', 'POST']) 
def login(): 
  error = None 
  if request.method == 'POST': 
    if request.form['username'] != 'admin' or request.form['password'] != 'admin': 
      error = 'Invalid Credentials. Please try again.' 
    else: 
      session['logged_in'] = True
      flash('You are now logged in!')
      return redirect(url_for('welcome')) 
  return render_template('login.html', error=error) 

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You are now logged out!')
    return redirect(url_for('login'))

@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
   if request.method == 'POST':
       title = request.form['title']
       content = request.form['content']

       if not title:
           flash('Title is required!')
       else:
           conn = get_db_connection()
           conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                        (title, content))
           conn.commit()
           conn.close()
           return redirect(url_for('index'))
   return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


@app.route("/welcome") 
@login_required
def welcome(): 
  error = None 
  return render_template('welcome.html', error=error) 

@app.route("/dashboard")
def dashboard():
  return "<h2>Dashboard</h2>"

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

