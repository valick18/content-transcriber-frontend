import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function App() {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState('idle'); // idle, downloading, splitting, transcribing, done, error, queued
  const [jobId, setJobId] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [question, setQuestion] = useState('');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [view, setView] = useState('home'); // home, result
  const chatEndRef = useRef(null);

  // Load history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('transcription_history');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  // Save to localStorage whenever a job completes
  const saveToHistory = (jobData) => {
    const newHistory = [jobData, ...history];
    setHistory(newHistory);
    localStorage.setItem('transcription_history', JSON.stringify(newHistory));
  };

  const deleteHistoryItem = (e, id) => {
    e.stopPropagation();
    if (!confirm('Delete this transcript?')) return;
    const newHistory = history.filter(item => item.id !== id);
    setHistory(newHistory);
    localStorage.setItem('transcription_history', JSON.stringify(newHistory));
    if (jobId === id) {
      handleBack();
    }
  };

  useEffect(() => {
    let interval;
    if (jobId && status !== 'done' && status !== 'error') {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_URL}/status/${jobId}`);
          setStatus(res.data.status);
          if (res.data.status === 'done') {
            const resultRes = await axios.get(`${API_URL}/result/${jobId}`);
            setTranscript(resultRes.data.transcript);
            // Save to localStorage history
            saveToHistory({
              id: jobId,
              status: 'done',
              title: url || 'Uploaded File',
              date: new Date().toLocaleDateString()
            });
          } else if (res.data.status === 'error') {
            alert('Error processing video');
          }
        } catch (err) {
          console.error(err);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [jobId, status]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;
    setStatus('queued');
    setView('result');
    try {
      const res = await axios.post(`${API_URL}/process`, { url });
      setJobId(res.data.job_id);
    } catch (err) {
      console.error(err);
      setStatus('error');
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setStatus('queued');
    setView('result');

    try {
      const res = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setJobId(res.data.job_id);
    } catch (err) {
      console.error(err);
      setStatus('error');
      alert("Upload failed");
    }
  };

  const loadHistoryItem = async (item) => {
    if (item.status !== 'done') return;
    setJobId(item.id);
    setStatus('done');
    setView('result');
    try {
      const res = await axios.get(`${API_URL}/result/${item.id}`);
      setTranscript(res.data.transcript);
    } catch (err) {
      console.error(err);
    }
  };

  const handleBack = () => {
    setView('home');
    setUrl('');
    setStatus('idle');
    setJobId(null);
    setTranscript('');
    setChatHistory([]);
    setIsChatOpen(false);
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!question || isChatLoading) return;

    const newHistory = [...chatHistory, { role: 'user', content: question }];
    setChatHistory(newHistory);
    setQuestion('');
    setIsChatLoading(true);

    try {
      const res = await axios.post(`${API_URL}/chat`, { job_id: jobId, question });
      setChatHistory([...newHistory, { role: 'assistant', content: res.data.answer }]);
    } catch (err) {
      console.error(err);
      setChatHistory([...newHistory, { role: 'assistant', content: "Error getting response: " + (err.response?.data?.detail || err.message) }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isChatLoading]);

  return (
    <div className="app-container">
      <header className="header">
        {view === 'result' && (
          <button className="back-btn" onClick={handleBack}>←</button>
        )}
        <div className="header-content">
          <h1>Content Transcriber</h1>
          <p className="subtitle">Automatically transcribe audio or video content</p>
        </div>
      </header>

      <main className="main-content">
        {view === 'home' && (
          <>
            <div className="input-section">
              <form onSubmit={handleSubmit}>
                <input
                  type="text"
                  placeholder="Paste Link..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="url-input"
                />
                <button type="submit" className="primary-btn">
                  Start Transcription
                </button>
              </form>

              <div className="divider">
                <span>OR</span>
              </div>

              <div className="upload-section">
                <input
                  type="file"
                  id="file-upload"
                  accept="video/*,audio/*"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                />
                <label htmlFor="file-upload" className="upload-btn">
                  📂 Upload File from Device
                </label>
              </div>
            </div>

            <div className="history-section">
              <h3>Recent Transcripts</h3>
              {history.length === 0 ? (
                <p className="empty-text">No history yet.</p>
              ) : (
                <div className="history-list">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      className="history-item"
                      onClick={() => loadHistoryItem(item)}
                    >
                      <div className="history-info">
                        <span className="history-title">{item.title}</span>
                        <span className={`history-status ${item.status}`}>{item.status}</span>
                      </div>
                      <button
                        className="delete-btn"
                        onClick={(e) => deleteHistoryItem(e, item.id)}
                      >
                        🗑️
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {view === 'result' && (
          <>
            {status !== 'idle' && status !== 'done' && (
              <div className="loading-section">
                <div className="loader"></div>
                <p className="status-text">Processing: {status}...</p>
              </div>
            )}

            {status === 'done' && (
              <div className="result-section">
                <div className="transcript-header">
                  <h2>Full Transcript</h2>
                  <button
                    className="copy-btn"
                    onClick={() => navigator.clipboard.writeText(transcript)}
                  >
                    📋 Copy
                  </button>
                </div>
                <div className="transcript-container">
                  <p className="transcript-text">{transcript}</p>
                </div>

                <button
                  className="fab-chat"
                  onClick={() => setIsChatOpen(!isChatOpen)}
                >
                  💬 Ask AI
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {isChatOpen && (
        <div className="chat-overlay">
          <div className="chat-header">
            <h3>Content Assistant</h3>
            <button onClick={() => setIsChatOpen(false)}>✕</button>
          </div>
          <div className="chat-messages">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {isChatLoading && (
              <div className="message assistant typing">
                <span>●</span><span>●</span><span>●</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          <form onSubmit={handleChatSubmit} className="chat-input-form">
            <input
              type="text"
              placeholder="Ask about the content..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={isChatLoading}
            />
            <button type="submit" disabled={isChatLoading}>Send</button>
          </form>
        </div>
      )}
    </div>
  );
}

export default App;
