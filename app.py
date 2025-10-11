from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import random
import os
import psycopg2.extras

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # you can make this any random string

# ==============================
# Database Connection
# ==============================
import os
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    url = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_SL6kgmXIj9Jw@ep-silent-water-adqp55tv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
    result = urlparse(url)
    return psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port,
        sslmode="require"
    )

# ==============================
# Routes
# ==============================

# Home Page – show all songs
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    print("DEBUG SONGS:", songs)  # 👈 Add this
    cursor.close()
    conn.close()
    return render_template('index.html', songs=songs)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        SELECT * FROM songs
        WHERE artist LIKE %s OR title LIKE %s OR genre LIKE %s
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    songs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', songs=songs, query=query)

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

@app.route('/add', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        artist = request.form['artist']
        title = request.form['title']
        song = request.form['song']
        label = request.form['label']
        podcast = request.form['podcast_played_on']
        genre = request.form['genre']
        bpm = request.form['bpm']
        song_key = request.form['song_key']

        # --- Spotify lookup ---
        album_art_url = None
        preview_url = None

        try:
            query = f"{artist} {title}"
            results = sp.search(q=query, type='track', limit=1)
            tracks = results.get('tracks', {}).get('items', [])
            if tracks:
                track = tracks[0]
                album_art_url = track['album']['images'][0]['url'] if track['album']['images'] else None
                preview_url = track['preview_url']
                if not genre and track['artists']:
                    # Try to fetch artist genres (optional)
                    artist_id = track['artists'][0]['id']
                    artist_info = sp.artist(artist_id)
                    if artist_info.get('genres'):
                        genre = artist_info['genres'][0]
        except Exception as e:
            print("Spotify lookup failed:", e)

        # --- Database insert ---
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO songs (artist, title, song, label, podcast_played_on, genre, bpm, song_key, album_art_url, preview_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (artist, title, song, label, podcast, genre, bpm, song_key, album_art_url, preview_url))
        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Song added successfully (Spotify data included)!", "success")
        return redirect(url_for('index'))

    return render_template('add.html')


@app.route("/random")
def random_song():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    cursor.close()
    conn.close()

    song = random.choice(songs) if songs else None
    return render_template("random.html", song=song)

@app.route('/delete/<int:song_id>')
def delete_song(song_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM songs WHERE id = %s", (song_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("🗑️ Song deleted!", "danger")
    return redirect(url_for('index'))


@app.route('/edit/<int:song_id>', methods=['GET', 'POST'])
def edit_song(song_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM songs WHERE id = %s", (song_id,))
    song = cursor.fetchone()

    if request.method == 'POST':
        data = {key: request.form[key] for key in request.form}
        cursor.execute("""
            UPDATE songs
            SET artist=%s, title=%s, song=%s, label=%s, podcast_played_on=%s, genre=%s,
                bpm=%s, song_key=%s, album_art_url=%s, preview_url=%s
            WHERE id=%s
        """, (data['artist'], data['title'], data['song'], data['label'], data['podcast_played_on'],
              data['genre'], data['bpm'], data['song_key'], data['album_art_url'], data['preview_url'], song_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("✅ Song updated successfully!", "success")
        return redirect(url_for('index'))

    cursor.close()
    conn.close()
    return render_template('edit.html', song=song)



# ==============================
# Run App
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
