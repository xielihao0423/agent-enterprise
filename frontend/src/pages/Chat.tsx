import { useState, useEffect, useRef } from 'react'
import api from '../api/client'
import { Send, Square, Play, Plus } from 'lucide-react'

export default function Chat() {
  const [agents, setAgents] = useState<any[]>([])
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null)
  const [sessions, setSessions] = useState<any[]>([])
  const [selectedSession, setSelectedSession] = useState<number | null>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const msgEndRef = useRef<HTMLDivElement>(null)

  const fetchAgents = async () => {
    const res: any = await api.get('/agents?status=active')
    if (res.code === 0) { setAgents(res.data.items); if (res.data.items.length > 0) setSelectedAgent(res.data.items[0].id) }
  }

  const fetchSessions = async () => {
    if (!selectedAgent) return
    const res: any = await api.get(`/agents/${selectedAgent}/sessions`)
    if (res.code === 0) setSessions(res.data.items)
  }

  const fetchMessages = async () => {
    if (!selectedSession) return
    const res: any = await api.get(`/sessions/${selectedSession}/messages`)
    if (res.code === 0) setMessages(res.data.items)
  }

  useEffect(() => { fetchAgents() }, [])
  useEffect(() => { fetchSessions() }, [selectedAgent])
  useEffect(() => { fetchMessages() }, [selectedSession])
  useEffect(() => { msgEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleNewSession = async () => {
    if (!selectedAgent) return
    const res: any = await api.post(`/agents/${selectedAgent}/sessions`, { source: 'web', chat_type: 'single' })
    if (res.code === 0) { setSelectedSession(res.data.id); fetchSessions() }
  }

  const handleSend = async () => {
    if (!input.trim() || !selectedSession) return
    setSending(true)
    const userMsg = { id: 0, role: 'user', content: input, created_at: new Date().toISOString() }
    const msg = input
    setMessages(prev => [...prev, userMsg])
    setInput('')
    try {
      const res: any = await api.post(`/sessions/${selectedSession}/messages`, { content: msg })
      if (res.code === 0) {
        // Reload persisted history so the assistant turn is authoritative.
        await fetchMessages()
      } else {
        // Keep the error bubble in the local list so the failure is visible.
        setMessages(prev => [...prev, { id: 0, role: 'error', content: res.message || '消息发送失败', created_at: new Date().toISOString() }])
      }
    } catch (err: any) {
      const message = err?.response?.data?.message || err?.message || '网络错误，消息发送失败'
      setMessages(prev => [...prev, { id: 0, role: 'error', content: message, created_at: new Date().toISOString() }])
    } finally {
      setSending(false)
    }
  }

  const handleInterrupt = async () => {
    await api.post(`/sessions/${selectedSession}/interrupt`)
    fetchMessages()
  }

  const handleResume = async () => {
    await api.post(`/sessions/${selectedSession}/resume`)
    fetchMessages()
  }

  const currentSession = sessions.find(s => s.id === selectedSession)

  return (
    <div className="flex h-screen">
      {/* Session sidebar */}
      <div className="w-64 bg-white border-r flex flex-col">
        <div className="p-3 border-b">
          <select value={selectedAgent || ''} onChange={(e) => { setSelectedAgent(Number(e.target.value)); setSelectedSession(null) }} className="w-full border rounded px-2 py-1.5 text-sm">
            {agents.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
        </div>
        <div className="p-2">
          <button onClick={handleNewSession} className="w-full flex items-center justify-center gap-1 py-2 border-2 border-dashed rounded-md text-sm text-gray-500 hover:bg-gray-50"><Plus className="w-4 h-4" /> 新建对话</button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {sessions.map(s => (
            <div key={s.id} onClick={() => setSelectedSession(s.id)} className={`px-3 py-2 cursor-pointer text-sm border-b ${selectedSession === s.id ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50'}`}>
              <div className="font-medium">Session #{s.id}</div>
              <div className="text-xs text-gray-400">{s.message_count} 条消息 · {s.status}</div>
            </div>
          ))}
        </div>
      </div>
      {/* Chat area */}
      <div className="flex-1 flex flex-col">
        {selectedSession ? (
          <>
            <div className="p-3 border-b flex items-center justify-between">
              <span className="text-sm font-medium">Session #{selectedSession}</span>
              <div className="flex gap-2">
                {currentSession?.status === 'running' && <button onClick={handleInterrupt} className="flex items-center gap-1 px-3 py-1 border rounded text-sm text-yellow-600 hover:bg-yellow-50"><Square className="w-3 h-3" /> 中断</button>}
                {currentSession?.status === 'interrupted' && <button onClick={handleResume} className="flex items-center gap-1 px-3 py-1 border rounded text-sm text-green-600 hover:bg-green-50"><Play className="w-3 h-3" /> 续跑</button>}
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[70%] px-4 py-2 rounded-lg ${
                    m.role === 'user' ? 'bg-primary-600 text-white'
                    : m.role === 'error' ? 'bg-red-50 text-red-700 border border-red-200'
                    : 'bg-gray-100 text-gray-800'
                  }`}>
                    <div className="text-xs opacity-60 mb-1">{m.role === 'user' ? '用户' : m.role === 'error' ? '错误' : 'Agent'}</div>
                    <div className="text-sm whitespace-pre-wrap">{m.content}</div>
                  </div>
                </div>
              ))}
              {sending && <div className="flex justify-start"><div className="bg-gray-100 px-4 py-2 rounded-lg text-sm text-gray-400">思考中...</div></div>}
              <div ref={msgEndRef} />
            </div>
            <div className="p-4 border-t">
              <div className="flex gap-2">
                <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !sending) handleSend() }} placeholder="输入消息..." className="flex-1 px-4 py-2 border rounded-md" disabled={sending} />
                <button onClick={handleSend} disabled={sending || !input.trim()} className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"><Send className="w-4 h-4" /></button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400"><div className="text-center"><p className="mb-2">选择一个 Session 或创建新对话</p><button onClick={handleNewSession} className="px-4 py-2 bg-primary-600 text-white rounded-md">新建对话</button></div></div>
        )}
      </div>
    </div>
  )
}
