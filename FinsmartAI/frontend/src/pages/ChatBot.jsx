import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import {
  Send, User, Bot, AlertCircle, Paperclip, X,
  FileText, CheckCircle, MessageSquare, Hash
} from 'lucide-react';

const QUICK_ACTIONS_GENERAL = [
  'What is SIP and how does it work?',
  'Explain mutual funds vs stocks',
  'How to start investing in India?',
  'I earn 80000, spent 15000 rent, 5000 food',
];

const QUICK_ACTIONS_DOC = [
  'Summarize this document',
  'What are the key financial highlights?',
  'What risks are mentioned?',
  'What are the main recommendations?',
];

const USER_ID = crypto.randomUUID();

export default function ChatBot() {
  const [messages, setMessages] = useState([{
    role: 'assistant',
    text: "Hello! I'm **FinSmart AI**.\n\n- **General mode** — ask any finance question or share income & expenses\n- **Document mode** — upload a PDF, TXT, or CSV to query its contents",
  }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  const [sessionId, setSessionId] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const processFile = async (file) => {
    if (!file) return;
    const allowed = ['application/pdf', 'text/plain', 'text/csv'];
    const allowedExt = ['.pdf', '.txt', '.csv'];
    const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowed.includes(file.type) && !allowedExt.includes(ext)) {
      pushMsg('error', `Unsupported file type. Please upload PDF, TXT, or CSV.`);
      return;
    }
    setUploading(true);
    pushMsg('system', `Uploading **${file.name}**…`);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', USER_ID);
    try {
      const res = await axios.post('http://localhost:8000/api/rag/ingest', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const { session_id, chunks_ingested } = res.data;
      setSessionId(session_id);
      setUploadedFileName(file.name);
      pushMsg('success', `**${file.name}** indexed (${chunks_ingested} chunks). Ask questions about this document.`);
    } catch (err) {
      pushMsg('error', `Upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleFileInput = (e) => { const f = e.target.files?.[0]; if (f) processFile(f); e.target.value = ''; };
  const handleDrop = useCallback((e) => { e.preventDefault(); setIsDragging(false); const f = e.dataTransfer.files?.[0]; if (f) processFile(f); }, []);
  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = () => setIsDragging(false);
  const clearDocument = () => { setSessionId(null); setUploadedFileName(null); pushMsg('system', 'Document cleared. Back to General Finance mode.'); };

  const pushMsg = (role, text) => setMessages(prev => [...prev, { role, text }]);

  const sendMessage = async (userMessage) => {
    if (!userMessage.trim()) return;
    setInput('');
    
    // Compute chat history from existing messages
    const validHistory = messages
      .filter(m => (m.role === 'user' || m.role === 'assistant') && m.text)
      .map(m => ({ role: m.role, text: m.text }));

    setMessages(prev => [...prev, { role: 'user', text: userMessage.trim() }]);
    setLoading(true);

    // ── Document / RAG path — Streaming ────────────────────────────────────────
    if (sessionId) {
      setMessages(prev => [...prev, { role: 'assistant', text: '' }]);
      try {
        const response = await fetch('http://localhost:8000/api/rag/query/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            question: userMessage.trim(), 
            user_id: USER_ID, 
            session_id: sessionId,
            chat_history: validHistory
          }),
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop();

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            const payload = line.slice(6).trim();
            if (payload === '[DONE]') break;

            try {
              const parsed = JSON.parse(payload);
              if (parsed.error) {
                setMessages(prev => {
                  const msgs = [...prev];
                  msgs[msgs.length - 1] = { role: 'error', text: `Streaming error: ${parsed.error}` };
                  return msgs;
                });
                break;
              }
              if (parsed.sources) {
                setMessages(prev => {
                  const msgs = [...prev];
                  const last = msgs[msgs.length - 1];
                  msgs[msgs.length - 1] = { ...last, text: last.text + (last.text ? '\n\n' : '') + `---\n*Sources: ${parsed.sources.join(' · ')}*\n\n` };
                  return msgs;
                });
              }
              if (parsed.chunk) {
                setMessages(prev => {
                  const msgs = [...prev];
                  const last = msgs[msgs.length - 1];
                  msgs[msgs.length - 1] = { ...last, text: last.text + parsed.chunk };
                  return msgs;
                });
              }
            } catch {
              // skip malformed
            }
          }
        }
      } catch (err) {
        setMessages(prev => {
          const msgs = [...prev];
          const last = msgs[msgs.length - 1];
          if (!last.text || last.text.includes('Sources:')) {
            msgs[msgs.length - 1] = { role: 'error', text: 'Failed to connect to AI engine. Please check the backend is running.' };
          }
          return msgs;
        });
      } finally {
        setLoading(false);
      }
      return;
    }

    // ── General Finance chat — SSE streaming ───────────────────────────────────
    // Add an empty assistant bubble that we'll fill incrementally
    setMessages(prev => [...prev, { role: 'assistant', text: '' }]);

    try {
      const response = await fetch('http://localhost:8000/api/finance_rag/query/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: userMessage.trim(),
          chat_history: validHistory
        }),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        // Keep the last incomplete line in buffer
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const payload = line.slice(6).trim();
          if (payload === '[DONE]') break;

          try {
            const { chunk, error } = JSON.parse(payload);
            if (error) {
              setMessages(prev => {
                const msgs = [...prev];
                msgs[msgs.length - 1] = { role: 'error', text: `Streaming error: ${error}` };
                return msgs;
              });
              break;
            }
            if (chunk) {
              // Append chunk to the last assistant bubble — no flicker, no full overwrite
              setMessages(prev => {
                const msgs = [...prev];
                const last = msgs[msgs.length - 1];
                msgs[msgs.length - 1] = { ...last, text: last.text + chunk };
                return msgs;
              });
            }
          } catch {
            // Malformed JSON chunk — skip silently
          }
        }
      }
    } catch (err) {
      // Fallback: if streaming totally fails, replace the empty bubble with an error
      setMessages(prev => {
        const msgs = [...prev];
        const last = msgs[msgs.length - 1];
        // If we got partial content already, keep it; otherwise show error
        if (!last.text) {
          msgs[msgs.length - 1] = {
            role: 'error',
            text: 'Failed to connect to AI engine. Please check the backend is running.',
          };
        }
        return msgs;
      });
    } finally {
      setLoading(false);
    }
  };


  const quickActions = sessionId ? QUICK_ACTIONS_DOC : QUICK_ACTIONS_GENERAL;

  const getBubbleStyle = (role) => {
    if (role === 'user') return {
      background: 'var(--emerald-dim)',
      color: '#fff',
      boxShadow: '0 2px 8px var(--emerald-glow)',
    };
    if (role === 'error') return {
      background: 'var(--red-glow-soft)',
      color: 'var(--red-400)',
      border: '1px solid rgba(239,68,68,0.2)',
    };
    if (role === 'success') return {
      background: 'var(--green-glow-soft)',
      color: 'var(--green-400)',
      border: '1px solid rgba(52,211,153,0.2)',
    };
    if (role === 'system') return {
      background: 'var(--ink-2)',
      color: 'var(--text-muted)',
      border: '1px solid var(--border-1)',
      fontStyle: 'italic',
    };
    return {
      background: 'var(--ink-2)',
      color: 'var(--text-primary)',
      border: '1px solid var(--border-2)',
    };
  };

  return (
    <div className="container page-wrapper" style={{
      height: 'calc(100vh - 20px)', display: 'flex', flexDirection: 'column',
      paddingTop: 'calc(var(--nav-h) + 1.5rem)', paddingBottom: '1.5rem',
    }}>

      {/* Header */}
      <div className="flex-between animate-fade-1" style={{ marginBottom: '1rem', gap: '1rem', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: 36, height: 36, borderRadius: 'var(--r-md)',
            background: 'var(--blue-glow-soft)', display: 'flex',
            alignItems: 'center', justifyContent: 'center', color: 'var(--blue-400)',
          }}>
            <MessageSquare size={18} strokeWidth={1.75} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, letterSpacing: '-0.02em' }}>
              Finance AI Chat
            </h1>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              {sessionId ? `Document mode — ${uploadedFileName}` : 'Powered by NVIDIA NIM · Llama 3'}
            </span>
          </div>
        </div>

        {sessionId && (
          <div className="badge badge-green" style={{ gap: '0.5rem' }}>
            <FileText size={11} /> Document Active
          </div>
        )}
      </div>

      {/* Upload bar */}
      <div className="animate-fade-2" style={{ marginBottom: '1rem' }}>
        {!sessionId ? (
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => !uploading && fileInputRef.current?.click()}
            style={{
              padding: '0.875rem 1.25rem',
              border: `1px dashed ${isDragging ? 'var(--blue-500)' : 'var(--border-2)'}`,
              borderRadius: 'var(--r-lg)',
              background: isDragging ? 'var(--blue-glow-soft)' : 'var(--ink-1)',
              cursor: uploading ? 'wait' : 'pointer',
              display: 'flex', alignItems: 'center', gap: '0.75rem',
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => { if (!isDragging) e.currentTarget.style.background = 'var(--ink-2)'; }}
            onMouseLeave={e => { if (!isDragging) e.currentTarget.style.background = 'var(--ink-1)'; }}
          >
            <div style={{
              width: 28, height: 28, borderRadius: 'var(--r-sm)',
              background: 'var(--ink-3)', display: 'flex',
              alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)',
            }}>
              <Paperclip size={14} />
            </div>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', flex: 1 }}>
              {uploading
                ? <strong style={{ color: 'var(--blue-400)' }}>Uploading & indexing into vector store…</strong>
                : isDragging
                  ? <strong style={{ color: 'var(--blue-400)' }}>Drop to index</strong>
                  : <><strong style={{ color: 'var(--text-primary)' }}>Upload document</strong> — PDF, TXT, or CSV · click or drag & drop</>
              }
            </span>
            <input ref={fileInputRef} type="file" accept=".pdf,.txt,.csv" style={{ display: 'none' }} onChange={handleFileInput} disabled={uploading} />
          </div>
        ) : (
          <div style={{
            padding: '0.875rem 1.25rem',
            background: 'var(--green-glow-soft)',
            border: '1px solid rgba(52,211,153,0.2)',
            borderRadius: 'var(--r-lg)',
            display: 'flex', alignItems: 'center', gap: '0.75rem',
          }}>
            <FileText size={15} color="var(--green-400)" />
            <span style={{ flex: 1, fontSize: '0.875rem', color: 'var(--green-400)', fontWeight: 600 }}>{uploadedFileName}</span>
            <CheckCircle size={15} color="var(--green-400)" />
            <button
              onClick={clearDocument}
              style={{
                background: 'none', border: 'none', cursor: 'pointer', padding: '0.25rem',
                color: 'var(--text-muted)', borderRadius: 'var(--r-sm)',
                display: 'flex', transition: 'color 0.15s',
              }}
              onMouseEnter={e => e.currentTarget.style.color = 'var(--red-400)'}
              onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
            >
              <X size={14} />
            </button>
          </div>
        )}
      </div>

      {/* Chat area */}
      <div className="animate-fade-3" style={{
        flex: 1,
        background: 'var(--ink-1)',
        border: '1px solid var(--border-1)',
        borderRadius: 'var(--r-xl)',
        display: 'flex', flexDirection: 'column',
        overflow: 'hidden', minHeight: 0,
      }}>

        {/* Messages */}
        <div style={{
          flex: 1, overflowY: 'auto',
          padding: '1.5rem', display: 'flex',
          flexDirection: 'column', gap: '1rem',
        }}>
          {messages.map((msg, i) => {
            if (msg.role === 'assistant' && !msg.text) return null;
            const isUser = msg.role === 'user';
            const isErr = msg.role === 'error';
            return (
              <div key={i} style={{
                display: 'flex', gap: '0.75rem',
                alignSelf: isUser ? 'flex-end' : 'flex-start',
                maxWidth: '82%',
                animation: 'fadeUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
              }}>
                {!isUser && (
                  <div style={{
                    width: 30, height: 30, borderRadius: '8px', flexShrink: 0,
                    background: isErr ? 'var(--red-glow-soft)' : 'var(--blue-glow-soft)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: isErr ? 'var(--red-400)' : 'var(--blue-400)',
                    marginTop: '2px',
                  }}>
                    {isErr ? <AlertCircle size={15} /> : <Bot size={15} strokeWidth={1.75} />}
                  </div>
                )}

                <div style={{
                  padding: '0.875rem 1.1rem',
                  borderRadius: isUser ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                  fontSize: '0.9rem', lineHeight: 1.65,
                  ...getBubbleStyle(msg.role),
                }}>
                  {isUser ? msg.text : (
                    <div className="chat-md">
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>
                  )}
                </div>

                {isUser && (
                  <div style={{
                    width: 30, height: 30, borderRadius: '8px', flexShrink: 0,
                    background: 'var(--ink-3)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: 'var(--text-secondary)', marginTop: '2px',
                  }}>
                    <User size={15} />
                  </div>
                )}
              </div>
            );
          })}

          {/* Typing indicator */}
          {loading && messages[messages.length - 1]?.text === '' && (
            <div style={{ display: 'flex', gap: '0.75rem', alignSelf: 'flex-start' }}>
              <div style={{ width: 30, height: 30, borderRadius: '8px', background: 'var(--blue-glow-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--blue-400)' }}>
                <Bot size={15} strokeWidth={1.75} />
              </div>
              <div style={{
                padding: '0.875rem 1.1rem',
                background: 'var(--ink-2)', border: '1px solid var(--border-2)',
                borderRadius: '14px 14px 14px 4px',
                display: 'flex', gap: '5px', alignItems: 'center',
              }}>
                {[0, 150, 300].map(d => (
                  <span key={d} style={{
                    width: 7, height: 7, borderRadius: '50%',
                    background: 'var(--text-muted)',
                    animation: `pulse-live 1s ease-in-out ${d}ms infinite`,
                    display: 'inline-block',
                  }} />
                ))}
              </div>
            </div>
          )}

          <div ref={endRef} />
        </div>

        {/* Quick actions */}
        {messages.length <= 1 && !loading && (
          <div style={{ padding: '0 1.5rem 0.75rem', display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {quickActions.map((q, i) => (
              <button
                key={i}
                onClick={() => sendMessage(q)}
                style={{
                  padding: '0.4rem 0.875rem',
                  background: 'var(--ink-2)',
                  border: '1px solid var(--border-2)',
                  borderRadius: '100px',
                  color: 'var(--text-secondary)',
                  fontSize: '0.8rem', cursor: 'pointer',
                  transition: 'all 0.15s', fontWeight: 500,
                  display: 'flex', alignItems: 'center', gap: '0.3rem',
                  fontFamily: 'var(--font-sans)',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--border-3)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-2)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
              >
                <Hash size={10} /> {q}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div style={{
          padding: '0.875rem 1.25rem',
          borderTop: '1px solid var(--border-1)',
          background: 'var(--ink-0)',
          borderRadius: '0 0 var(--r-xl) var(--r-xl)',
        }}>
          <form onSubmit={e => { e.preventDefault(); sendMessage(input); }} style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <input
              type="text"
              className="input-control"
              placeholder={sessionId ? `Ask about ${uploadedFileName}…` : 'Ask anything about finance…'}
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={loading}
              autoFocus
              style={{ flex: 1, height: '44px', borderRadius: 'var(--r-md)', fontSize: '0.9rem' }}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !input.trim()}
              style={{ height: '44px', width: '44px', padding: 0, borderRadius: '50%', flexShrink: 0 }}
            >
              {loading
                ? <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
                : <Send size={16} />
              }
            </button>
          </form>
        </div>
      </div>

      <style>{`
        .chat-md p { margin: 0 0 0.5rem; }
        .chat-md p:last-child { margin: 0; }
        .chat-md strong { color: var(--blue-400); font-weight: 600; }
        .chat-md h3 { font-size: 1rem; margin: 0.875rem 0 0.4rem; color: var(--text-primary); font-weight: 700; }
        .chat-md ul, .chat-md ol { padding-left: 1.25rem; margin: 0.4rem 0; }
        .chat-md li { margin-bottom: 0.2rem; font-size: 0.9rem; }
        .chat-md table { width: 100%; border-collapse: collapse; margin: 0.6rem 0; font-size: 0.875rem; }
        .chat-md th { background: rgba(75,122,255,0.08); color: var(--blue-400); padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--border-1); text-align: left; font-size: 0.8rem; font-weight: 700; }
        .chat-md td { padding: 0.45rem 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.03); font-family: var(--font-mono); font-size: 0.85rem; }
        .chat-md tr:last-child td { border-bottom: none; }
        .chat-md code { background: var(--ink-3); padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.85em; color: var(--amber-400); font-family: var(--font-mono); }
        .chat-md hr { border: none; border-top: 1px solid var(--border-1); margin: 1rem 0; }
        .chat-md em { color: var(--text-secondary); }
      `}</style>
    </div>
  );
}
