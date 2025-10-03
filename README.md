🎵 MusicDB Project



A simple Music Database project for storing and searching track metadata.
Includes a terminal app and a Flask web app, with support for batch import/export.

⚡ Tech Stack

Language: Python 3.10+

Framework: Flask (Web App)

Database: MySQL (with MySQL Connector)

Frontend: HTML (Jinja2 templates)

Tools: Git, Virtualenv, Tabulate, CSV

📖 Features

Add, search, update, delete songs

Batch import/export via TXT/CSV

Random song picker

Full CRUD from terminal or web app

Handles duplicates automatically on import

🗄️ Database Schema

Table: songs

Column	Type	Description
id	INT (PK)	Auto-increment unique ID
artist	VARCHAR	Artist name
title	VARCHAR	Album / collection title
song	VARCHAR	Song name
label	VARCHAR	Record label
podcast_played_on	VARCHAR	Podcast / platform played on
genre	VARCHAR	Song genre (e.g. House, Rock)
bpm	INT	Beats per minute (e.g. 128)
song_key	VARCHAR	Musical key (e.g. Am, C#, F)