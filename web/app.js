const editorInput = document.getElementById("editorInput");
const lineNumbers = document.getElementById("lineNumbers");
const lineCount = document.getElementById("lineCount");
const charCount = document.getElementById("charCount");
const clearEditorBtn = document.getElementById("clearEditorBtn");
const seedCodeBtn = document.getElementById("seedCodeBtn");
const clearChatBtn = document.getElementById("clearChatBtn");
const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");

const state = {
  sessionId: crypto.randomUUID(),
  conversation: [],
  pendingTypingNode: null,
};

const sampleEditorText = `function summarizeStudents(students) {
  return students
    .filter((student) => student.active)
    .map((student) => ({
      name: student.name,
      average: (student.math + student.history + student.science) / 3,
    }))
    .sort((a, b) => b.average - a.average);
}

const notes = [
  "Necesito explicar este codigo a un principiante.",
  "Tambien quiero detectar posibles mejoras.",
];`;

function updateEditorStats() {
  const value = editorInput.value;
  const lines = Math.max(1, value.split("\n").length);
  lineNumbers.textContent = Array.from({ length: lines }, (_, index) => String(index + 1)).join("\n");
  lineCount.textContent = `${lines} ${lines === 1 ? "linea" : "lineas"}`;
  charCount.textContent = `${value.length} caracteres`;
}

function syncScroll() {
  lineNumbers.scrollTop = editorInput.scrollTop;
}

function addMessage(role, content, extraClass = "") {
  const article = document.createElement("article");
  article.className = `message ${role} ${extraClass}`.trim();
  article.innerHTML = `
    <div class="message-role">${role === "assistant" ? "IA" : "Tu"}</div>
    <div class="message-bubble"></div>
  `;
  article.querySelector(".message-bubble").textContent = content;
  chatMessages.appendChild(article);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return article;
}

function appendMessageMeta(article, latencyMs, totalTokens, statusCode) {
  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.innerHTML = `
    <span>${latencyMs || 0} ms</span>
    <span>${totalTokens || 0} tokens</span>
    <span>status ${statusCode || "-"}</span>
  `;
  article.appendChild(meta);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTypingIndicator() {
  const article = document.createElement("article");
  article.className = "message assistant typing";
  article.innerHTML = `
    <div class="message-role">IA</div>
    <div class="message-bubble">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  `;
  chatMessages.appendChild(article);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  state.pendingTypingNode = article;
}

function removeTypingIndicator() {
  if (state.pendingTypingNode) {
    state.pendingTypingNode.remove();
    state.pendingTypingNode = null;
  }
}

async function sendChatMessage(message) {
  const trimmed = message.trim();
  if (!trimmed) {
    return;
  }

  addMessage("user", trimmed);
  state.conversation.push({ role: "user", content: trimmed });
  chatInput.value = "";
  sendBtn.disabled = true;
  addTypingIndicator();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sessionId: state.sessionId,
        message: trimmed,
        editorContent: editorInput.value,
        conversation: state.conversation,
      }),
    });

    const data = await response.json();
    removeTypingIndicator();

    if (!response.ok || !data.ok) {
      const errorText = data.answer || data.error || "Error desconocido";
      const errorMessage = addMessage("assistant", `No pude responder correctamente.\n\n${errorText}`);
      appendMessageMeta(errorMessage, data.latency_ms, data.total_tokens, data.status_code || response.status);
      return;
    }

    const assistantMessage = addMessage("assistant", data.answer || "Respuesta vacia.");
    appendMessageMeta(assistantMessage, data.latency_ms, data.total_tokens, data.status_code);
    state.conversation.push({ role: "assistant", content: data.answer || "" });
  } catch (error) {
    removeTypingIndicator();
    addMessage("assistant", `Error de red o servidor: ${error.message}`);
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

editorInput.addEventListener("input", updateEditorStats);
editorInput.addEventListener("scroll", syncScroll);
clearEditorBtn.addEventListener("click", () => {
  editorInput.value = "";
  updateEditorStats();
  editorInput.focus();
});
seedCodeBtn.addEventListener("click", () => {
  editorInput.value = sampleEditorText;
  updateEditorStats();
  editorInput.focus();
});
clearChatBtn.addEventListener("click", () => {
  state.sessionId = crypto.randomUUID();
  state.conversation = [];
  chatMessages.innerHTML = `
    <article class="message assistant">
      <div class="message-role">IA</div>
      <div class="message-bubble">Sesion reiniciada. Puedo ayudarte otra vez con el contenido del editor.</div>
    </article>
  `;
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await sendChatMessage(chatInput.value);
});

chatInput.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    await sendChatMessage(chatInput.value);
  }
});

window.addEventListener("load", async () => {
  updateEditorStats();
  editorInput.value = sampleEditorText;
  updateEditorStats();

  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    const statusNode = document.querySelector(".topbar-status");
    statusNode.textContent = data.ok ? `Conectado a ${data.model}` : "Backend no disponible";
  } catch {
    const statusNode = document.querySelector(".topbar-status");
    statusNode.textContent = "Backend no disponible";
  }
});
