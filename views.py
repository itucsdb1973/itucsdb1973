from flask import render_template, current_app, request, redirect, url_for, \
    flash
import itucsdb1973.data_model as data_model


# TODO: Implement login/logout system
def home():
    return render_template("home.html")


def search_movie():
    return render_template("placeholder.html", text="Search movie")


# TODO: Show movies ordered by vote count and then name
def discover():
    db = current_app.config["db"]
    if request.method == "GET":
        movies = db.get_items(data_model.Movie, ("title", "release_date"))
        return render_template("movies.html", movies=movies)
    else:
        form_movie_keys = request.form.getlist("movie_keys")
        for form_movie_key in form_movie_keys:
            db.delete_items(data_model.Movie, id=form_movie_key)
        return redirect(url_for("discover_page"))


# TODO: Show movie details and create a way to edit them
def movie(movie_key):
    return render_template("placeholder.html",
                           text=f"Movie page for movie with id {movie_key}")


def notifications():
    return render_template("placeholder.html", text="Notifications")


def profile():
    return render_template("placeholder.html", text="Profile")


# TODO: Implement functionality of selecting genre, country for movie
def add_movie():
    db = current_app.config["db"]
    if request.method == "GET":
        return render_template("add_movie_page.html")
    else:
        movie = data_model.Movie(**request.form)
        db.add_item(movie)
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
