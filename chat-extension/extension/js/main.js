import { streamChat } from "./api.js";
import { initHistory } from "./history.js";

const messagesEl = document.getElementById("messages");
const inputEl    = document.getElementById("input");
const sendBtn    = document.getElementById("send-btn");
const clearBtn   = document.getElementById("clear-btn");

let messages       = [];
let conversationId = null;
let streaming      = false;
const config = { mock: true, humanize: false, developer: false };

// ── Toggles ──────────────────────────────────────────────────────────────────
document.querySelectorAll(".toggle").forEach((btn) => {
  btn.addEventListener("click", () => {
    const key = btn.dataset.key;
    config[key] = !config[key];
    btn.classList.toggle("active", config[key]);
  });
});

// ── History ───────────────────────────────────────────────────────────────────
initHistory({
  onSelect(id, msgs) {
    conversationId = id;
    messages = msgs.map((m) => ({ role: m.role, content: m.content }));
    messagesEl.innerHTML = "";
    msgs.forEach((m) => addMessage(m.role, m.content));
  },
  onNew() { reset(); },
});

clearBtn.addEventListener("click", reset);

function reset() {
  conversationId = null;
  messages = [];
  messagesEl.innerHTML = "";
}

// ── Messages ──────────────────────────────────────────────────────────────────
function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  scroll();
  return div;
}

function showError(msg) {
  const div = document.createElement("div");
  div.className = "error";
  div.textContent = msg;
  messagesEl.appendChild(div);
  scroll();
}

function scroll() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// ── Send ──────────────────────────────────────────────────────────────────────
async function send() {
  const text = inputEl.value.trim();
  if (!text || streaming) return;

  inputEl.value = "";
  inputEl.style.height = "auto";
  streaming = true;
  sendBtn.disabled = true;

  messages.push({ role: "user", content: text });
  addMessage("user", text);

  const aDiv = addMessage("assistant", "");
  aDiv.classList.add("streaming");
  let accumulated = "";

  try {
    await streamChat({
      messages,
      config,
      conversationId,
      onToken(t) {
        accumulated += t;
        aDiv.textContent = accumulated;
        scroll();
      },
      onMeta(meta) {
        conversationId = meta.conversation_id;
      },
    });
    messages.push({ role: "assistant", content: accumulated });
  } catch (err) {
    aDiv.remove();
    messages.pop();
    showError(err.message || "Something went wrong. Is the server running?");
  } finally {
    aDiv.classList.remove("streaming");
    streaming = false;
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

sendBtn.addEventListener("click", send);

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
});

inputEl.addEventListener("input", () => {
  inputEl.style.height = "auto";
  inputEl.style.height = inputEl.scrollHeight + "px";
});
