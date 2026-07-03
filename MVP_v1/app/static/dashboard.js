const overlay = document.getElementById("verdict-overlay");
const verdictText = document.getElementById("verdict-text");
const verdictMeta = document.getElementById("verdict-meta");
const doorStatus  = document.getElementById("door-status");
const lastUser    = document.getElementById("last-user");
const lastScore   = document.getElementById("last-score");
const mlStatus    = document.getElementById("ml-status");
const servoState  = document.getElementById("servo-state");

function applyVerdict(data) {
  if (!data || !overlay) return;

  // Обновляем класс для цвета
  overlay.className = "verdict-overlay " + data.verdict;

  // Логика текста
  switch (data.verdict) {
    case "granted":
      verdictText.textContent = "Access granted: " + (data.name || "User");
      verdictMeta.textContent = `${data.access_type || ''} · score ${(data.score || 0).toFixed(3)}`;
      if(doorStatus) { doorStatus.textContent = "Open"; doorStatus.style.color = "#2e7d32"; }
      if(servoState) servoState.textContent = "Triggered";
      break;
    case "denied":
      verdictText.textContent = "Access denied";
      verdictMeta.textContent = `score ${(data.score || 0).toFixed(3)}`;
      if(doorStatus) { doorStatus.textContent = "Locked"; doorStatus.style.color = "#c62828"; }
      if(servoState) servoState.textContent = "Idle";
      break;
    case "idle":
      verdictText.textContent = "Waiting for face...";
      verdictMeta.textContent = "";
      if(doorStatus) { doorStatus.textContent = "Locked"; doorStatus.style.color = "#757575"; }
      if(servoState) servoState.textContent = "Idle";
      break;
    case "error":
      verdictText.textContent = "System error";
      verdictMeta.textContent = data.name || "";
      if(doorStatus) doorStatus.textContent = "—";
      if(servoState) servoState.textContent = "—";
      break;
    default:
      // Для статусов scanning или других
      verdictText.textContent = data.verdict;
  }

  // Обновляем инфо о последнем юзере
  if (data.name && data.verdict !== "idle" && data.verdict !== "error") {
    if(lastUser) lastUser.textContent = data.name;
    if(lastScore) lastScore.textContent = (data.score || 0).toFixed(3);
  }
}

function connectSSE() {
  const es = new EventSource("/status/events");
  es.addEventListener("verdict", (e) => {
    try {
      const data = JSON.parse(e.data);
      console.log("SSE Verdict:", data); // <-- Смотри сюда в консоли!
      applyVerdict(data);
    } catch (err) {
      console.error("SSE Error:", err);
    }
  });
  
  es.onerror = () => {
    console.warn("SSE disconnected");
    es.close();
    setTimeout(connectSSE, 3000);
  };
}

async function pollHealth() {
  try {
    const r = await fetch("/status/snapshot");
    const data = await r.json();
    console.log("Health Snapshot:", data); // <-- И сюда!
    
    if (mlStatus) {
      mlStatus.textContent = data.ml_healthy ? "Online" : "Offline";
      mlStatus.style.color = data.ml_healthy ? "#2e7d32" : "#c62828";
    }
  } catch (e) {
    if (mlStatus) {
      mlStatus.textContent = "Unknown";
      mlStatus.style.color = "#757575";
    }
  }
}

connectSSE();
pollHealth();
setInterval(pollHealth, 10000);