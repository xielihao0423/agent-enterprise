import { useState, useEffect } from 'react'
import api from '../api/client'
import { Trash2 } from 'lucide-react'

export default function Memory() {
  const [agents, setAgents] = useState<any[]>([])
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null)
  const [memories, setMemories] = useState<any[]>([])
  const [scopeFilter, setScopeFilter] = useState('')

  const fetchAgents = async () => {
    const res: any = await api.get('/agents')
    if (res.code === 0) { setAgents(res.data.items); if (res.data.items.length > 0) setSelectedAgent(res.data.items[0].id) }
  }

  const fetchMemories = async () => {
    if (!selectedAgent) return
    const params = scopeFilter ? `?scope=${scopeFilter}` : ''
    const res: any = await api.get(`/agents/${selectedAgent}/memories${params}`)
    if (res.code === 0) setMemories(res.data.items)
  }

  useEffect(() => { fetchAgents() }, [])
  useEffect(() => { fetchMemories() }, [selectedAgent, scopeFilter])

  const handleDelete = async (id: number) => {
    if (!selectedAgent) return
    await api.delete(`/agents/${selectedAgent}/memories/${id}`)
    fetchMemories()
  }

  const handleBatchDelete = async () => {
    if (!selectedAgent || !scopeFilter) return
    if (!confirm(`确认清理所有 ${scopeFilter} 级记忆？`)) return
    await api.delete(`/agents/${selectedAgent}/memories?scope=${scopeFilter}`)
    fetchMemories()
  }

  const scopeLabels: Record<string, string> = { agent: 'Agent 级', user: '用户级', session: '会话级' }

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">记忆管理</h2>
      <div className="flex gap-4 mb-4">
        <select value={selectedAgent || ''} onChange={(e) => setSelectedAgent(Number(e.target.value))} className="border rounded-md px-3 py-2 text-sm">
          {agents.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
        </select>
        <select value={scopeFilter} onChange={(e) => setScopeFilter(e.target.value)} className="border rounded-md px-3 py-2 text-sm">
          <option value="">全部作用域</option>
          <option value="agent">Agent 级</option>
          <option value="user">用户级</option>
          <option value="session">会话级</option>
        </select>
        {scopeFilter && <button onClick={handleBatchDelete} className="flex items-center gap-1 px-3 py-2 border border-red-300 text-red-600 rounded-md text-sm hover:bg-red-50"><Trash2 className="w-4 h-4" /> 批量清理</button>}
      </div>
      <div className="space-y-1">
        {memories.map(m => (
          <div key={m.id} className="flex items-center justify-between p-3 border rounded-md">
            <div><span className="text-xs px-2 py-0.5 bg-gray-100 rounded mr-2">{scopeLabels[m.scope] || m.scope}</span><span className="text-sm">{m.content}</span>{m.user_id && <span className="ml-2 text-xs text-gray-400">用户: {m.user_id}</span>}</div>
            <button onClick={() => handleDelete(m.id)} className="text-red-400 hover:text-red-600"><Trash2 className="w-4 h-4" /></button>
          </div>
        ))}
        {memories.length === 0 && <div className="text-center text-gray-400 py-8">暂无记忆条目</div>}
      </div>
    </div>
  )
}
