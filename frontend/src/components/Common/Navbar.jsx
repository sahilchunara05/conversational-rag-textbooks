import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { BookOpen, LogOut, MessageSquare, Upload } from "lucide-react";

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <header className="glass sticky top-0 z-50 w-full border-b border-slate-900 px-6 py-4 flex justify-between items-center">
      {/* Brand logo */}
      <Link to="/" className="flex items-center gap-2.5">
        <div className="p-2 bg-teal-500/10 rounded-xl border border-teal-500/20">
          <BookOpen className="h-5 w-5 text-teal-400" />
        </div>
        <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-teal-200 to-indigo-400 bg-clip-text text-transparent">
          Textbook RAG
        </span>
      </Link>

      {/* Navigation */}
      {user && (
        <nav className="flex items-center gap-1.5 md:gap-4">
          <Link
            to="/"
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              isActive("/") 
                ? "bg-teal-500/10 text-teal-400 border border-teal-500/25" 
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
            }`}
          >
            <MessageSquare className="h-4 w-4" />
            <span className="hidden sm:inline">Conversations</span>
          </Link>
          
          <Link
            to="/upload"
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              isActive("/upload") 
                ? "bg-teal-500/10 text-teal-400 border border-teal-500/25" 
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
            }`}
          >
            <Upload className="h-4 w-4" />
            <span className="hidden sm:inline">Upload Textbook</span>
          </Link>
        </nav>
      )}

      {/* Profile / Logout */}
      {user && (
        <div className="flex items-center gap-4">
          <div className="hidden md:flex flex-col items-end text-right">
            <span className="text-sm font-semibold text-slate-200">{user.username}</span>
            <span className="text-[10px] text-teal-400 uppercase tracking-wider font-bold">Student</span>
          </div>
          <button
            onClick={logout}
            className="flex items-center gap-2 bg-slate-900/60 hover:bg-slate-900 text-slate-400 hover:text-red-400 px-3 py-2 rounded-xl border border-slate-800 transition-all cursor-pointer hover:border-red-500/20"
            title="Log out"
          >
            <LogOut className="h-4 w-4" />
            <span className="hidden md:inline text-xs font-semibold">Log out</span>
          </button>
        </div>
      )}
    </header>
  );
};

export default Navbar;
