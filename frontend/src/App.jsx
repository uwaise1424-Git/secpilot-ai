import { useState } from 'react'
import './App.css'

function App() {
  // These are our state variables. They hold the data as it changes in real-time.
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)

  // This function triggers when you click the upload button
  const handleUpload = async () => {
    if (!file) {
      alert("Please select a log file first, bruh!")
      return
    }

    setLoading(true)
    setReport(null) // Clear any old reports

    // Package the file securely to send over HTTP
    const formData = new FormData()
    formData.append('file', file)

    try {
      // Send the POST request to our FastAPI backend
      const response = await fetch('http://localhost:8000/api/logs/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error("Backend connection failed")

      // Unpack the JSON response from Llama 3
      const data = await response.json()
      
      // Update our React state with the AI Analysis, which will trigger the Alert Card to appear
      setReport(data.ai_analysis)
    } catch (error) {
      console.error("Error:", error)
      alert("Failed to analyze logs. Is the FastAPI server running?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center p-10 font-sans">
      
      {/* Header Section */}
      <div className="max-w-3xl w-full text-center mb-10 mt-10">
        <h1 className="text-5xl font-extrabold text-blue-500 tracking-tight mb-3">
          SecPilot AI SOC
        </h1>
        <p className="text-gray-400 text-lg">
          Automated Threat Detection & Log Analysis Engine
        </p>
      </div>

      {/* Upload Control Zone */}
      <div className="max-w-xl w-full bg-slate-800 p-8 rounded-xl border border-slate-700 shadow-2xl mb-12">
        <h2 className="text-2xl font-bold text-white mb-6">Ingest System Logs</h2>
        
        <input 
          type="file" 
          onChange={(e) => setFile(e.target.files[0])}
          className="block w-full text-sm text-gray-400 file:mr-4 file:py-3 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer mb-6 transition-all duration-200"
        />
        
        <button 
          onClick={handleUpload}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 text-white font-bold py-3 px-4 rounded-md transition-all duration-200 shadow-lg"
        >
          {loading ? "Llama 3 is analyzing logs..." : "Run AI Threat Analysis"}
        </button>
      </div>

      {/* Dynamic AI Alert Card (Only shows up if 'report' has data) */}
      {report && (
        <div className="max-w-3xl w-full bg-slate-800 p-8 rounded-xl border border-red-500/50 shadow-2xl shadow-red-900/20 animate-fade-in">
          
          <div className="flex items-center justify-between mb-8 border-b border-slate-700 pb-6">
            <h2 className="text-3xl font-bold text-red-400">{report.incident_title}</h2>
            <span className="px-4 py-1 bg-red-900/40 text-red-400 rounded-full font-bold uppercase tracking-wider text-sm border border-red-700/50">
              {report.severity} SEVERITY
            </span>
          </div>
          
          <div className="grid grid-cols-1 gap-6">
            <div className="bg-slate-900 p-5 rounded-lg border border-slate-700 shadow-inner">
              <h3 className="text-blue-400 font-bold uppercase text-xs mb-2 tracking-widest">MITRE ATT&CK Technique</h3>
              <p className="text-white text-lg font-semibold">{report.mitre_attack_technique}</p>
            </div>
            
            <div className="bg-slate-900 p-5 rounded-lg border border-slate-700 shadow-inner">
              <h3 className="text-blue-400 font-bold uppercase text-xs mb-2 tracking-widest">AI Analyst Explanation</h3>
              <p className="text-gray-300 text-base leading-relaxed">{report.explanation}</p>
            </div>
            
            <div className="bg-slate-900 p-5 rounded-lg border border-slate-700 shadow-inner">
              <h3 className="text-emerald-400 font-bold uppercase text-xs mb-2 tracking-widest">Remediation Steps</h3>
              <p className="text-gray-300 text-base leading-relaxed">{report.remediation_steps}</p>
            </div>
          </div>

        </div>
      )}
    </div>
  )
}

export default App