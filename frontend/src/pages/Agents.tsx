import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { Plus, Search, Copy, Trash2, Power } from 'lucide-react'

interface Agent {
  id: number
  name: string
  description: string | null
  status: string
  created_at: string | null
}

const statusLabels: Record<string, string> = {
  draft: '草稿',
  active: '已启用',
  inactive: '已停用',
  deleted: '已删除'
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  active: 'bg-green-100 text-green-700',
  inactive: 'bg-yellow-100 text-yellow-700',
  deleted: 'bg-red-100 text-red-700'
}

export default function Agents() {
  const navigate = useNavigate()
  const [agents, setAgents] = useState<Agent[]>([])
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [newDesc, setNewDesc] = useState('')

  const fetchAgents = async () => {
    const params = new URLSearchParams()
    if (statusFilter !== 'all') params.set('status', statusFilter)
    if (search) params.set('name', search)
    const res: any = await api.get(`/agents?${params}`)
    if (res.code === 0) setAgents(res.data.items)
  }

  useEffect(() => { fetchAgents() }, [statusFilter, search])

  const handleCreate = async () => {
    const res: any = await api.post('/agents', { name: newName, description: newDesc })
    if (res.code === 0) {
      setShowCreate(false)
      setNewName('')
      setNewDesc('')
      fetchAgents()
    }
  }

  const handleDuplicate = async (id: number) => {
    const res: any = await api.post(`/agents/${id}/duplicate`)
    if (res.code === 0) fetchAgents()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确认删除该 Agent？')) return
    const res: any = await api.delete(`/agents/${id}`)
    if (res.code === 0) fetchAgents()
  }

  const handleToggleStatus = async (id: number, current: string) => {
    const newStatus = current === 'active' ? 'inactive' : 'active'
    const res: any = await api.patch(`/agents/${id}/status`, { status: newStatus })
    if (res.code === 0) fetchAgents()
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Agent 管理</h2>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-1 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700">
          <Plus className="w-4 h-4" /> 创建 Agent
        </button>
      </div>
      <div className="flex gap-4 mb-4">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索 Agent 名称..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm"
          />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="border border-gray-300 rounded-md px-3 py-2 text-sm">
          <option value="all">全部状态</option>
          <option value="draft">草稿</option>
          <option value="active">已启用</option>
          <option value="inactive">已停用</option>
        </select>
      </div>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">名称</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">描述</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">创建时间</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {agents.length === 0 ? (
              <tr><td colSpan={5} className="text-center py-8 text-gray-400">暂无 Agent，点击右上角创建</td></tr>
            ) : agents.map(a => (
              <tr key={a.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => navigate(`/agents/${a.id}`)}>
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{a.name}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{a.description || '-'}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 text-xs rounded-full ${statusColors[a.status]}`}>{statusLabels[a.status]}</span></td>
                <td className="px-4 py-3 text-sm text-gray-500">{a.created_at?.slice(0, 19).replace('T', ' ') || '-'}</td>
                <td className="px-4 py-3 text-right" onClick={(e) => e.stopPropagation()}>
                  <div className="flex justify-end gap-2">
                    <button onClick={() => handleToggleStatus(a.id, a.status)} title="启停" className="text-gray-400 hover:text-primary-600"><Power className="w-4 h-4" /></button>
                    <button onClick={() => handleDuplicate(a.id)} title="复制" className="text-gray-400 hover:text-primary-600"><Copy className="w-4 h-4" /></button>
                    <button onClick={() => handleDelete(a.id)} title="删除" className="text-gray-400 hover:text-red-600"><Trash2 className="w-4 h-4" /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowCreate(false)}>
          <div className="bg-white rounded-lg p-6 w-96" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">创建 Agent</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">名称 *</label>
              <input type="text" value={newName} onChange={(e) => setNewName(e.target.value)} className="w-full px-3 py-2 border rounded-md" placeholder="输入 Agent 名称" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">描述</label>
              <textarea value={newDesc} onChange={(e) => setNewDesc(e.target.value)} className="w-full px-3 py-2 border rounded-md" rows={3} placeholder="输入描述（可选）" />
            </div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowCreate(false)} className="px-4 py-2 border rounded-md text-sm">取消</button>
              <button onClick={handleCreate} className="px-4 py-2 bg-primary-600 text-white rounded-md text-sm">创建</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
