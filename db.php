<?php
$host = "10.223.138.288";
$user = "autopjoo_practitioners";
$pass = "Biba2@portmore";
$db = "autopjoo_medical_ai";

/*$host = "localhost";
$user = "root";
$pass = "owen";
$db = "medical_ai";*/

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
