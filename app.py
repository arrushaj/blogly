"""Blogly application."""

from flask import Flask, request, redirect, render_template
from models import db, connect_db, User, DEFAULT_IMAGE_URL


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
    image_url = request.form['image_url'] or DEFAULT_IMAGE_URL


    user = User(first_name=first_name, last_name=last_name, image_url=image_url)
    db.session.add(user)
    db.session.commit()

    return redirect(f"/users/{user.id}")


@app.get("/users/new")
def show_add_user():
    """shows add user form"""

    return render_template('add_user_form.html')

@app.get("/users/<int:user_id>")
# @app.get("/users/<user_id>")
def show_user(user_id):
    """Show info on a single user."""

    user = User.query.get_or_404(user_id)
    # user = User.query.get_or_404(int(user_id))
    return render_template("user_detail.html", user=user)

@app.get("/users/<user_id>/edit")
def edit_user_form(user_id):
    """Show edit user form"""

    user = User.query.get_or_404(int(user_id))
    return render_template("edit_user.html", user=user)

@app.post("/users/<user_id>/edit")
def edit_user(user_id):
    """Edit user"""

    user = User.query.get_or_404(int(user_id))
    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    user.image_url = request.form["image_url"]

    db.session.commit()

    return redirect(f'/users/{user_id}')

@app.post("/users/<user_id>/delete")
def delete_user(user_id):
    """Delete user"""

    User.query.filter(User.id==user_id).delete()
    # user = got here
    # db.session.delete(user) # need to get user

    db.session.commit()

    return redirect("/users")