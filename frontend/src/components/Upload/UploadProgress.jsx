import React from "react";

const UploadProgress = ({ progress, filename }) => {
  if (progress === null || progress === undefined) return null;

  return (
    <div className="w-full bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-2 text-xs">
      <div className="flex justify-between font-semibold text-slate-300">
        <span className="truncate max-w-[80%]">Uploading {filename}</span>
        <span>{progress}%</span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
        <div 
          className="bg-gradient-to-r from-teal-500 to-indigo-500 h-1.5 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

export default UploadProgress;
