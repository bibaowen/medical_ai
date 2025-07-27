<?php include("auth.php"); ?>

<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Doctor Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-5">
  <h2 class="mb-4">👨‍⚕️ Welcome, Dr. <?= htmlspecialchars($_SESSION['doctor_name']) ?></h2>

  <div class="mb-4">
    <a href="index.php" class="btn btn-primary">Submit Clinical Note</a>
    <a href="analytics.php" class="btn btn-outline-info">View Analytics</a>
    <a href="logout.php" class="btn btn-danger">Logout</a>
  </div>

  <div class="card shadow-sm">
    <div class="card-body">
      <h5 class="card-title">Platform Overview</h5>
      <p class="card-text">Submit clinical notes, receive AI-assisted diagnoses, and view analytics for your practice. Stay up to date with your patient case history and recommendations.</p>
    </div>
  </div>
</div>
</body>
</html>
