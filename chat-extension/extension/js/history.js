import { fetchConversations, fetchMessages } from "./api.js";

const PAGE = 15;

export function initHistory({ onSelect, onNew }) {
  const panel     = document.getElementById("history-panel");
  const chatView  = document.getElementById("chat-view");
  const menuBtn   = document.getElementById("menu-btn");
  const newBtn    = document.getElementById("new-chat-btn");
  const list      = document.getElementById("history-list");
  const moreBtn   = document.getElementById("show-more-btn");

  let offset = 0;
  let busy   = false;

  function open() {
    offset = 0;
    list.innerHTML = "";
    panel.classList.remove("hidden");
    chatView.classList.add("hidden");
    load();
  }

  function close() {
    panel.classList.add("hidden");
    chatView.classList.remove("hidden");
  }

  async function load() {
    if (busy) return;
    busy = true;
    moreBtn.classList.add("hidden");

    const convs = await fetchConversations(PAGE, offset);
    offset += convs.length;

    for (const conv of convs) {
      const btn = document.createElement("button");
      btn.className = "history-item";
      btn.innerHTML = `
        <span class="hi-title">${esc(conv.title)}</span>
        <span class="hi-time">${ago(conv.updated_at)}</span>
      `;
      btn.addEventListener("click", async () => {
        close();
        const msgs = await fetchMessages(conv.id);
        onSelect(conv.id, msgs);
      });
      list.appendChild(btn);
    }

    if (convs.length === PAGE) moreBtn.classList.remove("hidden");
    busy = false;
  }

  menuBtn.addEventListener("click", open);
  newBtn.addEventListener("click",  () => { close(); onNew(); });
  moreBtn.addEventListener("click", load);
}

function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function ago(ts) {
  const s = Date.now() / 1000 - ts;
  if (s < 60)     return "just now";
  if (s < 3600)   return `${Math.floor(s / 60)}m ago`;
  if (s < 86400)  return `${Math.floor(s / 3600)}h ago`;
  if (s < 604800) return `${Math.floor(s / 86400)}d ago`;
  return new Date(ts * 1000).toLocaleDateString();
}
