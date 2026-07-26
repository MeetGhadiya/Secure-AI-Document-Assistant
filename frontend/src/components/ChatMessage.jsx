import { ShieldCheck } from "lucide-react";

export default function ChatMessage({ role, content, sources }) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "bg-navy text-white"
            : "border border-outline bg-surface text-on-surface shadow-soft"
        }`}
      >
        <p className="whitespace-pre-wrap">{content}</p>

        {!isUser && sources && sources.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5 border-t border-outline pt-2">
            {sources.map((s, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 rounded-full bg-electric/10 px-2 py-0.5 text-[11px] font-medium text-electric-strong"
                title={s.redactions > 0 ? `${s.redactions} value(s) masked before sending to the model` : "No sensitive data detected"}
              >
                doc {s.document_id.slice(0, 6)} · chunk {s.chunk_index}
                {s.redactions > 0 && <ShieldCheck size={11} />}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
