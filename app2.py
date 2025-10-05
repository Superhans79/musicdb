from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import random
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="musicuser",
    password="musicpass",
    database="musicdb"
)
cursor = db.cursor(dictionary=True)

# Spotify connection
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

def get_album_art(artist, title):
    """Search Spotify for album artwork based on artist + title"""
    query = f"{artist} {title}"
    results = sp.search(q=query, limit=1, type="track")
    if results["tracks"]["items"]:
        return results["tracks"]["items"][0]["album"]["images"][0]["url"]
    return None

# ----------------- ROUTES -----------------

@app.route("/")
def index():
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    return render_template("index.html", songs=songs)

@app.route("/add", methods=["GET", "POST"])
def add_song():
    if request.method == "POST":
        artist = request.form["artist"]
        title = request.form["title"]
        song = request.form["song"]
        label = request.form["label"]
        podcast = request.form["podcast_played_on"]
        genre = request.form["genre"]
        bpm = request.form["bpm"]
        song_key = request.form["song_key"]

        # Fetch album art from Spotify
        album_art_url = get_album_art(artist, title)

        cursor.execute("""
            INSERT INTO songs (artist, title, song, label, podcast_played_on, genre, bpm, song_key, album_art_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (artist, title, song, label, podcast, genre, bpm, song_key, album_art_url))
        db.commit()
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/random")
def random_song():
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    if not songs:
        return "No songs in database yet!"
    song = random.choice(songs)
    return render_template("random.html", song=song)

# ----------------- MAIN -----------------
if __name__ == "__main__":
    app.run(debug=True)
