<?php
session_start();
include("db.php");

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = $_POST['email'];
    $pass  = $_POST['password'];

    $query = $conn->query("SELECT * FROM doctors WHERE email = '$email'");

    if ($query && $row = $query->fetch_assoc()) {
        if (password_verify($pass, $row['password_hash'])) {
            $_SESSION['doctor_id'] = $row['id'];
            $_SESSION['doctor_name'] = $row['name'];
            $_SESSION['specialty'] = $row['specialty_slug'];
            header("Location: dashboard.php");
            exit;
        }
    }

    $error = "Invalid credentials.";
}
?>
<html>
<head>
  <title>Doctor Registration</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container mt-5">
<form method="post">
    <div class="mb-3">
      <label for="name" class="form-label">Email</label>
  <input type="email" name="email" placeholder="Email" required>
</div>
<div class="mb-3">
      <label for="name" class="form-label">Name</label>
  <input type="password" name="password" placeholder="Password" required>
  </div>
  <button type="submit" class="btn btn-primary">Login</button>
</form>
<?php if (isset($error)) echo "<p style='color:red;'>$error</p>"; ?>
</html>
</body>