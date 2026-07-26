import { ShieldCheck } from "lucide-react";
import UploadZone from "./UploadZone.jsx";
import DocumentCard from "./DocumentCard.jsx";

export default function Sidebar({
  documents,
  uploading,
  onUpload,
  onDelete,
  selectedDocument,
  onSelectDocument,
}) {
  return (
    <aside className="flex h-full w-[320px] shrink-0 flex-col border-r border-outline bg-surface">
      <div className="border-b border-outline p-5">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-navy text-white">
            <ShieldCheck size={16} />
          </div>
          <div>
            <p className="text-sm font-bold leading-tight text-on-surface">Secure Intelligence</p>
            <p className="text-[11px] text-on-surface-variant">Document RAG Assistant</p>
          </div>
        </div>
      </div>

      <div className="p-5">
        <UploadZone onUpload={onUpload} uploading={uploading} />
      </div>

      <div className="flex-1 overflow-y-auto px-5 pb-5">
        <div className="mb-2 flex items-center justify-between">
          <p className="text-xs font-semibold uppercase tracking-wide text-on-surface-variant">
            Your Documents
          </p>
          <span className="text-xs text-on-surface-variant">{documents.length}</span>
        </div>

        {documents.length === 0 ? (
          <p className="mt-4 text-center text-xs text-on-surface-variant">
            No documents yet. Uploads are isolated to this browser session only.
          </p>
        ) : (
          <div className="space-y-2">
            <button
              onClick={() => onSelectDocument(null)}
              className={`w-full rounded-lg border px-3 py-2 text-left text-xs font-medium transition-colors ${
                !selectedDocument
                  ? "border-navy bg-surface-container text-navy"
                  : "border-outline text-on-surface-variant hover:border-navy/30"
              }`}
            >
              Search across all documents
            </button>
            {documents.map((doc) => (
              <DocumentCard
                key={doc.id}
                document={doc}
                onDelete={onDelete}
                selected={selectedDocument?.id === doc.id}
                onSelect={onSelectDocument}
              />
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
