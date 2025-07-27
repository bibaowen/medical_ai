<?php
include("auth.php"); // ensure doctor is logged in
include("db.php");

// Fetch basic stats
$totals = $conn->query("SELECT 
    (SELECT COUNT(*) FROM patients) AS total_patients,
    (SELECT COUNT(*) FROM ai_responses) AS total_responses,
    (SELECT COUNT(*) FROM clinical_inputs) AS total_inputs
")->fetch_assoc();

// Daily case count for chart
$chart_data = [];
$res = $conn->query("
    SELECT DATE(created_at) as day, COUNT(*) as count
    FROM clinical_inputs
    GROUP BY day ORDER BY day DESC LIMIT 7
");

while ($row = $res->fetch_assoc()) {
    $chart_data[] = [
        'day' => $row['day'],
        'count' => $row['count']
    ];
}

$chart_data = array_reverse($chart_data); // show oldest first
?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Analytics Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-light">
<div class="container py-5">
    <h2 class="mb-4">📊 AI Diagnostic Platform – Analytics</h2>

    <div class="row text-center mb-4">
        <div class="col-md-4">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h5>Total Patients</h5>
                    <h2 class="text-primary"><?= $totals['total_patients'] ?></h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h5>Clinical Inputs</h5>
                    <h2 class="text-success"><?= $totals['total_inputs'] ?></h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h5>AI Responses</h5>
                    <h2 class="text-warning"><?= $totals['total_responses'] ?></h2>
                </div>
            </div>
        </div>
    </div>

    <h4>📅 Submissions (Past 7 Days)</h4>
    <canvas id="casesChart" height="100"></canvas>
</div>

<script>
    const ctx = document.getElementById('casesChart').getContext('2d');
    const casesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: <?= json_encode(array_column($chart_data, 'day')) ?>,
            datasets: [{
                label: 'Cases Submitted',
                data: <?= json_encode(array_column($chart_data, 'count')) ?>,
                fill: true,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    precision: 0
                }
            }
        }
    });
</script>
</body>
</html>
