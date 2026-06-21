// =========================================================
// Dashboard live updates via SSE.
// Renders the verdict overlay + status panel in real time.
// =========================================================

const overlay = document.getElementById("verdict-overlay");
const verdictText = document.getElementById("verdict-text");
const verdictMeta = document.getElementById("verdict-meta");
const doorStatus  = document.getElementById("door-status");
const lastUser    = document.getElementById("last-user");
const lastScore   = document.getElementById("last-score");
const mlStatus    = document.getElementById("ml-status");
const servoState  = document.getElementById("servo-state");

function applyVerdict(data) {
  // Reset class
  overlay.className = "verdict-overlay " + data.verdict;

  switch (data.verdict) {
    case "granted":
      verdictText.textContent = "Access granted: " + data.name;
      verdictMeta.textContent =
        `${data.access_type} · score ${data.score.toFixed(3)}`;
      doorStatus.textContent = "Open";
      doorStatus.style.color = "#2e7d32";
      servoState.textContent = "Triggered (open)";
      break;
    case "denied":
      verdictText.textContent = "Access denied: " + data.name;
      verdictMeta.textContent = `score ${data.score.toFixed(3)}`;
      doorStatus.textContent = "Locked";
      doorStatus.style.color = "#c62828";
      servoState.textContent = "Idle";
      break;
    case "scanning":
      verdictText.textContent = "Scanning...";
      verdictMeta.textContent = "";
      break;
    case "idle":
      verdictText.textContent = "Waiting for face...";
      verdictMeta.textContent = "";
      doorStatus.textContent = "Locked";
      doorStatus.style.color = "#757575";
      servoState.textContent = "Idle";
      break;
    case "error":
      verdictText.textContent = "System error";
      verdictMeta.textContent = data.name || "";
      doorStatus.textContent = "—";
      servoState.textContent = "—";
      break;
  }

  if (data.name && data.verdict !== "idle" && data.verdict !== "error") {
    lastUser.textContent = data.name;
    lastScore.textContent = data.score.toFixed(3);
  }
}

function connectSSE() {
  const es = new EventSource("/status/events");

  es.addEventListener("verdict", (e) => {
    try {
      applyVerdict(JSON.parse(e.data));
    } catch (err) {
      console.warn("Bad SSE payload:", err);
    }
  });

  es.addEventListener("ping", () => {
    // Heartbeat — no UI update needed.
  });

  es.onerror = () => {
    console.warn("SSE disconnected, retrying in 3s...");
    es.close();
    setTimeout(connectSSE, 3000);
  };
}

// ML health — poll every 10s (cheap endpoint, no SSE).
async function pollHealth() {
  try {
    const r = await fetch("/status/snapshot");
    const data = await r.json();
    mlStatus.textContent = data.ml_healthy ? "Online" : "Offline";
    mlStatus.style.color = data.ml_healthy ? "#2e7d32" : "#c62828";
    // Initial paint
    applyVerdict(data);
  } catch (e) {
    mlStatus.textContent = "Unknown";
  }
}

connectSSE();
pollHealth();
setInterval(pollHealth, 10000);
