import React from "react";
import UploadPDF from "../components/Upload/UploadPDF";

const UploadPage = () => {
  return (
    <div className="flex-1 overflow-y-auto h-[calc(100vh-73px)] py-6 bg-slate-950">
      <UploadPDF />
    </div>
  );
};

export default UploadPage;
