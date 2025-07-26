<?php
$host = "dpg-d22i0nidbo4c73f94l8g-a.oregon-postgres.render.com";
$user = "owen";
$pass = "PYpI59sLWRCoXxogLpf4lh5nEhtXehRn";
$db = "medical_db_p50s";

/*$host = "localhost";
$user = "root";
$pass = "owen";
$db = "medical_ai";*/

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
