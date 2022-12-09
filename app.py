"""Blogly application."""

from flask import Flask, request, redirect, render_template
from models import db, connect_db, User, Post,DEFAULT_IMAGE_URL
from datetime import date


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

from flask_debugtoolbar import DebugToolbarExtension
app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)

@app.get("/")
def redirect_users():
    """Redirect to list of users"""

    return redirect("/users")

@app.get("/users")
def list_users():
    """List users and show add form."""

    users = User.query.all()
    return render_template("list.html", users=users)


@app.post("/users/new")
def add_user():
    """Add user and redirect to list."""

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    image_url = request.form['image_url'] or None
    # '' ==> falsy, then uses none


    user = User(first_name=first_name, last_name=last_name, image_url=image_url)
    db.session.add(user)
    db.session.commit()

    return redirect(f"/users/{user.id}")


@app.get("/users/new")
def show_add_user():
    """Shows add user form"""

    return render_template('add_user_form.html')

@app.get("/users/<int:user_id>")
def show_user(user_id):
    """Show info on a single user."""

    user = User.query.get_or_404(user_id)
    return render_template("user_detail.html", user=user)

@app.get("/users/<int:user_id>/edit")
def edit_user_form(user_id):
    """Show edit user form"""

    user = User.query.get_or_404(user_id)
    return render_template("edit_user.html", user=user)

@app.post("/users/<int:user_id>/edit")
def edit_user(user_id):
    """Edit user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    user.image_url = request.form["image_url"]

    db.session.commit()

    return redirect(f'/users/{user_id}')

@app.post("/users/<user_id>/delete")
def delete_user(user_id):
    """Deletes user"""

    User.query.filter(User.id==user_id).delete()

    db.session.commit()

    return redirect("/users")

@app.get("/users/<int:user_id>/posts/new")
def show_post_form(user_id):
    """Shows post form to add new post"""
    user = User.query.get_or_404(user_id)
    first_name = user.first_name
    last_name = user.last_name
    full_name = f"{first_name} {last_name}"

    return render_template("new_post_form.html", full_name=full_name, user=user)

@app.post("/users/<int:user_id>/posts/new")
def add_new_post(user_id):
    """Creates new post"""

    user = User.query.get_or_404(user_id)

    title = request.form['title']
    content = request.form['content']

    new_post = Post(user_id=user.id, title=title, content=content)

    db.session.add(new_post)
    user.posts.append(new_post)
    db.session.commit()

    post_id = new_post.id

    return redirect(f"/posts/{post_id}")


@app.get("/posts/<int:post_id>")
def show_post(post_id):
    """Shows a post"""

    post = Post.query.get_or_404(post_id)

    return render_template('post_detail.html', post=post)

@app.get("/posts/<int:post_id>/edit")
def edit_post(post_id):
    """Show edit post form"""

    post = Post.query.get_or_404(post_id)

    return render_template("post_edit_form.html", post=post)

@app.post("/posts/<int:post_id>/edit")
def update_post(post_id):
    """Submit updated post"""

    post = Post.query.get_or_404(post_id)
    title = request.form['title']
    content = request.form['content']

    post.title = title
    post.content = content

    db.session.commit()

    return redirect(f'/posts/{post_id}')

@app.post("/posts/<int:post_id>/delete")
def delete_post(post_id):
    """Deletes the post"""

    post = Post.query.get_or_404(post_id)
    user_id = post.user_id

    db.session.delete(post)

    db.session.commit()

    return redirect(f"/users/{user_id}")


