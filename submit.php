<?php
include("db.php");
ini_set('display_errors', '1'); //don't show any errors
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Capture input
$note = isset($_POST['note']) ? $conn->real_escape_string($_POST['note']) : '';
$specialty = isset($_POST['specialty']) ? $conn->real_escape_string($_POST['specialty']) : 'general';

if (empty($note)) {
    die("<h3 class='text-danger'>No clinical note provided.</h3>");
}

// Call Flask API
$api_key = "abc123xyzsecure"; // Replace in production
$ch = curl_init('https://medical-ai-8hdt.onrender.com/analyze');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['note' => $note, 'specialty' => $specialty]));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-API-KEY: ' . $api_key
]);
$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);

// Handle errors
if (!is_array($result) || isset($result['error'])) {
    echo "<h3 class='text-danger'>AI Error:</h3><pre>";
    print_r($result);
    echo "</pre>";
    exit;
}

$full_response = isset($result['full_response']) ? $conn->real_escape_string($result['full_response']) : '';

// Optional: Extract name/age/gender from the note (fallback or hardcoded here)
$name = 'Unknown';
$age = 0;
$gender = 'Unknown';

// Insert patient
$conn->query("INSERT INTO patients (name, age, gender) VALUES ('$name', $age, '$gender')");
$patient_id = $conn->insert_id;

// Insert clinical input
$conn->query("INSERT INTO clinical_inputs (patient_id, symptoms, history, lab_results, created_at, note) 
              VALUES ($patient_id, '', '', '', NOW(), '$note')");
$clinical_input_id = $conn->insert_id;

// Insert full AI response
$full_response = $conn->real_escape_string($result['full_response'] ?? '');
$conn->query("INSERT INTO ai_responses 
(clinical_input_id, summary, full_response)
VALUES ($clinical_input_id, 'Full diagnostic breakdown from AI.', '$full_response')");
?>

<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>AI Diagnostic Summary</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-5">
  <h2>AI Diagnostic Result</h2>
  <p><strong>Date:</strong> <?= date("F j, Y, g:i a") ?></p>
  <p><strong>Specialty:</strong> <?= htmlspecialchars($specialty) ?></p>
  <hr>
  <h4>Clinical Note</h4>
  <p><?= nl2br(htmlspecialchars($note)) ?></p>

  <hr>
  <h3>AI Diagnostic Reasoning</h3>
<div class="border p-3 bg-light rounded">
    <pre><?= htmlspecialchars($result['full_response'] ?? 'No response received from AI.') ?></pre>
</div>


  <a href="index.php" class="btn btn-secondary mt-4">← Back</a>
</body>
</html>
