const BASE = "http://localhost:8000";

export async function streamChat({ messages, config, conversationId, onToken, onMeta }) {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, config, conversation_id: conversationId }),
  });

  if (!res.ok) throw new Error(`Server error ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    for (const line of chunk.split("\n")) {
      if (!line.startsWith("data: ")) continue;
      const raw = line.slice(6).trim();
      if (raw === "[DONE]") continue;
      try {
        const parsed = JSON.parse(raw);
        if (parsed.content !== undefined) onToken(parsed.content);
        if (parsed.meta) onMeta(parsed.meta);
      } catch (_) {}
    }
  }
}

export async function fetchConversations(limit = 15, offset = 0) {
  const res = await fetch(`${BASE}/conversations?limit=${limit}&offset=${offset}`);
  return res.json();
}

export async function fetchMessages(cid) {
  const res = await fetch(`${BASE}/conversations/${cid}/messages`);
  return res.json();
}
