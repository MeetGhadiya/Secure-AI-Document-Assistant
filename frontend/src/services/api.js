import axios from "axios";

const client = axios.create({
  baseURL: "/api",
});

function withSession(sessionId, config = {}) {
  return {
    ...config,
    headers: {
      ...(config.headers || {}),
      "X-Session-Id": sessionId,
    },
  };
}

export async function uploadDocument(sessionId, file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await client.post(
    "/upload",
    formData,
    withSession(sessionId, { headers: { "Content-Type": "multipart/form-data" } })
  );
  return data;
}

export async function listDocuments(sessionId) {
  const { data } = await client.get("/documents", withSession(sessionId));
  return data;
}

export async function deleteDocument(sessionId, documentId) {
  const { data } = await client.delete(`/documents/${documentId}`, withSession(sessionId));
  return data;
}

export async function queryDocuments(sessionId, question, documentId = null) {
  const { data } = await client.post(
    "/query",
    { question, document_id: documentId },
    withSession(sessionId)
  );
  return data;
}
