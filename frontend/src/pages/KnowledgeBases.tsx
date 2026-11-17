import { useState, useEffect } from 'react'
import api from '../api/client'
import { Plus, Upload, FileText } from 'lucide-react'

export default function KnowledgeBases() {
  const [kbs, setKbs] = useState<any[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [newDesc, setNewDesc] = useState('')
  const [selectedKb, setSelectedKb] = useState<number | null>(null)
  const [documents, setDocuments] = useState<any[]>([])

  const fetch = async () => {
    const res: any = await api.get('/knowledge-bases')
    if (res.code === 0) setKbs(res.data)
  }

  useEffect(() => { fetch() }, [])

  const handleCreate = async () => {
    const res: any = await api.post('/knowledge-bases', { name: newName, description: newDesc })
    if (res.code === 0) { setShowCreate(false); fetch() }
  }

  const fetchDocs = async (kbId: number) => {
    setSelectedKb(kbId)
    const res: any = await api.get(`/knowledge-bases/${kbId}/documents`)
    if (res.code === 0) setDocuments(res.data)
  }

  const handleUpload = async (kbId: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const res: any = await api.post(`/knowledge-bases/${kbId}/documents`, formData)
    if (res.code === 0) fetchDocs(kbId)
  }

  const statusLabels: Record<string, string> = { uploading: '上传中', parsing: '解析中', indexing: '索引中', ready: '已就绪', failed: '失败' }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">知识库</h2>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-1 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"><Plus className="w-4 h-4" /> 创建知识库</button>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {kbs.map(kb => (
          <div key={kb.id} className="bg-white rounded-lg shadow p-4 cursor-pointer hover:shadow-md" onClick={() => fetchDocs(kb.id)}>
            <div className="flex items-center gap-2 mb-1"><FileText className="w-4 h-4 text-primary-500" /><span className="font-medium">{kb.name}</span></div>
            <p className="text-sm text-gray-500">{kb.description || '-'}</p>
            <p className="text-xs text-gray-400 mt-2">{kb.document_count} 篇文档</p>
          </div>
        ))}
        {kbs.length === 0 && <div className="col-span-3 text-center text-gray-400 py-8">暂无知识库</div>}
      </div>
      {selectedKb && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedKb(null)}>
          <div className="bg-white rounded-lg p-6 w-2/3 max-h-[80vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">文档列表</h3>
            <div className="mb-4">
              <label className="flex items-center gap-2 px-4 py-2 border-2 border-dashed rounded-md cursor-pointer hover:bg-gray-50">
                <Upload className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-500">上传文档（PDF, TXT, Markdown, DOCX）</span>
                <input type="file" className="hidden" onChange={(e) => { if (e.target.files?.[0]) handleUpload(selectedKb, e.target.files[0]) }} />
              </label>
            </div>
            <table className="w-full">
              <thead className="bg-gray-50 border-b"><tr><th className="px-4 py-2 text-left text-xs">文件名</th><th className="px-4 py-2 text-left text-xs">大小</th><th className="px-4 py-2 text-left text-xs">状态</th></tr></thead>
              <tbody className="divide-y">
                {documents.map(d => (
                  <tr key={d.id}>
                    <td className="px-4 py-2 text-sm">{d.filename}</td>
                    <td className="px-4 py-2 text-sm text-gray-500">{(d.file_size / 1024).toFixed(1)} KB</td>
                    <td className="px-4 py-2"><span className={`text-xs px-2 py-0.5 rounded ${d.status === 'ready' ? 'bg-green-100 text-green-700' : d.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>{statusLabels[d.status] || d.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
            <button onClick={() => setSelectedKb(null)} className="mt-4 w-full py-2 border rounded-md text-sm">关闭</button>
          </div>
        </div>
      )}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowCreate(false)}>
          <div className="bg-white rounded-lg p-6 w-96" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">创建知识库</h3>
            <div className="mb-3"><label className="block text-sm font-medium mb-1">名称</label><input value={newName} onChange={(e) => setNewName(e.target.value)} className="w-full px-3 py-2 border rounded-md" /></div>
            <div className="mb-3"><label className="block text-sm font-medium mb-1">描述</label><textarea value={newDesc} onChange={(e) => setNewDesc(e.target.value)} className="w-full px-3 py-2 border rounded-md" rows={3} /></div>
            <div className="flex gap-2 justify-end"><button onClick={() => setShowCreate(false)} className="px-4 py-2 border rounded-md text-sm">取消</button><button onClick={handleCreate} className="px-4 py-2 bg-primary-600 text-white rounded-md text-sm">创建</button></div>
          </div>
        </div>
      )}
    </div>
  )
}
