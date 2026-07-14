import React, { useEffect } from "react";
import { useChat } from "../../context/ChatContext";
import { MessageSquare, Trash2, Plus, LogOut } from "lucide-react";

const SessionList = () => {
  const {
    sessions,
    currentSessionId,
    loadSessions,
    selectSession,
    startNewSession,
    removeSession
  } = useChat();

  useEffect(() => {
    loadSessions();
  }, []);

  return (
    <div className="w-80 h-full border-r border-slate-900 bg-slate-950/60 backdrop-blur flex flex-col">
      {/* Action Header */}
      <div className="p-4 border-b border-slate-900">
        <button
          onClick={() => startNewSession()}
          className="w-full bg-gradient-to-r from-teal-500 to-indigo-600 hover:from-teal-400 hover:to-indigo-500 text-slate-950 font-bold py-3 px-4 rounded-xl transition-all shadow-md shadow-teal-500/10 flex justify-center items-center gap-2 cursor-pointer hover:scale-[1.01]"
        >
          <Plus className="h-4 w-4" />
          <span>New Conversation</span>
        </button>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        <span className="block text-[10px] uppercase font-bold tracking-wider text-slate-500 px-3 py-2">
          Conversation History
        </span>

        {sessions.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">
            No history yet
          </div>
        ) : (
          sessions.map((session) => {
            const active = session.id === currentSessionId;
            return (
              <div
                key={session.id}
                className={`group flex items-center justify-between rounded-xl transition-all p-1 ${
                  active 
                    ? "bg-slate-900 border border-slate-800 text-teal-400" 
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/30"
                }`}
              >
                <button
                  onClick={() => selectSession(session.id)}
                  className="flex-1 flex items-center gap-3 px-3 py-2.5 text-left text-xs font-semibold cursor-pointer truncate"
                >
                  <MessageSquare className={`h-4 w-4 shrink-0 ${active ? "text-teal-400" : "text-slate-500"}`} />
                  <span className="truncate">{session.title}</span>
                </button>

                <button
                  onClick={() => removeSession(session.id)}
                  className="p-2 opacity-0 group-hover:opacity-100 hover:text-red-400 rounded-lg hover:bg-slate-800/40 transition-all cursor-pointer mr-1"
                  title="Delete conversation"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default SessionList;
