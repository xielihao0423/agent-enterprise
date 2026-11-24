import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

export default function Sessions() {
  const navigate = useNavigate()
  const [agents, setAgents] = useState<any[]>([])
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null)
  const [sessions, setSessions] = useState<any[]>([])

  const fetchAgents = async () => {
    const res: any = await api.get('/agents')
    if (res.code === 0) { setAgents(res.data.items); if (res.data.items.length > 0) setSelectedAgent(res.data.items[0].id) }
  }

  const fetchSessions = async () => {
    if (!selectedAgent) return
    const res: any = await api.get(`/agents/${selectedAgent}/sessions`)
    if (res.code === 0) setSessions(res.data.items)
  }

  useEffect(() => { fetchAgents() }, [])
  useEffect(() => { fetchSessions() }, [selectedAgent])

  const statusLabels: Record<string, string> = { idle: '空闲', running: '运行中', interrupted: '已中断', closed: '已关闭' }
  const statusColors: Record<string, string> = { idle: 'bg-gray-100 text-gray-700', running: 'bg-green-100 text-green-700', interrupted: 'bg-yellow-100 text-yellow-700', closed: 'bg-red-100 text-red-700' }

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Session 管理</h2>
      <div className="mb-4">
        <select value={selectedAgent || ''} onChange={(e) => setSelectedAgent(Number(e.target.value))} className="border rounded-md px-3 py-2 text-sm">
          {agents.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
        </select>
      </div>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b"><tr><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">来源</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">消息数</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">更新时间</th></tr></thead>
          <tbody className="divide-y divide-gray-200">
            {sessions.map(s => (
              <tr key={s.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => navigate(`/sessions/${s.id}`)}>
                <td className="px-4 py-3 text-sm">{s.id}</td>
                <td className="px-4 py-3 text-sm">{s.source === 'feishu' ? '飞书' : 'Web'}</td>
                <td className="px-4 py-3 text-sm">{s.chat_type === 'group' ? '群聊' : '单聊'}</td>
                <td className="px-4 py-3"><span className={`text-xs px-2 py-0.5 rounded ${statusColors[s.status]}`}>{statusLabels[s.status]}</span></td>
                <td className="px-4 py-3 text-sm">{s.message_count}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{s.updated_at?.slice(0, 19).replace('T', ' ') || '-'}</td>
              </tr>
            ))}
            {sessions.length === 0 && <tr><td colSpan={6} className="text-center py-8 text-gray-400">暂无 Session</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
