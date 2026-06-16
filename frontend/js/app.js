const chatBox = document.getElementById("chatBox");
const queryInput = document.getElementById("queryInput");
const sendBtn = document.getElementById("sendBtn");
const welcomeSection = document.getElementById("welcomeSection");
const exampleCards = document.querySelectorAll(".example-card");

let loadingMessageElement = null;

function hideWelcome() {
  if (welcomeSection) {
    welcomeSection.style.display = "none";
  }
}

function scrollToBottom() {
  chatBox.scrollTop = chatBox.scrollHeight;
}

function addMessage(sender, text) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", sender);

  messageDiv.textContent = text;

  chatBox.appendChild(messageDiv);
  scrollToBottom();
}

function showLoading() {
  loadingMessageElement = document.createElement("div");
  loadingMessageElement.classList.add("message", "bot", "loading");
  loadingMessageElement.textContent = "Thinking...";
  chatBox.appendChild(loadingMessageElement);
  scrollToBottom();
}

function removeLoading() {
  if (loadingMessageElement) {
    loadingMessageElement.remove();
    loadingMessageElement = null;
  }
}

async function sendMessage() {
  const query = queryInput.value.trim();

  if (!query) return;

  hideWelcome();
  addMessage("user", query);

  queryInput.value = "";
  queryInput.focus();

  showLoading();

  try {
    const response = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query: query
      })
    });

    const data = await response.json();

    removeLoading();
    addMessage("bot", data.answer || "No answer received.");
  } catch (error) {
    removeLoading();
    addMessage("bot", "Unable to connect to server.");
  }
}

sendBtn.addEventListener("click", sendMessage);

queryInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});

exampleCards.forEach((card) => {
  card.addEventListener("click", () => {
    queryInput.value = card.dataset.question;
    queryInput.focus();
  });
});