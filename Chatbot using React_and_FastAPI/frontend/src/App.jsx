import React, { useCallback, useEffect, useRef, useState } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const API_URL = import.meta?.env?.VITE_API_URL || "http://127.0.0.1:8000";
  const chatEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // --- Minimal markdown renderer (headings, lists, code, hr, paragraphs, bold/italics, tables) ---
  const escapeHtml = (s) => (s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");

  const inlineFormat = (s) => {
    // bold **text** and italic *text*
    let out = s;
    out = out.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    out = out.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, "<em>$1</em>");
    return out;
  };

  const renderMarkdown = (text) => {
    if (!text) return "";
    // Handle code blocks
    const parts = (text + "\n").split(/```/);
    for (let i = 0; i < parts.length; i += 2) {
      parts[i] = renderBlocks(parts[i]);
      if (i + 1 < parts.length) {
        parts[i + 1] = `<pre><code>${escapeHtml(parts[i + 1].replace(/\n$/, ""))}</code></pre>`;
      }
    }
    return parts.join("");
  };

  const renderBlocks = (raw) => {
    const lines = raw.replace(/\r/g, "").split("\n");
    const html = [];
    let inList = false;
    let inOl = false;
    let tableRows = [];

    const flushList = () => {
      if (inList) { html.push("</ul>"); inList = false; }
      if (inOl) { html.push("</ol>"); inOl = false; }
    };
    const flushTable = () => {
      if (tableRows.length > 0) {
        const rows = tableRows.map((r, idx) => {
          const cells = r.split("|").map(c => c.trim()).filter(Boolean);
          const tag = idx === 0 ? "th" : "td";
          return `<tr>${cells.map(c => `<${tag}>${inlineFormat(escapeHtml(c))}</${tag}>`).join("")}</tr>`;
        }).join("");
        html.push(`<table>${rows}</table>`);
        tableRows = [];
      }
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!line.trim()) { flushList(); flushTable(); continue; }

      // Tables: collect contiguous lines with |
      if (line.includes("|") && /\S\|\S/.test(line)) {
        tableRows.push(line);
        continue;
      } else {
        flushTable();
      }

      const mH = line.match(/^(#{1,6})\s+(.*)$/);
      if (mH) {
        flushList();
        const level = mH[1].length;
        html.push(`<h${level}>${inlineFormat(escapeHtml(mH[2]))}</h${level}>`);
        continue;
      }

      const mHr = line.match(/^(-{3,}|\*{3,}|_{3,})$/);
      if (mHr) { flushList(); html.push("<hr/>"); continue; }

      const mUl = line.match(/^\s*[-*]\s+(.+)$/);
      if (mUl) {
        if (!inList) { flushList(); html.push("<ul>"); inList = true; }
        html.push(`<li>${inlineFormat(escapeHtml(mUl[1]))}</li>`);
        continue;
      }

      const mOl = line.match(/^\s*\d+\.\s+(.+)$/);
      if (mOl) {
        if (!inOl) { flushList(); html.push("<ol>"); inOl = true; }
        html.push(`<li>${inlineFormat(escapeHtml(mOl[1]))}</li>`);
        continue;
      }

      // Paragraph
      flushList();
      html.push(`<p>${inlineFormat(escapeHtml(line))}</p>`);
    }

    flushList();
    flushTable();
    return html.join("");
  };

  const typeOutText = useCallback(async (fullText) => {
    const tokens = fullText.split(/(\s+)/); // keep spaces
    for (let i = 0; i < tokens.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 15));
      setMessages((prev) => {
        if (prev.length === 0) return prev;
        const next = [...prev];
        const lastIdx = next.length - 1;
        if (next[lastIdx]?.sender !== "Bot") return prev;
        next[lastIdx] = { ...next[lastIdx], text: (next[lastIdx].text || "") + tokens[i] };
        return next;
      });
    }
  }, []);

  const sendMessage = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isSending || isTyping) return;

    const userMessage = { sender: "You", text: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsSending(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });
      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
      }
      const data = await res.json();
      const replyText = data?.reply ?? "No reply";

      // Insert empty bot message, then type it out
      setIsTyping(true);
      setMessages((prev) => [...prev, { sender: "Bot", text: "" }]);
      await typeOutText(replyText);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "Bot", text: "Error connecting to server" },
      ]);
    } finally {
      setIsTyping(false);
      setIsSending(false);
    }

  }, [API_URL, input, isSending, isTyping, typeOutText]);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
      }
    },
    [sendMessage]
  );

  const hasMessages = messages.length > 0;

  return (
    <div className="chat-container">
      <header className="chat-header" role="banner">
        <h1 className="chat-title">Custom Support Chatbot</h1>
      </header>

      {hasMessages ? (
        <>
          <main className="chat-main" aria-live="polite" aria-label="Chat messages">
            {messages.map((msg, i) => (
              <section
                key={i}
                className={msg.sender === "You" ? "message message--user" : "message message--bot"}
              >
                <div className="message__meta">{msg.sender}</div>
                {msg.sender === "Bot" ? (
                  <div className="message__text" dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.text) }} />
                ) : (
                  <div className="message__text">{msg.text}</div>
                )}
              </section>
            ))}
            <div ref={chatEndRef} />
          </main>

          <form className="chat-input" onSubmit={(e) => { e.preventDefault(); sendMessage(); }}>
            <input
              className="chat-input__field"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              aria-label="Message input"
              autoFocus
            />
            <button
              className="chat-input__button"
              onClick={sendMessage}
              disabled={isSending || isTyping || !input.trim()}
              aria-busy={isSending || isTyping}
              aria-label="Send message"
              type="submit"
            >
              {isSending ? "Sending..." : isTyping ? "Typing..." : "Send"}
            </button>
          </form>
        </>
      ) : (
        <section className="empty" aria-label="Welcome">
          <div className="empty__inner">
            <h2 className="empty__title">Good to see you</h2>
            <p className="empty__subtitle">How can I help you today?</p>
            <form className="empty__form" onSubmit={(e) => { e.preventDefault(); sendMessage(); }}>
              <input
                className="chat-input__field"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask your question here."
                aria-label="Message input"
                autoFocus
              />
              <button
                className="chat-input__button"
                onClick={sendMessage}
                disabled={isSending || isTyping || !input.trim()}
                aria-busy={isSending || isTyping}
                aria-label="Send message"
                type="submit"
              >
                {isSending ? "Sending..." : isTyping ? "Typing..." : "Send"}
              </button>
            </form>
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
