import React, { createContext, useState, useEffect, useContext } from "react";
import BASE_URL, { getAuthHeaders } from "../services/api";
import { 
  fetchSessions, 
  createSession, 
  deleteSession, 
  fetchSessionMessages 
} from "../services/chat";

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  
  // Streaming state
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [streamingCitations, setStreamingCitations] = useState([]);

  // Load user sessions
  const loadSessions = async () => {
    setLoadingSessions(true);
    try {
      const data = await fetchSessions();
      setSessions(data);
      // Select the first session if nothing is selected and sessions exist
      if (data.length > 0 && !currentSessionId) {
        selectSession(data[0].id);
      }
    } catch (error) {
      console.error("Failed to load sessions:", error);
    } finally {
      setLoadingSessions(false);
    }
  };

  // Select a session and load its messages
  const selectSession = async (sessionId) => {
    setCurrentSessionId(sessionId);
    setLoadingMessages(true);
    setMessages([]);
    try {
      const data = await fetchSessionMessages(sessionId);
      setMessages(data);
    } catch (error) {
      console.error("Failed to load session messages:", error);
    } finally {
      setLoadingMessages(false);
    }
  };

  // Start a new session
  const startNewSession = async (title = "New Conversation") => {
    try {
      const newSession = await createSession(title);
      setSessions(prev => [newSession, ...prev]);
      setCurrentSessionId(newSession.id);
      setMessages([]);
      return newSession.id;
    } catch (error) {
      console.error("Failed to create session:", error);
      throw error;
    }
  };

  // Delete a session
  const removeSession = async (sessionId) => {
    try {
      await deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSessionId === sessionId) {
        const remaining = sessions.filter(s => s.id !== sessionId);
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          setCurrentSessionId(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error("Failed to delete session:", error);
    }
  };

  // Send a message and stream the response
  const sendMessage = async (messageText, standards = null, subjects = null) => {
    let activeSessionId = currentSessionId;
    
    // If no active session, automatically start a new one
    if (!activeSessionId) {
      activeSessionId = await startNewSession();
    }

    // Append User message to local state immediately for fast feedback
    const tempUserMsg = {
      id: Date.now(),
      session_id: activeSessionId,
      role: "user",
      content: messageText,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    // Initialize streaming state
    setIsStreaming(true);
    setStreamingText("");
    setStreamingCitations([]);

    try {
      // Build API query parameters
      const params = new URLSearchParams();
      if (standards && standards.length > 0) {
        standards.forEach(std => params.append("standard", std));
      }
      if (subjects && subjects.length > 0) {
        subjects.forEach(sub => params.append("subject", sub));
      }
      
      let url = `${BASE_URL}/chat/sessions/${activeSessionId}/query`;
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const headers = getAuthHeaders();
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...headers
        },
        body: JSON.stringify({ message: messageText })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let accumulatedText = "";
      let finalCitations = [];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop(); // keep last partial line

        for (const line of lines) {
          const cleanLine = line.trim();
          if (cleanLine.startsWith("data: ")) {
            const jsonStr = cleanLine.slice(6);
            try {
              const parsed = JSON.parse(jsonStr);
              if (parsed.type === "metadata") {
                setStreamingCitations(parsed.citations);
                finalCitations = parsed.citations;
              } else if (parsed.type === "text") {
                setStreamingText(prev => prev + parsed.content);
                accumulatedText += parsed.content;
              } else if (parsed.type === "error") {
                const streamErr = new Error(parsed.content);
                streamErr.isStreamError = true;
                throw streamErr;
              }
            } catch (err) {
              if (err.isStreamError) {
                throw err;
              }
              console.error("Error parsing stream chunk:", err);
            }
          }
        }
      }

      // Finish streaming and sync database
      setIsStreaming(false);
      setStreamingText("");
      setStreamingCitations([]);

      // Reload messages to get final IDs and citations
      const updatedMessages = await fetchSessionMessages(activeSessionId);
      setMessages(updatedMessages);
      
      // Reload sessions list to update session title if changed
      const updatedSessions = await fetchSessions();
      setSessions(updatedSessions);
      
    } catch (error) {
      console.error("Streaming message failed:", error);
      setIsStreaming(false);
      setStreamingText("");
      setStreamingCitations([]);
      
      // Append an error message from assistant
      const tempErrorMsg = {
        id: Date.now() + 1,
        session_id: activeSessionId,
        role: "assistant",
        content: `I am sorry, but an error occurred: ${error.message || "Please check your network or try again."}`,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, tempErrorMsg]);
    }
  };

  return (
    <ChatContext.Provider value={{
      sessions,
      currentSessionId,
      messages,
      loadingSessions,
      loadingMessages,
      isStreaming,
      streamingText,
      streamingCitations,
      loadSessions,
      selectSession,
      startNewSession,
      removeSession,
      sendMessage
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);
