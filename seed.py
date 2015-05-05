"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Ratings, Movie, connect_to_db, db
from datetime import datetime
from server import app

import time
start = time.time()


def load_users():
    """Load users from u.user into database."""

    user_file = open("seed_data/u.user")
    for line in user_file:
        user_info = line.rstrip().split("|")
        user = User(age=user_info[1], zipcode=user_info[4])
        db.session.add(user)
    db.session.commit()

def load_movies():
    """Load movies from u.item into database."""
    movie_file = open("seed_data/u.item")
    start = time.time()

    for line in movie_file:
        movie_info = line.rstrip().split("|")
        if movie_info[2]: 
            release_date = datetime.strptime(movie_info[2], "%d-%b-%Y")
        movie = Movie(movie_name=movie_info[1][:-7], release_date=release_date, imdb_url=movie_info[3])
        db.session.add(movie)
    print "The load_movies for loop took", time.time() - start, "ms to run"    

    db.session.commit()

def load_ratings():
    """Load ratings from u.data into database."""
    
    ratings_file = open("seed_data/u.data")
    start = time.time()
    for line in ratings_file:
        rating_info = line.rstrip().split("\t")
        rating = Ratings(user_id=rating_info[0], movie_id=rating_info[1], movie_score=rating_info[2])
        db.session.add(rating)
    print "The load_ratings for loop took", time.time() - start, "ms to run"    
    db.session.commit()

    

if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_movies()
    load_ratings()

