import mysql.connector
from tabulate import tabulate
import csv
import random

# Connect to database
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="musicuser",
        password="your_password",
        database="musicdb"
    )

# Insert new record
def insert_record():
    artist = input("Artist: ")
    title = input("Title: ")
    song = input("Song: ")
    label = input("Label: ")
    podcast_played_on = input("Podcast played on: ")
    genre = input("Genre: ")
    bpm = input("BPM (number): ")
    song_key = input("Key: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO songs (artist, title, song, label, podcast_played_on, genre, bpm, song_key)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (artist, title, song, label, podcast_played_on, genre, bpm or None, song_key))
    conn.commit()
    conn.close()
    print("✅ Record inserted.")

# List all records
def list_records():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM songs")
    rows = cur.fetchall()
    conn.close()

    headers = ["ID", "Artist", "Title", "Song", "Label", "Podcast", "Genre", "BPM", "Key"]
    print(tabulate(rows, headers=headers, tablefmt="grid"))

# Search records
def search_records():
    keyword = input("Enter search keyword: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM songs
        WHERE artist LIKE %s OR title LIKE %s OR song LIKE %s OR label LIKE %s 
              OR podcast_played_on LIKE %s OR genre LIKE %s OR song_key LIKE %s
    """, [f"%{keyword}%"] * 7)
    rows = cur.fetchall()
    conn.close()
    headers = ["ID", "Artist", "Title", "Song", "Label", "Podcast", "Genre", "BPM", "Key"]
    print(tabulate(rows, headers=headers, tablefmt="grid"))

# Update a record
def update_record():
    record_id = input("Enter record ID to update: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM songs WHERE id=%s", (record_id,))
    row = cur.fetchone()
    if not row:
        print("❌ Record not found.")
        return

    fields = ["artist", "title", "song", "label", "podcast_played_on", "genre", "bpm", "song_key"]
    updates = []
    values = []
    for i, field in enumerate(fields, 1):
        new_val = input(f"{field.capitalize()} ({row[i]}): ")
        if new_val:
            updates.append(f"{field}=%s")
            values.append(new_val)
    values.append(record_id)

    if updates:
        cur.execute(f"UPDATE songs SET {', '.join(updates)} WHERE id=%s", values)
        conn.commit()
        print("✅ Record updated.")
    conn.close()

# Delete record
def delete_record():
    record_id = input("Enter record ID to delete: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM songs WHERE id=%s", (record_id,))
    conn.commit()
    conn.close()
    print("✅ Record deleted.")

# Random record
def random_record():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM songs")
    rows = cur.fetchall()
    conn.close()
    if rows:
        row = random.choice(rows)
        headers = ["ID", "Artist", "Title", "Song", "Label", "Podcast", "Genre", "BPM", "Key"]
        print(tabulate([row], headers=headers, tablefmt="grid"))
    else:
        print("❌ No records found.")

# Export to TXT
def export_records():
    filename = input("Enter filename to export (e.g., export.txt): ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT artist, title, song, label, podcast_played_on, genre, bpm, song_key FROM songs")
    rows = cur.fetchall()
    conn.close()

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["artist", "title", "song", "label", "podcast_played_on", "genre", "bpm", "song_key"])
        writer.writerows(rows)
    print(f"✅ Records exported to {filename}")

# Import from TXT
def import_records():
    filename = input("Enter filename to import: ")
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    conn = get_connection()
    cur = conn.cursor()
    for row in rows:
        cur.execute("""
            SELECT * FROM songs WHERE artist=%s AND title=%s AND song=%s
        """, (row["artist"], row["title"], row["song"]))
        if cur.fetchone():
            print(f"⚠️ Duplicate skipped: {row}")
            continue

        cur.execute("""
            INSERT INTO songs (artist, title, song, label, podcast_played_on, genre, bpm, song_key)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (row["artist"], row["title"], row["song"], row["label"], row["podcast_played_on"],
              row["genre"], row["bpm"] or None, row["song_key"]))
    conn.commit()
    conn.close()
    print("✅ Import complete.")

# Menu
def main():
    while True:
        print("""
1. Insert new record
2. Search records
3. List all records
4. Random record
5. Update record
6. Delete record
7. Export all records to TXT
8. Import records from TXT
9. Quit
""")
        choice = input("Choose option: ")
        if choice == "1":
            insert_record()
        elif choice == "2":
            search_records()
        elif choice == "3":
            list_records()
        elif choice == "4":
            random_record()
        elif choice == "5":
            update_record()
        elif choice == "6":
            delete_record()
        elif choice == "7":
            export_records()
        elif choice == "8":
            import_records()
        elif choice == "9":
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
