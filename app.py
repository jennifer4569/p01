#!usr/bin/python

from flask import Flask, session, render_template, request, redirect, url_for, flash
import os, sys, sqlite3
import util.db_builder
import api

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route("/")
def home():
    if "username" in session:
        print 100000000000000
        return render_template("home.html", username = session['username'])
    print 200000000000
    return render_template("home.html")

@app.route("/createaccount", methods=["GET","POST"])
def make_account():
    return render_template("cr_acct.html")

@app.route("/search", methods=["GET","POST"])
def search():
    try:
        movie = request.form['search']
        if util.db_builder.check_movie(movie):
            print "movie was already in database"
        else:
            print "movie not in database"
            omdb_info = api.omdb_info(movie)
            description = omdb_info['Plot']
            reviews = ''
            recommendation = ''
            rating = omdb_info['imdbRating']
            print "I am here"
            #print movie,description,reviews,recommendation,rating
            util.db_builder.add_movie(movie,description,reviews,recommendation,rating)
            print "movie now in database"
        TITLE = movie
        #NYT API-------------------------------------------------
        nyt_info = api.nyt_info(movie)
        print "is in nyt"
        print nyt_info
        nyt_results = nyt_info['results']
        print nyt_results
        NYT_link = nyt_results[0]['link']['url']
        print NYT_link
        NYT_desc = nyt_results[0]['link']['suggested_link_text']
        print NYT_desc
        #--------------------------------------------------------
        print "stuff"
        #OMDB API-----------------------------------------------=
        omdb_info = api.omdb_info(movie)
        print "is in omdb"
        DIRECTOR = omdb_info['Director']
        PLOT = omdb_info['Plot']
        ACTORS = omdb_info['Actors']
        POSTER = omdb_info['Poster']
        #--------------------------------------------------------
        
        #tastedive_info = api.tastedive_info(movie)
        #if tastedive_info == -1:
            #TASTEDIVE = "No similar results found"
        #else:
            #results = tastedive_info['Results']
            
        print "tastedive"                          
        tastedive_info = api.tastedive_info(movie) 
        if tastedive_info == -1:                   
            TASTEDIVE = "No similar results found" 
            print TASTEDIVE                        
            no_matches = True                      
        else:
            print tastedive_info
            results = tastedive_info['Similar']['Results']
            print 'results'
            if len(results) == 0:
                no_matches = True
                print 'empty'
            else:
                #results is a list of dicts
                for dict in results:               
                    print 'Name: ',dict['Name'],"     "
        print 'end of tastedive stuff'
        return render_template("display.html", title = TITLE, review_link = NYT_link, review_title = NYT_desc, \
                               director = DIRECTOR, actors = ACTORS, plot = PLOT, poster = POSTER, recommended = results)
    except:
        return redirect(url_for("home"))

@app.route("/auth", methods=["GET","POST"])
def auth():
    try:
        username = request.form.get('User')
        password = request.form.get('Pass')
        print 'cred'
        print username, password
        if util.db_builder.auth_user(username,password):
            print 'session:  ',session
            session['username'] = username
            print 'omg'
            session['password'] = password
            print 'session:  ',session
            print 'this the profile'
            return redirect(url_for('profile'))
        else:
            print "invalid user/pass combo" #testing purposes
            return redirect(url_for('home'))
    except:
        return redirect(url_for('home'))


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("home"))
    else:
        return render_template("profile.html", username = session['username'])

@app.route("/signup", methods=["GET", "POST"])
def signup():
    try:
	username = request.form['User']
	password = request.form['Pass']
	util.db_builder.add_user(username,password)
	return redirect(url_for('home'))
    except:
	return redirect(url_for('home'))

@app.route("/logout", methods=["GET", "POST"])
def logout_route():
    print 'logout'
    if "username" in session:
        session.pop("username")
    return redirect("/")
    
if __name__ == "__main__":
    app.debug = True
    app.run()
