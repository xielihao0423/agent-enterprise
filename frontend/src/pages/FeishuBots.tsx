import { useState, useEffect } from 'react'
import api from '../api/client'
import { Plus, Link2 } from 'lucide-react'

export default function FeishuBots() {
  const [bots, setBots] = useState<any[]>([])
  const [agents, setAgents] = useState<any[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', app_id: '', app_secret: '', connection_mode: 'long_polling' })

  const fetch = async () => {
    const [botRes, agentRes]: any = await Promise.all([api.get('/feishu-bots'), api.get('/agents')])
    if (botRes.code === 0) setBots(botRes.data)
    if (agentRes.code === 0) setAgents(agentRes.data.items)
  }

  useEffect(() => { fetch() }, [])

  const handleCreate = async () => {
    const res: any = await api.post('/feishu-bots', form)
    if (res.code === 0) { setShowCreate(false); fetch() }
  }

  const handleBind = async (botId: number, agentId: number) => {
    const res: any = await api.put(`/feishu-bots/${botId}/agent`, { agent_id: agentId })
    if (res.code === 0) { alert('绑定成功'); fetch() }
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">飞书机器人</h2>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-1 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"><Plus className="w-4 h-4" /> 创建机器人</button>
      </div>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b"><tr><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">名称</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">App ID</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">接入方式</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">绑定 Agent</th></tr></thead>
          <tbody className="divide-y divide-gray-200">
            {bots.map(b => (
              <tr key={b.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium">{b.name}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{b.app_id}</td>
                <td className="px-4 py-3 text-sm">{b.connection_mode === 'long_polling' ? '长连接' : 'Webhook'}</td>
                <td className="px-4 py-3"><span className={`text-xs px-2 py-0.5 rounded ${b.status === 'connected' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>{b.status === 'connected' ? '已连接' : '未连接'}</span></td>
                <td className="px-4 py-3">
                  <select value={b.agent_id || ''} onChange={(e) => handleBind(b.id, Number(e.target.value))} className="border rounded px-2 py-1 text-sm">
                    <option value="">未绑定</option>
                    {agents.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
                  </select>
                </td>
              </tr>
            ))}
            {bots.length === 0 && <tr><td colSpan={5} className="text-center py-8 text-gray-400">暂无飞书机器人</td></tr>}
          </tbody>
        </table>
      </div>
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowCreate(false)}>
          <div className="bg-white rounded-lg p-6 w-96" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">创建飞书机器人</h3>
            <div className="space-y-3">
              <div><label className="block text-sm font-medium mb-1">名称</label><input value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} className="w-full px-3 py-2 border rounded-md" /></div>
              <div><label className="block text-sm font-medium mb-1">App ID</label><input value={form.app_id} onChange={(e) => setForm({...form, app_id: e.target.value})} className="w-full px-3 py-2 border rounded-md" /></div>
              <div><label className="block text-sm font-medium mb-1">App Secret</label><input type="password" value={form.app_secret} onChange={(e) => setForm({...form, app_secret: e.target.value})} className="w-full px-3 py-2 border rounded-md" /></div>
              <div><label className="block text-sm font-medium mb-1">接入方式</label><select value={form.connection_mode} onChange={(e) => setForm({...form, connection_mode: e.target.value})} className="w-full px-3 py-2 border rounded-md"><option value="long_polling">长连接</option><option value="webhook">Webhook</option></select></div>
            </div>
            <div className="flex gap-2 justify-end mt-4"><button onClick={() => setShowCreate(false)} className="px-4 py-2 border rounded-md text-sm">取消</button><button onClick={handleCreate} className="px-4 py-2 bg-primary-600 text-white rounded-md text-sm">创建</button></div>
          </div>
        </div>
      )}
    </div>
  )
}
