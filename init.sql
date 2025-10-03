CREATE DATABASE IF NOT EXISTS musicdb;
USE musicdb;

CREATE TABLE IF NOT EXISTS songs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artist VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    song VARCHAR(255),
    label VARCHAR(255),
    podcast_played_on VARCHAR(255),
    genre VARCHAR(100),
    bpm INT,
    song_key VARCHAR(10)
);

CREATE USER IF NOT EXISTS 'musicuser'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON musicdb.* TO 'musicuser'@'localhost';
FLUSH PRIVILEGES;
