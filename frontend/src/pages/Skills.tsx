import { useState, useEffect } from 'react'
import api from '../api/client'
import { Plus } from 'lucide-react'

export default function Skills() {
  const [skills, setSkills] = useState<any[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', version: '1.0.0', source: '' })

  const fetch = async () => {
    const res: any = await api.get('/skills')
    if (res.code === 0) setSkills(res.data)
  }

  useEffect(() => { fetch() }, [])

  const handleCreate = async () => {
    const res: any = await api.post('/skills', form)
    if (res.code === 0) { setShowCreate(false); fetch() }
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Skill 库</h2>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-1 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700">
          <Plus className="w-4 h-4" /> 安装 Skill
        </button>
      </div>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">名称</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">描述</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">版本</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">来源</th></tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {skills.map(s => (
              <tr key={s.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium">{s.name}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{s.description || '-'}</td>
                <td className="px-4 py-3"><span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded">v{s.version}</span></td>
                <td className="px-4 py-3 text-sm text-gray-500">{s.source || '-'}</td>
              </tr>
            ))}
            {skills.length === 0 && <tr><td colSpan={4} className="text-center py-8 text-gray-400">暂无 Skill</td></tr>}
          </tbody>
        </table>
      </div>
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowCreate(false)}>
          <div className="bg-white rounded-lg p-6 w-96" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">安装 Skill</h3>
            <div className="space-y-3">
              <div><label className="block text-sm font-medium mb-1">名称</label><input value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} className="w-full px-3 py-2 border rounded-md" /></div>
              <div><label className="block text-sm font-medium mb-1">描述</label><input value={form.description} onChange={(e) => setForm({...form, description: e.target.value})} className="w-full px-3 py-2 border rounded-md" /></div>
              <div><label className="block text-sm font-medium mb-1">版本</label><input value={form.version} onChange={(e) => setForm({...form, version: e.target.value})} className="w-full px-3 py-2 border rounded-md" /></div>
              <div><label className="block text-sm font-medium mb-1">来源</label><input value={form.source} onChange={(e) => setForm({...form, source: e.target.value})} className="w-full px-3 py-2 border rounded-md" /></div>
            </div>
            <div className="flex gap-2 justify-end mt-4"><button onClick={() => setShowCreate(false)} className="px-4 py-2 border rounded-md text-sm">取消</button><button onClick={handleCreate} className="px-4 py-2 bg-primary-600 text-white rounded-md text-sm">安装</button></div>
          </div>
        </div>
      )}
    </div>
  )
}
