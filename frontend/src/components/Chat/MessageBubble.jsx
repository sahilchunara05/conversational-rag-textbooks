import React from "react";
import CitationCard from "./CitationCard";
import { User, Sparkles } from "lucide-react";

// Simple self-contained text formatter for basic Markdown & citations
const FormattedText = ({ text }) => {
  if (!text) return null;

  // Split by newlines to form paragraphs/lines
  const lines = text.split("\n");

  return (
    <div className="space-y-2 select-text">
      {lines.map((line, lIdx) => {
        // Render lists
        if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
          return (
            <ul key={lIdx} className="list-disc pl-5 my-1 text-slate-300">
              <li>{renderInlineStyles(line.trim().substring(2))}</li>
            </ul>
          );
        }
        
        // Render numbered lists
        const numListMatch = line.trim().match(/^(\d+)\.\s+(.*)/);
        if (numListMatch) {
          return (
            <ol key={lIdx} className="list-decimal pl-5 my-1 text-slate-300">
              <li>{renderInlineStyles(numListMatch[2])}</li>
            </ol>
          );
        }

        // Render empty lines as spacers
        if (line.trim() === "") {
          return <div key={lIdx} className="h-2" />;
        }

        // Default paragraph
        return (
          <p key={lIdx} className="leading-relaxed text-slate-200">
            {renderInlineStyles(line)}
          </p>
        );
      })}
    </div>
  );
};

// Formats inline bold text (**), inline code (`), and citations ([1])
const renderInlineStyles = (line) => {
  // Regex to find bold elements, code snippets, and citation brackets
  const regex = /(\*\*.*?\*\*|`.*?`|\[\d+\])/g;
  const parts = line.split(regex);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={index} className="font-bold text-slate-100">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={index} className="bg-slate-900 border border-slate-800 text-teal-300 px-1.5 py-0.5 rounded font-mono text-xs">
          {part.slice(1, -1)}
        </code>
      );
    }
    // Citation badge link
    const citationMatch = part.match(/^\[(\d+)\]$/);
    if (citationMatch) {
      const citNum = citationMatch[1];
      return (
        <span 
          key={index} 
          className="inline-flex items-center justify-center bg-teal-500/20 hover:bg-teal-500/35 text-teal-400 border border-teal-500/30 text-[10px] font-bold rounded-full w-4.5 h-4.5 mx-0.5 cursor-pointer transition-colors"
          title={`View Source Citation [${citNum}]`}
          onClick={() => {
            const el = document.getElementById(`citation-${citNum}`);
            if (el) {
              el.scrollIntoView({ behavior: "smooth", block: "center" });
              // Flash styling
              el.classList.add("ring-2", "ring-teal-500");
              setTimeout(() => el.classList.remove("ring-2", "ring-teal-500"), 1500);
            }
          }}
        >
          {citNum}
        </span>
      );
    }
    return part;
  });
};

const MessageBubble = ({ message }) => {
  const { role, content, citations, created_at } = message;
  const isUser = role === "user";

  return (
    <div className={`flex w-full gap-4 my-4 ${isUser ? "justify-end" : "justify-start"}`}>
      {/* Icon/Avatar for Assistant */}
      {!isUser && (
        <div className="h-9 w-9 shrink-0 flex items-center justify-center rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
          <Sparkles className="h-4 w-4" />
        </div>
      )}

      {/* Message Content Container */}
      <div className="max-w-[85%] sm:max-w-[75%] flex flex-col gap-2">
        <div 
          className={`px-5 py-4 rounded-2xl text-sm shadow-md transition-all ${
            isUser 
              ? "bg-gradient-to-br from-teal-500/20 to-indigo-600/25 border border-teal-500/20 text-slate-100 rounded-tr-none" 
              : "glass-card text-slate-200 rounded-tl-none"
          }`}
        >
          <FormattedText text={content} />
        </div>

        {/* Timestamp */}
        <span className={`text-[10px] text-slate-500 font-semibold px-2 ${isUser ? "text-right" : "text-left"}`}>
          {new Date(created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>

        {/* Citations Drawer (Assistant only) */}
        {!isUser && citations && citations.length > 0 && (
          <div className="mt-2 space-y-2">
            <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider px-2">
              Sources & Citations
            </div>
            <div className="grid grid-cols-1 gap-2">
              {citations.map((citation, idx) => (
                <div key={idx} id={`citation-${idx + 1}`}>
                  <CitationCard citation={citation} index={idx + 1} />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Avatar for User */}
      {isUser && (
        <div className="h-9 w-9 shrink-0 flex items-center justify-center rounded-xl bg-slate-900 border border-slate-800 text-slate-400">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
