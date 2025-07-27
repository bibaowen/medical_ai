<?php
$host = "dpg-d22i0nidbo4c73f94l8g-a.oregon-postgres.render.com";
$port = "5432";
$dbname = "medical_db_p50s";
$user = "owen";
$password = "PYpI59sLWRCoXxogLpf4lh5nEhtXehRn";

$conn = pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");

if (!$conn) {
    die("Connection failed: " . pg_last_error());
}

