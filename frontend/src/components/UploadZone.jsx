import { useRef, useState } from "react";
import { UploadCloud, Loader2 } from "lucide-react";

const ACCEPTED = ".pdf,.docx,.txt";

export default function UploadZone({ onUpload, uploading }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = (files) => {
    if (files && files.length > 0) {
      onUpload(files[0]);
    }
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
      className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
        dragOver ? "border-electric bg-electric/5" : "border-outline-variant bg-surface-container-high/40"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      {uploading ? (
        <>
          <Loader2 className="animate-spin text-navy" size={28} />
          <p className="text-sm font-medium text-on-surface">Processing document…</p>
        </>
      ) : (
        <>
          <UploadCloud className="text-navy" size={28} />
          <p className="text-sm font-semibold text-on-surface">Drop a document here, or click to browse</p>
          <p className="text-xs text-on-surface-variant">PDF, DOCX, or TXT · Max 20MB · Encrypted at rest</p>
        </>
      )}
    </div>
  );
}
