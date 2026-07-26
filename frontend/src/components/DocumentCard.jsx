import { FileText, Trash2 } from "lucide-react";
import SecurityBadge from "./SecurityBadge.jsx";

const STATUS_STYLES = {
  ready: { label: "Ready", badge: "Secured" },
  processing: { label: "Processing…", badge: "Encrypting" },
  failed: { label: "Failed", badge: null },
};

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentCard({ document, onDelete, selected, onSelect }) {
  const status = STATUS_STYLES[document.status] || STATUS_STYLES.processing;

  function handleKeyDown(e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onSelect(document);
    }
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onSelect(document)}
      onKeyDown={handleKeyDown}
      className={`w-full text-left rounded-lg border p-4 transition-all hover:shadow-soft hover:border-navy/40 ${
        selected ? "border-navy bg-surface-container" : "border-outline bg-surface"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-surface-container text-navy">
            <FileText size={18} />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-on-surface">
              {document.original_filename}
            </p>
            <p className="mt-0.5 text-xs text-on-surface-variant">
              {document.file_type.replace(".", "").toUpperCase()} · {formatSize(document.file_size_bytes)} ·{" "}
              {document.chunk_count} chunks
            </p>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(document.id);
          }}
          className="shrink-0 rounded-md p-1.5 text-on-surface-variant hover:bg-danger-container hover:text-danger"
          aria-label="Delete document"
        >
          <Trash2 size={15} />
        </button>
      </div>
      <div className="mt-3 flex items-center justify-between">
        <span className="text-xs font-medium text-on-surface-variant">{status.label}</span>
        {status.badge && <SecurityBadge label={status.badge} />}
      </div>
    </div>
  );
}
