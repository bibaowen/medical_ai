<?php
include("auth.php"); // Ensures user is logged in
include("db.php");

// Fetch doctor name and specialty from session
$doctor_name = $_SESSION['doctor_name'] ?? 'Doctor';
$specialty = $_SESSION['specialty'] ?? 'general';
?>

<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Submit Clinical Note</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    #dictation-status {
      font-style: italic;
      color: #6c757d;
    }
    #mic-indicator {
  font-weight: bold;
  margin-left: 10px;
}
  </style>
</head>
<body class="container mt-5">

  <h2>Hello, <?= htmlspecialchars($doctor_name) ?></h2>
  <p class="text-muted">Specialty: <strong><?= htmlspecialchars($specialty) ?></strong></p>

  <form action="submit.php" method="POST">
    <input type="hidden" name="specialty" value="<?= htmlspecialchars($specialty) ?>">

  <div class="mb-3">
  <label for="note" class="form-label">Clinical Note</label>
  <textarea class="form-control" id="note" name="note" rows="6" placeholder="You may type or use dictation below..."></textarea>
</div>

<!-- <button id="mic-btn" type="button" class="btn btn-primary">
  🎤 Start Dictation <span id="mic-indicator" style="display:none;">🔴</span>
</button> -->
<button id="mic-btn" type="button" class="btn btn-primary">🎤 Start Dictation</button>
<button id="stop-mic-btn" type="button" class="btn btn-danger">🛑 Stop Dictation</button>
<small id="mic-indicator" class="text-success" style="display: none;">🎙️ Listening...</small>


<p id="status" class="mt-2 text-muted"></p>


    <button type="submit" class="btn btn-primary" title="">Ask Dr. RIQ</button>
  </form>

  <script>
  const micBtn = document.getElementById("mic-btn");
  const stopMicBtn = document.getElementById("stop-mic-btn");
  const micIndicator = document.getElementById("mic-indicator");
  const textarea = document.querySelector('textarea[name="note"]');

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  let isListening = false;

  micBtn.addEventListener("click", function () {
    if (!isListening) {
      recognition.start();
      isListening = true;
      micIndicator.style.display = "inline";
      micBtn.disabled = true;
      stopMicBtn.disabled = false;
      micBtn.innerHTML = "🎤 Listening...";
    }
  });

  stopMicBtn.addEventListener("click", function () {
    recognition.stop();
    isListening = false;
    micIndicator.style.display = "none";
    micBtn.innerHTML = "🎤 Start Dictation";
    micBtn.disabled = false;
    stopMicBtn.disabled = true;
  });

  recognition.onresult = function (event) {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        textarea.value += event.results[i][0].transcript + " ";
      } else {
        interim += event.results[i][0].transcript;
      }
    }
  };

  recognition.onend = function () {
    micIndicator.style.display = "none";
    micBtn.innerHTML = "🎤 Start Dictation";
    micBtn.disabled = false;

    if (isListening) {
      // restart recognition automatically unless user stopped it
      recognition.start();
    }
  };

  recognition.onerror = function (event) {
    console.error("Speech recognition error:", event.error);
    recognition.stop();
    isListening = false;
    micBtn.disabled = false;
    micBtn.innerHTML = "🎤 Start Dictation";
    micIndicator.style.display = "none";
  };
</script>

  </body>
  </html>