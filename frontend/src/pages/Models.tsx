import { useState, useEffect } from 'react'
import api from '../api/client'
import { Plus, Zap } from 'lucide-react'

export default function Models() {
  const [providers, setProviders] = useState<any[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ provider_type: 'ark', name: '', api_key: '', base_url: '', available_models: '' })

  const fetch = async () => {
    const res: any = await api.get('/model-providers')
    if (res.code === 0) setProviders(res.data)
  }

  useEffect(() => { fetch() }, [])

  const handleCreate = async () => {
    const models = form.available_models.split(',').map(s => s.trim()).filter(Boolean)
    const res: any = await api.post('/model-providers', { ...form, available_models: models })
    if (res.code === 0) { setShowCreate(false); fetch() }
  }

  const handleTest = async (id: number) => {
    const res: any = await api.post(`/model-providers/${id}/test`)
    if (res.code === 0) { alert('连接测试成功'); fetch() }
    else alert(res.message)
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">模型配置</h2>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-1 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700">
          <Plus className="w-4 h-4" /> 添加供应商
        </button>
      </div>
      <div className="grid gap-4">
        {providers.map((p) => (
          <div key={p.id} className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="font-medium text-lg">{p.name}</span>
                <span className="ml-2 text-xs px-2 py-0.5 bg-gray-100 rounded">{p.provider_type === 'ark' ? '火山引擎 ARK' : 'OpenAI'}</span>
                <span className={`ml-2 text-xs px-2 py-0.5 rounded ${p.status === 'available' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{p.status === 'available' ? '可用' : '不可用'}</span>
              </div>
              <button onClick={() => handleTest(p.id)} className="flex items-center gap-1 px-3 py-1 border rounded-md text-sm hover:bg-primary-50"><Zap className="w-4 h-4" /> 测试连接</button>
            </div>
            <div className="text-sm text-gray-500">API Key: {p.api_key_masked}</div>
            {p.base_url && <div className="text-sm text-gray-500">Base URL: {p.base_url}</div>}
            <div className="mt-2">
              <span className="text-sm text-gray-500">可用模型：</span>
              {(p.available_models || []).map((m: string) => (
                <span key={m} className="ml-2 inline-block px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded">{m}</span>
              ))}
            </div>
          </div>
        ))}
        {providers.length === 0 && <div className="text-center text-gray-400 py-8">暂无模型供应商</div>}
      </div>
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowCreate(false)}>
          <div className="bg-white rounded-lg p-6 w-96" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">添加模型供应商</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">类型</label>
                <select value={form.provider_type} onChange={(e) => setForm({...form, provider_type: e.target.value})} className="w-full px-3 py-2 border rounded-md">
                  <option value="ark">火山引擎 ARK</option>
                  <option value="openai">OpenAI</option>
                </select>
              </div>
              <div><label className="block text-sm font-medium mb-1">名称</label><input value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} className="w-full px-3 py-2 border rounded-md" /></div>
              <div><label className="block text-sm font-medium mb-1">API Key</label><input type="password" value={form.api_key} onChange={(e) => setForm({...form, api_key: e.target.value})} className="w-full px-3 py-2 border rounded-md" /></div>
              <div><label className="block text-sm font-medium mb-1">Base URL（可选）</label><input value={form.base_url} onChange={(e) => setForm({...form, base_url: e.target.value})} className="w-full px-3 py-2 border rounded-md" /></div>
              <div><label className="block text-sm font-medium mb-1">可用模型（逗号分隔）</label><input value={form.available_models} onChange={(e) => setForm({...form, available_models: e.target.value})} className="w-full px-3 py-2 border rounded-md" placeholder="doubao-pro-32k, doubao-lite-32k" /></div>
            </div>
            <div className="flex gap-2 justify-end mt-4">
              <button onClick={() => setShowCreate(false)} className="px-4 py-2 border rounded-md text-sm">取消</button>
              <button onClick={handleCreate} className="px-4 py-2 bg-primary-600 text-white rounded-md text-sm">添加</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
