from flask import render_template, current_app, request, redirect, url_for, \
    flash
from flask_login import login_user, logout_user

import itucsdb1973.data_model as data_model
from itucsdb1973.data_model import get_user
from forms import LoginForm, RegisterForm
from passlib.hash import pbkdf2_sha256 as hasher
from itucsdb1973.db_handler import NotUniqueError


def home():
    return render_template("home_page.html")


def search_movie():
    db = current_app.config["db"]
    genres = db.select("movie_genre join genre",
                       ("id", "name", "count(name)"),
                       on_conditions="genre_id=id",
                       group_by="name, genre.id",
                       order_by="count desc"
                       )
    if request.method == "GET":
        return render_template("search_page.html", genres=genres)
    else:
        genre_ids = request.form.getlist("genre_id")
        print(genre_ids)
        film_name = request.form.get("search_query").strip()
        if not (film_name and genre_ids):
            return render_template("search_page.html", genres=genres)

        place_holder = ", ".join(str(id_) for id_ in range(len(genre_ids)))
        columns = "title, release_date, language, overview"
        query = f"""SELECT DISTINCT id, {columns} FROM movie JOIN movie_genre 
                            ON id=movie_id 
                            WHERE 
                                genre_id in ({place_holder}) and 
                                title ILIKE '%{film_name}%'"""
        movies = []
        for row in db._execute(query):
            id_, *datum = row
            movies.append(((id_,),
                           data_model.Movie.from_sql_data(columns.split(", "),
                                                          datum)))

        if not movies:
            return render_template("placeholder.html",
                                   text="No movies matching with specified criteria")
        return render_template("discover_page.html", movies=movies)


# TODO: Show movies ordered by vote count and then name
def discover():
    db = current_app.config["db"]
    if request.method == "GET":
        movies = db.get_items(data_model.Movie)
        # print(movies)
        return render_template("discover_page.html", movies=movies)
    else:
        movie_key = request.form.get("movie_key")
        db.delete_items(data_model.Movie, id=movie_key)
        return redirect(url_for("discover"))


# TODO: Show movie details and create a way to edit them
def movie(movie_id):
    db = current_app.config["db"]
    if request.method == "GET":
        _, movie = db.get_item(data_model.Movie, id=movie_id)
        movie_genres = db.select("movie_genre join genre", ("name",),
                                 on_conditions="genre_id=id",
                                 movie_id=movie_id)
        movie_genres = [id[0] for id in movie_genres]
        genres = db.get_items(data_model.Genre)
        return render_template("movie_page.html",
                               movie=movie, movie_genres=movie_genres,
                               genres=genres)
    else:
        title = request.form.get("title")
        print(title)
        movie = data_model.Movie(False, **request.form)
        print(movie)
        movie_id = db.update_items(movie, id=movie_id)[0][0]
        print(movie_id)
        genre_ids = request.form.get("genres")
        print(genre_ids)
        db.delete_rows("movie_genre", returning="", movie_id=movie_id)
        for genre_id in genre_ids:
            db.insert_values("movie_genre", movie_id=movie_id,
                             genre_id=genre_id, returning="")

        movie_genres = db.select("movie_genre join genre", ("name",),
                                 on_conditions="genre_id=id",
                                 movie_id=movie_id)
        movie_genres = [id[0] for id in movie_genres]
        genres = db.get_items(data_model.Genre)
        return render_template("movie_page.html",
                               movie=movie, movie_genres=movie_genres,
                               genres=genres)



def notifications():
    return render_template("placeholder.html", text="Notifications")


def profile():
    return render_template("placeholder.html", text="Profile")


# TODO: Implement functionality of selecting genre, country for movie
def add_movie():
    db = current_app.config["db"]
    if request.method == "GET":
        genres = db.get_items(data_model.Genre)
        return render_template("add_movie_page.html", genres=genres)
    else:
        movie = data_model.Movie(False, **request.form)
        movie_id = db.add_item(movie)[0][0]
        genre_ids = request.form.getlist("genres")
        for genre_id in genre_ids:
            db.insert_values("movie_genre", movie_id=movie_id,
                             genre_id=genre_id, returning="")

        return redirect("/")


def add_single_field_item(item):
    db = current_app.config["db"]
    class_ = getattr(data_model, item.title())
    items = db.get_items(class_)
    item_names = [item.name for _, item in items]
    if request.method == "GET":
        return render_template("add_single_field_item_page.html", item=item,
                               items=items)
    else:
        item_name = request.form[item].title()
        if item_name in item_names:
            flash(f"{item.title()}: {item_name} already exists")
        else:
            obj = class_(item_name)
            db.add_item(obj)
            flash(f"{item.title()}: {item_name} is added")
            items = db.get_items(class_)

        return render_template("add_single_field_item_page.html", item=item,
                               items=items)


# TODO: login page should not be displayed if user is already logged in
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.data["username"]
        user = get_user(username)
        if user is not None:
            password = form.data["password"]
            if hasher.verify(password, user.password):
                login_user(user)
                flash("You have logged in.")
                next_page = request.args.get("next", url_for("home"))
                return redirect(next_page)
        flash("Invalid credentials.")
    return render_template("login_page.html", form=form)


def logout():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("home"))


def signup():
    form = RegisterForm(request.form)
    db = current_app.config["db"]
    if form.validate_on_submit():
        password = hasher.hash(form.password.data)
        user = data_model.UserM(form.username.data, password,
                                form.email.data, form.profile_photo.data)
        try:
            db.add_item(user)
        except NotUniqueError as e:
            # FIXME: Show an error message to user
            raise e

        return redirect(url_for('login'))
    return render_template('signup_page.html', form=form)
