<?php
session_start();
ini_set('display_errors', '1'); //don't show any errors
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
include("db.php");

$dsn = "pgsql:host=$host;port=5432;dbname=$dbname;";
$pdo = new PDO($dsn, $user, $password, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$stmt = $pdo->prepare("
    INSERT INTO doctors (name, email, password_hash, specialty_slug)
    VALUES (:name, :email, :password_hash, :specialty_slug)
    RETURNING id
");

$stmt->execute([
    ':name'           => $_POST['name'] ?? '',
    ':email'          => $_POST['email'] ?? '',
    ':password_hash'  => password_hash($_POST['password'] ?? '', PASSWORD_BCRYPT),
    ':specialty_slug' => $_POST['specialty_slug'] ?? '',
]);

$id = $stmt->fetchColumn();
echo 'Inserted doctor id: ' . $id;
