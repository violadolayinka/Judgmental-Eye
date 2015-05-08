"""Movie Ratings."""
from flask import Flask, render_template, redirect, request, flash, session

from model import User, Ratings, Movie, connect_to_db, db

from jinja2 import StrictUndefined

import correlation


# from flask_debugtoolbar import DebugToolbarExtension

     #   <li><a href= {{ movie.imbd_url }}> View this movie's IMBD page</a></li>

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.movie_name).all()
    return render_template("movies.html", movies=movies)

@app.route("/movies/<int:id>", methods=["GET", "POST"])
def display_and_rate_movie(id):

    """Displays movie information and adds new movie rating or updates existing rating by user."""


    if "logged_in_email" in session:
        logged_in_email = session["logged_in_email"]
        logged_in_user_id = User.query.filter_by(email=logged_in_email).one().user_id # this gets the id of the logged in user
        # query for the rating that has the user_id = logged_in_user_id and the movie_id = id
        existing_rating = Ratings.query.filter_by(user_id = logged_in_user_id, movie_id = id).first() # if the user has not rated the movie before, existing_rating will = None
        if existing_rating: # if our Ratings query returned a rating object
            user_rating_string = "Your current rating for this movie is %d" % (existing_rating.movie_score)
        else:
            user_rating_string = "You have not yet rated this movie."

        if request.method == "GET":
            movie_object = Movie.query.filter_by(movie_id=id).one()
            return render_template("movie_details.html", movie=movie_object, user_rating_string=user_rating_string)

        else:
            new_rating_score = int(request.form.get("rating"))

            if existing_rating: # if our Ratings query returned a rating object, update the movie_score with new_rating
                existing_rating_temp = existing_rating.movie_score #this stores our existing_rating in a temporary variable before it's updated and allows us to call it again in update_string.
                existing_rating.movie_score = new_rating_score
                db.session.add(existing_rating)
                db.session.commit()
                update_string = "Your existing rating for %s is updated from %d to %d." % (existing_rating.movie.movie_name, existing_rating_temp, new_rating_score)
                flash(update_string)
                return redirect("/movies")

            else: # if our Ratings query returned None, add a new rating to the database with the new_rating score
                rating = Ratings(user_id=logged_in_user_id, movie_id=id, movie_score=new_rating_score)
                db.session.add(rating)
                db.session.commit()

                new_rating_string = "You have rated %s a score of %d." % (rating.movie.movie_name, new_rating_score)

                flash(new_rating_string)

                return redirect("/movies")
    else:
        movie_object = Movie.query.filter_by(movie_id=id).one()
        return render_template("movie_details.html", movie=movie_object)



@app.route('/login')
def login_page():
    """Login Page showing login form."""

    return render_template("login.html")

@app.route('/login', methods=["POST"])
def process_login():
    """Processes login form from Login Page."""
    login_email = request.form.get("email")
    login_password = request.form.get("password")

    user_object = User.query.filter_by(email=login_email).first()

    if user_object: # query returns none if login_email not in database
         user_password = user_object.password
         if user_password == login_password:
            session["logged_in_email"] = user_object.email #This keeps a user logged into the session while on site.
            flash("Successfully logged in.")
            return redirect('/user/' + str(user_object.user_id))
         else:
            flash("Password does not match user email.") 
            return redirect('/login') 
    else:
        flash("No such email")
        return redirect('/login')

@app.route('/registration')
def registration():
    """Registers a new user."""
    return render_template("registration.html")

@app.route('/registration', methods=["POST"])
def process_registration():
    """Adds new user to users database."""
    user_email = request.form.get("email")
    user_password = request.form.get("password")
    user_age = request.form.get("age")
    user_zipcode = request.form.get("zip-code")

    user_object = User.query.filter_by(email=user_email).first()
    if user_object: # query returns none if user_email not in database
        flash("Email already registered.")
        return redirect('/registration')
    else:
        user = User(email=user_email, password=user_password, age=user_age, zipcode=user_zipcode)
        db.session.add(user)
        db.session.commit()
        flash("You have successfully registered.  Please log in.")      
        return redirect('/login')

@app.route('/logout')
def logout():
    """Logs user out"""

    del session["logged_in_email"]
    flash("You have successfully logged out.") 
    return redirect('/')

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/user/<int:id>")
def display_user_info(id):
    user_object = User.query.filter_by(user_id=id).one()

    return render_template("user.html", user=user_object)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run()