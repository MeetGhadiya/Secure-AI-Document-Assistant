import { useEffect, useRef, useState } from "react";
import { Send, Loader2 } from "lucide-react";
import ChatMessage from "./ChatMessage.jsx";
import { queryDocuments } from "../services/api.js";

export default function ChatInterface({ sessionId, selectedDocument, hasDocuments }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    const question = input.trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const result = await queryDocuments(sessionId, question, selectedDocument?.id ?? null);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.answer, sources: result.sources },
      ]);
    } catch (err) {
      const detail = err?.response?.data?.detail || "Something went wrong reaching the assistant.";
      setMessages((prev) => [...prev, { role: "assistant", content: detail, sources: [] }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-6">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center text-on-surface-variant">
            <p className="text-sm">
              {hasDocuments
                ? "Ask a question about your uploaded documents."
                : "Upload a document to start asking questions."}
            </p>
            {selectedDocument && (
              <p className="mt-1 text-xs">
                Scoped to <span className="font-semibold">{selectedDocument.original_filename}</span>
              </p>
            )}
          </div>
        )}

        {messages.map((m, i) => (
          <ChatMessage key={i} role={m.role} content={m.content} sources={m.sources} />
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-lg border border-outline bg-surface px-4 py-3 text-sm text-on-surface-variant shadow-soft">
              <Loader2 className="animate-spin" size={15} />
              Retrieving relevant context…
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-outline p-4">
        <div className="flex items-center gap-2 rounded-full border border-outline bg-surface px-3 py-2 focus-within:border-electric">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={!hasDocuments}
            placeholder={hasDocuments ? "Ask about your documents…" : "Upload a document first"}
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-on-surface-variant disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSend}
            disabled={!hasDocuments || loading || !input.trim()}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-navy text-white disabled:opacity-30"
            aria-label="Send"
          >
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
