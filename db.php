<?php
$host = getenv('DB_HOST') ?: 'dpg-d22i0nidbo4c73f94l8g-a.oregon-postgres.render.com';
$port = getenv('DB_PORT') ?: '5432';
$dbname = getenv('DB_NAME');
$user = getenv('DB_USER');
$password = getenv('DB_PASS');

$conn = pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");

if (!$conn) {
    die("❌ Database connection failed: " . pg_last_error());
}
