import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  const [selectedIncident, setSelectedIncident] = useState(null);

  // FIXED: Pointing to your live Render backend for history
  const fetchHistory = async () => {
    try {
      const response = await fetch("https://secpilot-ai-r2ff.onrender.com/api/logs/history");
      const data = await response.json();
      if (data.status === "success") {
        setHistory(data.data.reverse());
      }
    } catch (error) {
      console.error("Failed to fetch history:", error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first!");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      // FIXED: Pointing to your live Render backend with the correct upload endpoint
      const response = await fetch("https://secpilot-ai-r2ff.onrender.com/api/logs/upload", {
        method: "POST",
        body: formData,
      });
      
      const rawText = await response.text();
      console.log("Raw Server Output:", rawText);
      
      const data = JSON.parse(rawText);
      setReport(data.ai_analysis);
      
      fetchHistory();
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Failed to analyze log. Check the console.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans flex flex-col items-center">
      {/* Header */}
      <h1 className="text-4xl font-extrabold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
        SecPilot AI
      </h1>
      <p className="text-gray-400 mb-8">Automated SOC Analyst & Threat Detection Engine</p>

      {/* Upload Section */}
      <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700 w-full max-w-2xl flex flex-col items-center">
        <input 
          type="file" 
          onChange={(e) => setFile(e.target.files[0])}
          className="mb-4 block w-full text-sm text-gray-400
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-600 file:text-white
            hover:file:bg-blue-700 transition-all"
        />
        <button 
          onClick={handleUpload}
          disabled={loading}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 px-6 py-2 rounded-full font-bold transition-all disabled:opacity-50"
        >
          {loading ? "Analyzing Threat Engine..." : "Run AI Threat Analysis"}
        </button>
      </div>

      {/* Main Alert Card (Current Upload) */}
      {report && (
        <div className="mt-8 bg-red-900/20 border border-red-500/50 p-6 rounded-xl w-full max-w-2xl shadow-2xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-red-400">🚨 {report.incident_title}</h2>
            <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm font-bold animate-pulse">
              {report.severity}
            </span>
          </div>
          
          <div className="space-y-4">
            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <span className="text-gray-400 text-sm font-bold uppercase tracking-wider">MITRE ATT&CK Technique</span>
              <p className="text-blue-400 font-mono mt-1">{report.mitre_attack_technique}</p>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <span className="text-gray-400 text-sm font-bold uppercase tracking-wider">AI Explanation</span>
              <p className="text-gray-200 mt-1">{report.explanation}</p>
            </div>

            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700 border-l-4 border-l-green-500">
              <span className="text-gray-400 text-sm font-bold uppercase tracking-wider">Recommended Remediation</span>
              <p className="text-green-400 mt-1 font-semibold">{report.remediation_steps}</p>
            </div>
          </div>
        </div>
      )}

      {/* Persistent Incident History Dashboard */}
      {history.length > 0 && (
        <div className="mt-16 w-full max-w-5xl">
          <h2 className="text-2xl font-bold text-gray-300 mb-6 border-b border-gray-700 pb-2">
            Database History (Past Incidents)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {history.map((incident) => (
              <div 
                key={incident.id} 
                className="bg-gray-800 p-5 rounded-xl border border-gray-700 shadow-md flex flex-col justify-between hover:border-gray-400 hover:bg-gray-700 transition-all cursor-pointer transform hover:-translate-y-1"
                onClick={() => setSelectedIncident(incident)}
              >
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-bold text-red-400 leading-tight">{incident.incident_title}</h3>
                    <span className={`text-xs font-bold px-2 py-1 rounded ml-2 ${
                      incident.severity === 'CRITICAL' || incident.severity === 'HIGH' ? 'bg-red-600 text-white' : 'bg-yellow-600 text-white'
                    }`}>
                      {incident.severity}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 font-mono mb-3 truncate">File: {incident.filename}</p>
                  <p className="text-sm text-gray-300 line-clamp-3 mb-4">{incident.explanation}</p>
                </div>
                <div className="text-xs font-mono text-blue-400 bg-gray-900 p-2 rounded">
                  {incident.mitre_attack_technique}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* --- INCIDENT MODAL POPUP --- */}
      {selectedIncident && (
        <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center p-4 z-50 transition-opacity">
          <div className="bg-gray-800 border border-gray-600 rounded-xl p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl text-white">
            <div className="flex justify-between items-start mb-4 border-b border-gray-700 pb-4">
              <h2 className="text-2xl font-bold text-red-500">
                {selectedIncident.incident_title}
              </h2>
              <span className={`text-sm font-bold px-3 py-1 rounded-full ${
                selectedIncident.severity === 'CRITICAL' || selectedIncident.severity === 'HIGH' ? 'bg-red-600 text-white' : 'bg-yellow-600 text-white'
              }`}>
                {selectedIncident.severity}
              </span>
            </div>
            
            <div className="mb-6 bg-gray-900 p-4 rounded-lg font-mono text-sm border border-gray-700">
              <span className="text-gray-400 font-bold block mb-1">MITRE Technique:</span> 
              <span className="text-blue-400">{selectedIncident.mitre_attack_technique}</span> 
              <br/><br/>
              <span className="text-gray-400 font-bold block mb-1">Log File:</span> 
              <span className="text-gray-300">{selectedIncident.filename}</span>
            </div>
            
            <div className="mb-6">
              <h3 className="font-bold text-lg text-gray-300 uppercase tracking-wider mb-2">In-Depth Analysis</h3>
              <p className="whitespace-pre-wrap text-gray-300 leading-relaxed bg-gray-900 p-4 rounded-lg border border-gray-700">
                {selectedIncident.explanation}
              </p>
            </div>
            
            <div className="mb-6 border-l-4 border-l-green-500 pl-4 bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="font-bold text-lg text-gray-300 uppercase tracking-wider mb-2">Remediation Steps</h3>
              <p className="whitespace-pre-wrap text-green-400 leading-relaxed font-semibold">
                {selectedIncident.remediation_steps}
              </p>
            </div>
            
            <button 
              className="mt-6 bg-gray-700 text-white px-6 py-3 rounded-full font-bold hover:bg-red-600 w-full transition-colors border border-gray-500 shadow-lg"
              onClick={() => setSelectedIncident(null)}
            >
              Close Detailed Report
            </button>
          </div>
        </div>
      )}

    </div>
  )
}

export default App