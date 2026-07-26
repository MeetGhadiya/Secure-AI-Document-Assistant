import { useCallback, useEffect, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import ChatInterface from "./components/ChatInterface.jsx";
import SecurityPanel from "./components/SecurityPanel.jsx";
import { useSession } from "./hooks/useSession.js";
import { listDocuments, uploadDocument, deleteDocument } from "./services/api.js";

export default function App() {
  const sessionId = useSession();
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const refreshDocuments = useCallback(async () => {
    if (!sessionId) return;
    try {
      const docs = await listDocuments(sessionId);
      setDocuments(docs);
    } catch (err) {
      setError("Could not load documents for this session.");
    }
  }, [sessionId]);

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  const handleUpload = async (file) => {
    setUploading(true);
    setError(null);
    try {
      await uploadDocument(sessionId, file);
      await refreshDocuments();
    } catch (err) {
      setError(err?.response?.data?.detail || "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId) => {
    try {
      await deleteDocument(sessionId, documentId);
      if (selectedDocument?.id === documentId) setSelectedDocument(null);
      await refreshDocuments();
    } catch (err) {
      setError("Could not delete document.");
    }
  };

  const readyDocuments = documents.filter((d) => d.status === "ready");

  return (
    <div className="flex h-screen w-full bg-background">
      <Sidebar
        documents={documents}
        uploading={uploading}
        onUpload={handleUpload}
        onDelete={handleDelete}
        selectedDocument={selectedDocument}
        onSelectDocument={setSelectedDocument}
      />

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-outline bg-surface px-6 py-4">
          <div>
            <h1 className="text-base font-bold text-on-surface">
              {selectedDocument ? selectedDocument.original_filename : "All Documents"}
            </h1>
            <p className="text-xs text-on-surface-variant">
              Answers are generated only from your uploaded, session-isolated documents.
            </p>
          </div>
          {error && (
            <p className="rounded-md bg-danger-container px-3 py-1.5 text-xs font-medium text-danger">
              {error}
            </p>
          )}
        </header>

        <div className="min-h-0 flex-1">
          <ChatInterface
            sessionId={sessionId}
            selectedDocument={selectedDocument}
            hasDocuments={readyDocuments.length > 0}
          />
        </div>
      </main>

      <SecurityPanel sessionId={sessionId} />
    </div>
  );
}
