from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# SQLite database file
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)


# Create database and table automatically
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add", methods=["POST"])
def add_user():
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()

    if not name:
        return render_template(
            "index.html",
            error="Name cannot be empty."
        )

    try:
        age = int(age)
        if age <= 0:
            raise ValueError
    except ValueError:
        return render_template(
            "index.html",
            error="Age must be a positive number."
        )

    user = User(name=name, age=age)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("users"))


@app.route("/users")
def users():
    all_users = User.query.all()
    return render_template("users.html", users=all_users)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_user(id):
    user = db.session.get(User, id)

    if not user:
        return "User not found", 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()

        if not name:
            return render_template(
                "edit.html",
                user=user,
                error="Name cannot be empty."
            )

        try:
            age = int(age)
            if age <= 0:
                raise ValueError
        except ValueError:
            return render_template(
                "edit.html",
                user=user,
                error="Age must be a positive number."
            )

        user.name = name
        user.age = age

        db.session.commit()

        return redirect(url_for("users"))

    return render_template("edit.html", user=user)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return "User not found", 404

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("users"))


if __name__ == "__main__":
    app.run(debug=True)
