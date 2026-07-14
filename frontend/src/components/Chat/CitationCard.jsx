import React, { useState } from "react";
import { BookOpen, ChevronDown, ChevronUp } from "lucide-react";

const CitationCard = ({ citation, index }) => {
  const [expanded, setExpanded] = useState(false);
  const { source, page, subject, standard, snippet } = citation;

  return (
    <div className="glass-card rounded-xl border border-slate-900 overflow-hidden text-xs transition-all duration-200">
      {/* Header Summary */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-slate-800/20 transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-teal-500/10 rounded-lg text-teal-400">
            <BookOpen className="h-3.5 w-3.5" />
          </div>
          <div>
            <span className="font-semibold text-slate-200">
              [{index}] {source}
            </span>
            <span className="ml-2 text-slate-500 font-medium">
              • Page {page}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="bg-slate-900 border border-slate-800 text-teal-400 font-bold px-2 py-0.5 rounded text-[10px] tracking-wide uppercase">
            {standard} - {subject}
          </span>
          {expanded ? (
            <ChevronUp className="h-3.5 w-3.5 text-slate-500" />
          ) : (
            <ChevronDown className="h-3.5 w-3.5 text-slate-500" />
          )}
        </div>
      </button>

      {/* Expanded snippet */}
      {expanded && (
        <div className="px-4 pb-3.5 pt-1 text-slate-350 leading-relaxed border-t border-slate-900/60 bg-slate-900/10">
          <p className="font-mono text-[11px] select-text">
            "{snippet}"
          </p>
        </div>
      )}
    </div>
  );
};

export default CitationCard;
