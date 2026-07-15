// Live dashboard: SSE-driven verdict overlay + periodic health snapshot.
// Safe to load on any page — if the elements aren't present, it no-ops.

const overlay = document.getElementById("verdict-overlay");
const verdictText = document.getElementById("verdict-text");
const verdictMeta = document.getElementById("verdict-meta");
const doorStatus = document.getElementById("door-status");
const lastUser = document.getElementById("last-user");
const lastScore = document.getElementById("last-score");
const mlStatus = document.getElementById("ml-status");
const servoState = document.getElementById("servo-state");

function applyVerdict(data) {
  if (!data || !overlay) return;

  overlay.className = "verdict-overlay " + data.verdict;

  switch (data.verdict) {
    case "granted":
      verdictText.textContent = "Access granted: " + (data.name || "User");
      verdictMeta.textContent = `${data.access_type || ""} · score ${(data.score || 0).toFixed(3)}`;
      if (doorStatus) { doorStatus.textContent = "Open"; doorStatus.style.color = "#2e7d32"; }
      if (servoState) servoState.textContent = "Triggered";
      break;
    case "denied":
      verdictText.textContent = "Access denied";
      verdictMeta.textContent = `score ${(data.score || 0).toFixed(3)}`;
      if (doorStatus) { doorStatus.textContent = "Locked"; doorStatus.style.color = "#c62828"; }
      if (servoState) servoState.textContent = "Idle";
      break;
    case "idle":
      verdictText.textContent = "Waiting for face...";
      verdictMeta.textContent = "";
      if (doorStatus) { doorStatus.textContent = "Locked"; doorStatus.style.color = "#6b7280"; }
      if (servoState) servoState.textContent = "Idle";
      break;
    case "liveness_check":
      verdictText.textContent = "Liveness check: please blink";
      verdictMeta.textContent = `name ${data.name || ""} · score ${(data.score || 0).toFixed(3)}`;
      if (doorStatus) { doorStatus.textContent = "Locked"; doorStatus.style.color = "#f9a825"; }
      if (servoState) servoState.textContent = "Idle";
      break;
    case "error":
      verdictText.textContent = "System error";
      verdictMeta.textContent = data.name || "";
      if (doorStatus) doorStatus.textContent = "—";
      if (servoState) servoState.textContent = "—";
      break;
    default:
      verdictText.textContent = data.verdict;
  }

  if (data.name && data.verdict !== "idle" && data.verdict !== "error") {
    if (lastUser) lastUser.textContent = data.name;
    if (lastScore) lastScore.textContent = (data.score || 0).toFixed(3);
  }
}

function connectSSE() {
  const es = new EventSource("/status/events");
  es.addEventListener("verdict", (e) => {
    try {
      applyVerdict(JSON.parse(e.data));
    } catch (err) {
      console.error("Bad SSE payload:", err);
    }
  });
  es.onerror = () => {
    es.close();
    setTimeout(connectSSE, 3000);
  };
}

async function pollHealth() {
  if (!mlStatus) return;
  try {
    const r = await fetch("/status/snapshot");
    const data = await r.json();
    mlStatus.textContent = data.ml_healthy ? "Online" : "Offline";
    mlStatus.style.color = data.ml_healthy ? "#2e7d32" : "#c62828";
    applyVerdict(data);
  } catch (e) {
    mlStatus.textContent = "Unknown";
    mlStatus.style.color = "#6b7280";
  }
}

if (overlay) {
  connectSSE();
  pollHealth();
  setInterval(pollHealth, 10000);
}
