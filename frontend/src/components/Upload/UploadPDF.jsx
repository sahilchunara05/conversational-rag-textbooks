import React, { useState, useEffect } from "react";
import { fetchDocuments, uploadDocumentFile, deleteDocument } from "../../services/chat";
import { Upload, Trash2, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

const UploadPDF = () => {
  const [file, setFile] = useState(null);
  const [standard, setStandard] = useState("Std10");
  const [subject, setSubject] = useState("Science");
  
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const standardsList = ["Std9", "Std10", "Std11", "Std12"];
  const subjectsList = ["Science", "Physics", "Chemistry", "Maths", "History"];

  const loadDocs = async () => {
    setLoadingDocs(true);
    try {
      const data = await fetchDocuments();
      setDocuments(data);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleFileChange = (e) => {
    setErrorMsg("");
    setSuccessMsg("");
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith(".pdf")) {
        setErrorMsg("Only PDF files are supported.");
        setFile(null);
      } else {
        setFile(selectedFile);
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      await uploadDocumentFile(file, standard, subject);
      setSuccessMsg(`Successfully uploaded and indexed '${file.name}'!`);
      setFile(null);
      
      // Clear file input
      const fileInput = document.getElementById("textbook-file");
      if (fileInput) fileInput.value = "";

      // Reload documents table
      loadDocs();
    } catch (err) {
      setErrorMsg(err.message || "Failed to upload file.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId, filename) => {
    if (!confirm(`Are you sure you want to delete and purge the index for '${filename}'?`)) return;
    
    try {
      await deleteDocument(docId);
      setDocuments(prev => prev.filter(d => d.id !== docId));
      setSuccessMsg(`Deleted and purged textbook '${filename}' successfully.`);
    } catch (err) {
      setErrorMsg(err.message || "Failed to delete document.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8 animate-slide-in">
      
      {/* Page Title */}
      <div>
        <h1 className="text-2xl font-extrabold bg-gradient-to-r from-teal-200 to-indigo-450 bg-clip-text text-transparent">
          Textbook Knowledge Base Manager
        </h1>
        <p className="text-slate-400 text-xs mt-1">
          Upload textbook PDFs to standard-specific folders to build the conversational RAG search index.
        </p>
      </div>

      {/* Upload Box Form */}
      <div className="glass p-6 rounded-2xl border border-slate-900 grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Upload Config Panel */}
        <form onSubmit={handleUpload} className="md:col-span-2 space-y-4 flex flex-col justify-between">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                Standard
              </label>
              <select
                value={standard}
                onChange={(e) => setStandard(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-teal-500/50"
              >
                {standardsList.map((std) => (
                  <option key={std} value={std}>
                    {std.replace("Std", "Standard ")}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                Subject
              </label>
              <select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-teal-500/50"
              >
                {subjectsList.map((sub) => (
                  <option key={sub} value={sub}>
                    {sub}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Drag & Drop Area */}
          <div className="border-2 border-dashed border-slate-800 hover:border-teal-500/30 rounded-2xl p-6 text-center cursor-pointer transition-colors relative flex flex-col items-center justify-center min-h-[140px] bg-slate-900/10">
            <input
              type="file"
              id="textbook-file"
              accept=".pdf"
              required
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <Upload className="h-8 w-8 text-slate-500 mb-2.5" />
            <span className="block text-xs font-semibold text-slate-350">
              {file ? file.name : "Select or drag & drop textbook PDF"}
            </span>
            <span className="block text-[10px] text-slate-500 mt-1">
              Supports PDF files up to 25MB
            </span>
          </div>

          {/* Submit Action */}
          <button
            type="submit"
            disabled={!file || uploading}
            className="w-full bg-gradient-to-r from-teal-500 to-indigo-600 hover:from-teal-400 hover:to-indigo-500 text-slate-950 font-bold py-3 px-4 rounded-xl transition-all shadow-md shadow-teal-500/10 flex justify-center items-center gap-2 cursor-pointer disabled:opacity-50 hover:scale-[1.01]"
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-slate-950" />
                <span>Extracting & Indexing Text...</span>
              </>
            ) : (
              <span>Add Textbook to Knowledge Base</span>
            )}
          </button>
        </form>

        {/* Info Box */}
        <div className="bg-slate-900/30 p-5 rounded-2xl border border-slate-900/80 flex flex-col justify-between text-xs space-y-4">
          <div className="space-y-2">
            <span className="block font-bold text-slate-400 uppercase tracking-widest text-[9px]">
              Ingestion Details
            </span>
            <p className="text-slate-450 leading-relaxed">
              When you add a textbook, the system runs an automatic ingestion process:
            </p>
            <ul className="list-disc pl-4 space-y-1 text-slate-450">
              <li>Extracts text page-by-page.</li>
              <li>Performs multimodal OCR fallback on scanned diagrams/pages.</li>
              <li>Splits text into sliding chunks.</li>
              <li>Generates Gemini embeddings.</li>
              <li>Stores vectors into a custom local index.</li>
            </ul>
          </div>
          
          <div className="text-[10px] text-teal-400/80 font-semibold bg-teal-500/5 border border-teal-500/10 p-3 rounded-xl">
            Auto-routing will parse these standard & subject tags.
          </div>
        </div>
      </div>

      {/* Alerts */}
      {successMsg && (
        <div className="p-4 bg-teal-500/10 border border-teal-500/20 rounded-xl flex items-start gap-3 text-teal-300 text-sm">
          <CheckCircle2 className="h-5 w-5 shrink-0 mt-0.5" />
          <span>{successMsg}</span>
        </div>
      )}
      
      {errorMsg && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3 text-red-300 text-sm">
          <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Document Catalog */}
      <div className="space-y-3">
        <h2 className="text-lg font-bold text-slate-200">
          Indexed Textbooks Catalogue ({documents.length})
        </h2>
        
        {loadingDocs ? (
          <div className="text-center p-6 text-slate-500 flex justify-center items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin text-teal-400" />
            <span>Loading database catalog...</span>
          </div>
        ) : documents.length === 0 ? (
          <div className="glass p-8 text-center text-xs text-slate-500 rounded-2xl border border-slate-900">
            No textbooks have been indexed yet. Upload one above to get started!
          </div>
        ) : (
          <div className="glass rounded-2xl border border-slate-900 overflow-hidden">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-900/50 border-b border-slate-900 text-slate-400 font-bold uppercase tracking-wider">
                  <th className="p-4">Filename</th>
                  <th className="p-4">Standard</th>
                  <th className="p-4">Subject</th>
                  <th className="p-4">Indexed Date</th>
                  <th className="p-4 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-900/20 text-slate-300 transition-colors">
                    <td className="p-4 font-medium flex items-center gap-2 max-w-xs truncate">
                      <FileText className="h-4 w-4 text-teal-400 shrink-0" />
                      <span className="truncate" title={doc.filename}>{doc.filename}</span>
                    </td>
                    <td className="p-4 font-semibold text-slate-400">
                      {doc.standard.replace("Std", "Standard ")}
                    </td>
                    <td className="p-4">
                      <span className="bg-slate-900 border border-slate-800/80 text-teal-400 font-bold px-2.5 py-1 rounded-lg text-[10px]">
                        {doc.subject}
                      </span>
                    </td>
                    <td className="p-4 text-slate-500">
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-center">
                      <button
                        onClick={() => handleDelete(doc.id, doc.filename)}
                        className="p-2 hover:text-red-400 rounded-lg hover:bg-slate-900 transition-colors cursor-pointer"
                        title="Delete and purge textbook"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadPDF;
