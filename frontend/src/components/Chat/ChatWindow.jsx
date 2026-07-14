import React, { useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import ChatInput from "./ChatInput";
import { useChat } from "../../context/ChatContext";
import { Sparkles, MessageSquarePlus, GraduationCap } from "lucide-react";

const ChatWindow = () => {
  const {
    messages,
    isStreaming,
    streamingText,
    streamingCitations,
    sendMessage,
    startNewSession
  } = useChat();

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Scroll to bottom when messages or streaming text change
  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingText, isStreaming]);

  const handleSend = (text, standards, subjects) => {
    sendMessage(text, standards, subjects);
  };

  const sampleQueries = [
    { text: "What is the powerhouse of the cell?", label: "Biology" },
    { text: "Explain the difference between exothermic and endothermic reactions.", label: "Chemistry" },
    { text: "What is the SI unit of force and energy?", label: "Physics" },
    { text: "What is a unit cell in a crystal lattice?", label: "Material Science" }
  ];

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-slate-950">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && !isStreaming ? (
          /* Empty / New Conversation Welcome Area */
          <div className="h-full flex flex-col items-center justify-center max-w-2xl mx-auto text-center space-y-8 animate-slide-in">
            <div className="p-4 bg-teal-500/10 rounded-3xl border border-teal-500/20 text-teal-400">
              <GraduationCap className="h-12 w-12" />
            </div>
            
            <div className="space-y-3">
              <h2 className="text-3xl font-extrabold bg-gradient-to-r from-teal-200 via-teal-400 to-indigo-400 bg-clip-text text-transparent">
                Textbook RAG Assistant
              </h2>
              <p className="text-slate-400 text-sm max-w-md mx-auto leading-relaxed">
                Ask questions and study. Answers are generated strictly from Gujarat State Board textbooks (Std 9–12) with direct citations.
              </p>
            </div>

            <div className="w-full space-y-3 pt-4">
              <span className="block text-[10px] uppercase font-bold tracking-wider text-slate-500">
                Sample queries to get started
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {sampleQueries.map((query, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(query.text)}
                    className="glass-card hover:bg-slate-800/40 border border-slate-900 hover:border-teal-500/35 p-4 rounded-2xl text-left text-xs font-semibold text-slate-350 hover:text-slate-200 transition-all cursor-pointer flex flex-col gap-1 hover:scale-[1.01]"
                  >
                    <span className="text-[10px] text-teal-400 uppercase tracking-widest font-bold">
                      {query.label}
                    </span>
                    <span>"{query.text}"</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Message List */
          <div className="max-w-4xl mx-auto w-full">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            
            {/* Streaming Message Bubble */}
            {isStreaming && streamingText && (
              <MessageBubble 
                message={{
                  id: "streaming",
                  role: "assistant",
                  content: streamingText,
                  citations: streamingCitations,
                  created_at: new Date().toISOString()
                }} 
              />
            )}

            {/* Thinking state (before streaming starts) */}
            {isStreaming && !streamingText && (
              <TypingIndicator />
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input panel at bottom */}
      <div className="border-t border-slate-900 bg-slate-950/80 backdrop-blur px-6 py-5">
        <div className="max-w-4xl mx-auto w-full">
          <ChatInput onSend={handleSend} disabled={isStreaming} />
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
