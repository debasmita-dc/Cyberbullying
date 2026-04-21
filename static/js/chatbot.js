(function () {
  const chatbox = document.getElementById("chatbox");
  const input = document.getElementById("chatInput");
  const btn = document.getElementById("chatSendBtn");

  function addMsg(role, text) {
    const wrap = document.createElement("div");
    wrap.style.margin = "8px 0";
    wrap.style.whiteSpace = "pre-wrap";

    const tag = document.createElement("div");
    tag.style.fontSize = "12px";
    tag.style.opacity = "0.7";
    tag.textContent = role === "user" ? "You" : "Bot";

    const body = document.createElement("div");
    body.textContent = text;

    wrap.appendChild(tag);
    wrap.appendChild(body);
    chatbox.appendChild(wrap);
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  async function send() {
    const msg = (input.value || "").trim();
    if (!msg) return;

    input.value = "";
    addMsg("user", msg);
    addMsg("bot", "…");

    // remove last "…" later by editing last node
    const lastBot = chatbox.lastChild;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
      });

      const data = await res.json();
      const reply = (data && data.reply) ? data.reply : "No reply received.";

      // replace "…" with real reply
      lastBot.querySelector("div:last-child").textContent = reply;
    } catch (e) {
      lastBot.querySelector("div:last-child").textContent =
        "Chat error. Check server logs / API key.";
    }
  }

  btn.addEventListener("click", send);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") send();
  });
})();