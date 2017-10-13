from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

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

@app.route('/blog')
def blog():
    if request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog_entry.html',blog=blog)
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

@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

if __name__ == '__main__':
    app.run()