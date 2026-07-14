import React from "react";

const Button = ({ 
  children, 
  onClick, 
  type = "button", 
  variant = "primary", 
  disabled = false, 
  className = "" 
}) => {
  const baseStyle = "px-4 py-2.5 rounded-xl font-semibold text-sm transition-all focus:outline-none flex items-center justify-center gap-2 cursor-pointer";
  
  const variants = {
    primary: "bg-gradient-to-r from-teal-500 to-indigo-600 hover:from-teal-400 hover:to-indigo-500 text-slate-950 shadow-md shadow-teal-500/10 disabled:opacity-50",
    secondary: "bg-slate-900 border border-slate-800 text-slate-300 hover:text-slate-100 hover:bg-slate-800 disabled:opacity-50",
    danger: "bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 disabled:opacity-50",
    success: "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 disabled:opacity-50",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyle} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;
