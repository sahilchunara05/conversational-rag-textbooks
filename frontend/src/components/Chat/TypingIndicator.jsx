import React from "react";
import { Sparkles } from "lucide-react";

const TypingIndicator = () => {
  return (
    <div className="flex w-full gap-4 my-4 justify-start items-start animate-pulse">
      <div className="h-9 w-9 shrink-0 flex items-center justify-center rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
        <Sparkles className="h-4 w-4" />
      </div>
      
      <div className="flex flex-col gap-1.5">
        <div className="glass-card px-5 py-4 rounded-2xl rounded-tl-none text-sm text-slate-400 flex items-center gap-2">
          <span>Thinking and searching textbooks</span>
          <span className="flex gap-1 items-center justify-center">
            <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
            <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
            <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce"></span>
          </span>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
