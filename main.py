from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '239xcvoiun39uifgujizoujer09uvx43dfpogh0cw'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):

   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(120))
   password = db.Column(db.String(120))
   blogs = db.relationship('Blog', backref='owner')

   def __init__(self, username, password):
       self.username = username
       self.password = password

@app.before_request
def require_login():
    allowed_routes = ['blog','sign_up','log_in','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog')
def blog():
    if request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog_entry.html',blog=blog)
    elif request.args.get('user'):
        user_id = request.args.get('user')
        user = User.query.filter_by(id=user_id).first()
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('user_page.html',blogs=blogs,user=user)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_content = request.form['content']
        blog_owner = User.query.filter_by(username=session['username']).first()
        title_error = ''
        content_error = ''

        if blog_title == '':
            title_error = "Please enter a title."

        if blog_content == '':
            content_error = "Please fill in the body."

        if not (title_error or content_error):
            new_blog = Blog(blog_title, blog_content, blog_owner)
            db.session.add(new_blog)
            db.session.commit()
            new_blog_id = str(new_blog.id)
            return redirect('/blog?id=' + new_blog_id)
        else:
            return render_template('newpost.html', title_error=title_error,
                content_error=content_error, title=blog_title, content=blog_content)

    return render_template('newpost.html')

@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == "" or password == "" or verify == "":
            flash("One or more fields left blank.","error")
            return redirect("/signup")

        if User.query.filter_by(username=username).first():
            flash("Username already exists.","error")
            return redirect("/signup")

        if password != verify:
            flash("Passwords do not match.","error")
            return redirect("/signup")

        if len(username) < 3 or len(username) > 20:
            flash("Invalid username.","error")
            return redirect("/signup")

        if len(password) < 3 or len(password) > 20:
            flash("Invalid password.","error")
            return redirect("/signup")

        new_user = User(username,password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect('/newpost')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def log_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Incorrect password.','error')
            return redirect('/login')
        elif not user:
            flash('Username does not exist.','error')
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def log_out():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html',users=users)

if __name__ == '__main__':
    app.run()