import BASE_URL, { request, getAuthHeaders } from "./api";

// Session Management
export const fetchSessions = async () => {
  return request("/sessions");
};

export const createSession = async (title = "New Conversation") => {
  return request("/sessions", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
};

export const deleteSession = async (sessionId) => {
  return request(`/sessions/${sessionId}`, {
    method: "DELETE",
  });
};

export const fetchSessionMessages = async (sessionId) => {
  return request(`/sessions/${sessionId}/messages`);
};

// Document Management
export const fetchDocuments = async () => {
  return request("/upload/list");
};

export const deleteDocument = async (docId) => {
  return request(`/upload/${docId}`, {
    method: "DELETE",
  });
};

export const uploadDocumentFile = async (file, standard, subject, onUploadProgress) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("standard", standard);
  formData.append("subject", subject);

  const token = localStorage.getItem("token");
  
  // Custom fetch configuration for multipart upload
  const response = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`
      // Let the browser set the boundary automatically for FormData
    },
    body: formData
  });

  if (response.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/login";
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
  }

  return response.json();
};
