import React, { useState } from "react";
import { Send, SlidersHorizontal, Check } from "lucide-react";

const ChatInput = ({ onSend, disabled }) => {
  const [text, setText] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  
  // Local metadata filter state
  const [selectedStandards, setSelectedStandards] = useState([]);
  const [selectedSubjects, setSelectedSubjects] = useState([]);

  const standardsList = ["Std9", "Std10", "Std11", "Std12"];
  const subjectsList = ["Science", "Physics", "Chemistry", "Maths", "History"];

  const handleSend = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    
    // Pass text along with active filters
    onSend(text.trim(), selectedStandards, selectedSubjects);
    setText("");
  };

  const toggleStandard = (std) => {
    setSelectedStandards(prev => 
      prev.includes(std) ? prev.filter(s => s !== std) : [...prev, std]
    );
  };

  const toggleSubject = (sub) => {
    setSelectedSubjects(prev => 
      prev.includes(sub) ? prev.filter(s => s !== sub) : [...prev, sub]
    );
  };

  const clearFilters = () => {
    setSelectedStandards([]);
    setSelectedSubjects([]);
  };

  const hasActiveFilters = selectedStandards.length > 0 || selectedSubjects.length > 0;

  return (
    <div className="w-full space-y-3">
      {/* Collapsible Filters Panel */}
      {showFilters && (
        <div className="glass-card p-4 rounded-xl border border-slate-900 grid grid-cols-1 md:grid-cols-2 gap-4 animate-slide-in text-xs">
          {/* Standard Filters */}
          <div>
            <span className="block font-bold text-slate-400 uppercase tracking-wider mb-2">
              Filter by Academic Standard
            </span>
            <div className="flex flex-wrap gap-2">
              {standardsList.map((std) => {
                const active = selectedStandards.includes(std);
                return (
                  <button
                    key={std}
                    type="button"
                    onClick={() => toggleStandard(std)}
                    className={`px-3 py-1.5 rounded-lg border font-medium flex items-center gap-1 cursor-pointer transition-all ${
                      active 
                        ? "bg-teal-500/10 text-teal-400 border-teal-500/30" 
                        : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {active && <Check className="h-3 w-3" />}
                    <span>{std.replace("Std", "Standard ")}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Subject Filters */}
          <div>
            <span className="block font-bold text-slate-400 uppercase tracking-wider mb-2">
              Filter by Subject
            </span>
            <div className="flex flex-wrap gap-2">
              {subjectsList.map((sub) => {
                const active = selectedSubjects.includes(sub);
                return (
                  <button
                    key={sub}
                    type="button"
                    onClick={() => toggleSubject(sub)}
                    className={`px-3 py-1.5 rounded-lg border font-medium flex items-center gap-1 cursor-pointer transition-all ${
                      active 
                        ? "bg-teal-500/10 text-teal-400 border-teal-500/30" 
                        : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {active && <Check className="h-3 w-3" />}
                    <span>{sub}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Reset Filters */}
          <div className="md:col-span-2 flex justify-between items-center border-t border-slate-900 pt-3">
            <span className="text-[10px] text-slate-500">
              {hasActiveFilters 
                ? "Manual filters are active and override LLM auto-routing." 
                : "No manual filters active. System will auto-route standard & subject."}
            </span>
            {hasActiveFilters && (
              <button
                type="button"
                onClick={clearFilters}
                className="text-teal-400 hover:text-teal-350 font-bold tracking-wide uppercase text-[10px] cursor-pointer"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>
      )}

      {/* Input Bar */}
      <form onSubmit={handleSend} className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
            showFilters || hasActiveFilters
              ? "bg-teal-500/10 border-teal-500/30 text-teal-400"
              : "bg-slate-900/60 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
          title="Toggle metadata search filters"
        >
          <SlidersHorizontal className="h-5 w-5" />
        </button>

        <div className="relative flex-1">
          <input
            type="text"
            required
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={disabled}
            placeholder="Ask a question about the textbooks..."
            className="w-full bg-slate-900/60 border border-slate-800/80 focus:border-teal-500/50 rounded-xl px-4 py-3.5 pr-12 text-sm text-slate-200 placeholder-slate-500 focus:outline-none transition-colors disabled:opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={!text.trim() || disabled}
          className="p-3.5 bg-gradient-to-r from-teal-500 to-indigo-600 hover:from-teal-400 hover:to-indigo-500 disabled:from-slate-900 disabled:to-slate-900 text-slate-950 disabled:text-slate-600 border disabled:border-slate-800/50 rounded-xl transition-all shadow-lg shadow-teal-500/5 flex items-center justify-center cursor-pointer disabled:cursor-not-allowed hover:scale-[1.02] disabled:scale-100"
        >
          <Send className="h-5 w-5" />
        </button>
      </form>
    </div>
  );
};

export default ChatInput;
