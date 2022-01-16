from enum import unique
from flask import Flask, json, request, jsonify
from flask.helpers import flash
from flask.templating import render_template
from flask_login.utils import login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import UserMixin, LoginManager, login_manager, login_user, current_user
import os
from werkzeug import routing
from werkzeug.security import check_password_hash

from werkzeug.utils import redirect


app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)
ma = Marshmallow(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    title = db.Column(db.String(100), unique=False)
    content = db.Column(db.String(1000), unique=False)

    def __init__(self, title, content):
        self.title = title
        self.content = content

class PostSchema(ma.Schema):
    class Meta:
        fields = ('title', 'content')


post_schema = PostSchema()
posts_schema = PostSchema(many=True)

# Endpoint to create new post 
@app.route('/blog', methods=["POST"])
def add_post():
    title = request.json['title']
    content = request.json['content']

    new_post = Post(title, content)

    db.session.add(new_post)
    db.session.commit()

    post = Post.query.get(new_post.id)

    return post_schema.jsonify(post)


# Endpoint to query all posts
@app.route('/blogs', methods=["GET"])
def get_posts():
    all_posts = Post.query.all()
    result = posts_schema.dump(all_posts)
    return jsonify(result)

# Endpoint for querying single post
@app.route("/blog/<id>", methods=["GET"])
def get_post(id):
    post = Post.query.get(id)
    return post_schema.jsonify(post)


# Endpoint for updating a post 
@app.route("/blog/<id>", methods=["PUT"])
def post_update(id):
    post = Post.query.get(id)
    title = request.json['title']
    content = request.json['content']

    post.title = title
    post.content = content

    db.session.commit()
    return post_schema.jsonify(post)


# Endpoint for deleting a record
@app.route("/blog/<id>", methods=["DELETE"])
def post_delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()

    return post_schema.jsonify(post)

# User section
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200), nullable=False)
    

# Endpoint for user Login

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=["POST"])
def login():
    
    #login_user(user)
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User.query.filter_by(email='example@gmail.com').first()

    if not user and not check_password_hash(user.password, password):
        flash('Check info and try again!')
        return redirect('/')

    login_user(user)

    return redirect('/blog')


# Endpoint for user Logout
@app.route ('/navigation')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

