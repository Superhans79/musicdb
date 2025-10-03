from flask import Flask, render_template, request, redirect, send_file
import mysql.connector
import csv
import io
import random

app = Flask(__name__)

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="musicuser",      # 👈 your MySQL username
        password="musicpass",  # 👈 your MySQL password
        database="musicdb"
    )

# Home page - list all songs
@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    conn.close()
    return render_template("index.html", songs=songs)

# Add a new song
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        artist = request.form["artist"]
        title = request.form["title"]
        song = request.form["song"]
        label = request.form["label"]
        podcast = request.form["podcast_played_on"]
        genre = request.form["genre"]
        bpm = request.form["bpm"]
        song_key = request.form["song_key"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO songs (artist, title, song, label, podcast_played_on, genre, bpm, song_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (artist, title, song, label, podcast, genre, bpm, song_key))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("add.html")

# Random song page
@app.route("/random")
def random_song():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    conn.close()
    if songs:
        song = random.choice(songs)
        return render_template("random.html", song=song)
    else:
        return "No songs in the database yet!"

# Export songs to CSV
@app.route("/export")
def export():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    conn.close()

    if not songs:
        return "No songs available to export!"

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=songs[0].keys())
    writer.writeheader()
    writer.writerows(songs)

    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)
    output.close()

    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name="songs.csv"
    )

if __name__ == "__main__":
    app.run(debug=True)
