import React from "react";
import { Loader2 } from "lucide-react";

const Loader = ({ message = "Loading..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-slate-400">
      <Loader2 className="h-8 w-8 animate-spin text-teal-400 mb-2" />
      <span className="text-sm font-medium">{message}</span>
    </div>
  );
};

export default Loader;
