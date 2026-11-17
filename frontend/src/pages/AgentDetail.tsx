import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'
import { ArrowLeft, Save, History, RotateCw } from 'lucide-react'

const FILE_TYPES = [
  { key: 'agent_md', label: 'Agent.md' },
  { key: 'user_md', label: 'USER.md' },
  { key: 'identity_md', label: 'IDENTITY.md' },
  { key: 'soul_md', label: 'SOUL.md' }
]

const TABS = ['角色文件', '模型', 'Skill', '知识库', '记忆', '飞书']

export default function AgentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [agent, setAgent] = useState<any>(null)
  const [activeTab, setActiveTab] = useState(0)
  const [activeFileType, setActiveFileType] = useState('agent_md')
  const [roleFiles, setRoleFiles] = useState<Record<string, any>>({})
  const [editingContent, setEditingContent] = useState('')
  const [versions, setVersions] = useState<any[]>([])
  const [showVersions, setShowVersions] = useState(false)
  const [modelBinding, setModelBinding] = useState<any>(null)
  const [providers, setProviders] = useState<any[]>([])
  const [skills, setSkills] = useState<any[]>([])
  const [allSkills, setAllSkills] = useState<any[]>([])
  const [kbs, setKbs] = useState<any[]>([])
  const [allKbs, setAllKbs] = useState<any[]>([])
  const [memConfig, setMemConfig] = useState<any>(null)
  const [feishuBot, setFeishuBot] = useState<any>(null)
  const [memories, setMemories] = useState<any[]>([])

  const fetchAgent = async () => {
    const res: any = await api.get(`/agents/${id}`)
    if (res.code === 0) setAgent(res.data)
  }

  const fetchRoleFiles = async () => {
    const res: any = await api.get(`/agents/${id}/role-files`)
    if (res.code === 0) {
      setRoleFiles(res.data)
      setEditingContent(res.data[activeFileType]?.content || '')
    }
  }

  const fetchVersions = async (ft: string) => {
    const res: any = await api.get(`/agents/${id}/role-files/${ft}/versions`)
    if (res.code === 0) setVersions(res.data)
  }

  const fetchModelBinding = async () => {
    const [provRes]: any = await Promise.all([
      api.get('/model-providers')
    ])
    if (provRes.code === 0) setProviders(provRes.data)
  }

  const fetchSkills = async () => {
    const [allRes]: any = await Promise.all([api.get('/skills')])
    if (allRes.code === 0) setAllSkills(allRes.data)
  }

  const fetchKbs = async () => {
    const res: any = await api.get('/knowledge-bases')
    if (res.code === 0) setAllKbs(res.data)
  }

  const fetchMemConfig = async () => {
    const res: any = await api.get(`/agents/${id}/memory-config`)
    if (res.code === 0) setMemConfig(res.data)
  }

  const fetchMemories = async () => {
    const res: any = await api.get(`/agents/${id}/memories`)
    if (res.code === 0) setMemories(res.data.items)
  }

  useEffect(() => { fetchAgent() }, [id])
  useEffect(() => {
    fetchRoleFiles()
    fetchModelBinding()
    fetchSkills()
    fetchKbs()
    fetchMemConfig()
    fetchMemories()
  }, [id])

  useEffect(() => {
    if (roleFiles[activeFileType]) setEditingContent(roleFiles[activeFileType].content)
  }, [activeFileType])

  const handleSaveRoleFile = async () => {
    const res: any = await api.put(`/agents/${id}/role-files/${activeFileType}`, { content: editingContent })
    if (res.code === 0) {
      alert('保存成功')
      fetchRoleFiles()
    }
  }

  const handleRestoreVersion = async (version: number) => {
    const res: any = await api.post(`/agents/${id}/role-files/${activeFileType}/versions/${version}/restore`)
    if (res.code === 0) {
      alert('恢复成功')
      fetchRoleFiles()
      setShowVersions(false)
    }
  }

  const handleBindModel = async (providerId: number, modelName: string) => {
    const res: any = await api.put(`/model-providers/agents/${id}/model`, {
      provider_id: providerId, model_name: modelName, temperature: 0.7, max_tokens: 4096, top_p: 0.9
    })
    if (res.code === 0) { alert('模型绑定成功'); setModelBinding(res.data) }
  }

  if (!agent) return <div className="p-6">加载中...</div>

  return (
    <div className="p-6">
      <div className="flex items-center gap-3 mb-4">
        <button onClick={() => navigate('/agents')} className="text-gray-500 hover:text-gray-700"><ArrowLeft className="w-5 h-5" /></button>
        <h2 className="text-xl font-bold">{agent.name}</h2>
        <span className={`px-2 py-1 text-xs rounded-full ${agent.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
          {agent.status === 'active' ? '已启用' : agent.status === 'draft' ? '草稿' : '已停用'}
        </span>
      </div>

      <div className="flex gap-1 border-b mb-4">
        {TABS.map((tab, i) => (
          <button key={tab} onClick={() => setActiveTab(i)}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${activeTab === i ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
            {tab}
          </button>
        ))}
      </div>

      {/* Tab: Role Files */}
      {activeTab === 0 && (
        <div>
          <div className="flex gap-2 mb-3">
            {FILE_TYPES.map(ft => (
              <button key={ft.key} onClick={() => { setActiveFileType(ft.key); fetchVersions(ft.key) }}
                className={`px-3 py-1.5 text-sm rounded-md ${activeFileType === ft.key ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
                {ft.label}
              </button>
            ))}
          </div>
          <div className="flex gap-2 mb-3">
            <button onClick={handleSaveRoleFile} className="flex items-center gap-1 px-3 py-1.5 bg-primary-600 text-white rounded-md text-sm"><Save className="w-4 h-4" /> 保存新版本</button>
            <button onClick={() => { fetchVersions(activeFileType); setShowVersions(true) }} className="flex items-center gap-1 px-3 py-1.5 border rounded-md text-sm"><History className="w-4 h-4" /> 版本历史</button>
          </div>
          <textarea value={editingContent} onChange={(e) => setEditingContent(e.target.value)} className="w-full h-96 p-3 border rounded-md font-mono text-sm" placeholder="输入角色文件内容（Markdown 格式）..." />
          {showVersions && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowVersions(false)}>
              <div className="bg-white rounded-lg p-6 w-96" onClick={(e) => e.stopPropagation()}>
                <h3 className="text-lg font-bold mb-4">版本历史 - {FILE_TYPES.find(f => f.key === activeFileType)?.label}</h3>
                <div className="space-y-2 max-h-80 overflow-y-auto">
                  {versions.map((v) => (
                    <div key={v.id} className="flex items-center justify-between p-2 border rounded">
                      <div>
                        <span className="font-medium">v{v.version}</span>
                        {v.is_current && <span className="ml-2 text-xs text-green-600">当前版本</span>}
                        <div className="text-xs text-gray-400">{v.created_at?.slice(0, 19).replace('T', ' ')}</div>
                      </div>
                      {!v.is_current && (
                        <button onClick={() => handleRestoreVersion(v.version)} className="text-primary-600 hover:underline text-sm flex items-center gap-1"><RotateCw className="w-3 h-3" /> 恢复</button>
                      )}
                    </div>
                  ))}
                </div>
                <button onClick={() => setShowVersions(false)} className="mt-4 w-full py-2 border rounded-md text-sm">关闭</button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab: Model */}
      {activeTab === 1 && (
        <div>
          {providers.length === 0 ? (
            <p className="text-gray-400">请先在「模型配置」页面添加模型供应商</p>
          ) : (
            <div>
              <p className="text-sm text-gray-500 mb-3">选择模型供应商和模型：</p>
              {providers.map((p) => (
                <div key={p.id} className="mb-3 p-4 border rounded-md">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{p.name} ({p.provider_type})</span>
                    <span className="text-xs text-gray-400">Key: {p.api_key_masked}</span>
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    {(p.available_models || []).map((m: string) => (
                      <button key={m} onClick={() => handleBindModel(p.id, m)}
                        className={`px-3 py-1 text-sm rounded border hover:bg-primary-50 ${modelBinding?.model_name === m ? 'border-primary-600 bg-primary-50 text-primary-600' : 'border-gray-300'}`}>
                        {m}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab: Skills */}
      {activeTab === 2 && (
        <div>
          <p className="text-sm text-gray-500 mb-3">已安装的 Skill：</p>
          <div className="space-y-2">
            {allSkills.map((s) => (
              <div key={s.id} className="flex items-center justify-between p-3 border rounded-md">
                <div>
                  <span className="font-medium">{s.name}</span>
                  <span className="ml-2 text-xs text-gray-400">v{s.version}</span>
                  <p className="text-sm text-gray-500">{s.description || '-'}</p>
                </div>
                <button onClick={async () => { const res: any = await api.post(`/agents/${id}/skills`, { skill_id: s.id }); if (res.code === 0) { alert('绑定成功') } }}
                  className="px-3 py-1 text-sm border rounded-md hover:bg-primary-50">绑定</button>
              </div>
            ))}
            {allSkills.length === 0 && <p className="text-gray-400">暂无已安装的 Skill</p>}
          </div>
        </div>
      )}

      {/* Tab: Knowledge Base */}
      {activeTab === 3 && (
        <div>
          <p className="text-sm text-gray-500 mb-3">可绑定的知识库：</p>
          <div className="space-y-2">
            {allKbs.map((kb) => (
              <div key={kb.id} className="flex items-center justify-between p-3 border rounded-md">
                <div>
                  <span className="font-medium">{kb.name}</span>
                  <span className="ml-2 text-xs text-gray-400">{kb.document_count} 篇文档</span>
                </div>
                <button onClick={async () => { const res: any = await api.post(`/agents/${id}/knowledge-bases`, { kb_id: kb.id, top_k: 3, similarity_threshold: 0.7 }); if (res.code === 0) alert('绑定成功') }}
                  className="px-3 py-1 text-sm border rounded-md hover:bg-primary-50">绑定</button>
              </div>
            ))}
            {allKbs.length === 0 && <p className="text-gray-400">暂无知识库</p>}
          </div>
        </div>
      )}

      {/* Tab: Memory */}
      {activeTab === 4 && (
        <div>
          {memConfig && (
            <div className="mb-4 p-4 border rounded-md">
              <h4 className="font-medium mb-3">记忆配置</h4>
              <div className="space-y-2">
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked={memConfig.agent_scope_enabled} onChange={async (e) => { setMemConfig({...memConfig, agent_scope_enabled: e.target.checked}); await api.put(`/agents/${id}/memory-config`, { agent_scope_enabled: e.target.checked }) }} />
                  <span className="text-sm">Agent 级记忆（跨所有会话共享）</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked={memConfig.user_scope_enabled} onChange={async (e) => { setMemConfig({...memConfig, user_scope_enabled: e.target.checked}); await api.put(`/agents/${id}/memory-config`, { user_scope_enabled: e.target.checked }) }} />
                  <span className="text-sm">用户级记忆（跨会话，按用户隔离）</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked={memConfig.session_scope_enabled} onChange={async (e) => { setMemConfig({...memConfig, session_scope_enabled: e.target.checked}); await api.put(`/agents/${id}/memory-config`, { session_scope_enabled: e.target.checked }) }} />
                  <span className="text-sm">会话级记忆（仅当前会话）</span>
                </label>
                <div className="flex items-center gap-2 mt-3">
                  <span className="text-sm">写入策略：</span>
                  <select value={memConfig.write_strategy} onChange={async (e) => { setMemConfig({...memConfig, write_strategy: e.target.value}); await api.put(`/agents/${id}/memory-config`, { write_strategy: e.target.value }) }} className="border rounded px-2 py-1 text-sm">
                    <option value="auto">自动写入</option>
                    <option value="manual">手动写入</option>
                  </select>
                </div>
              </div>
            </div>
          )}
          <div>
            <h4 className="font-medium mb-2">记忆条目</h4>
            <div className="space-y-1">
              {memories.map((m) => (
                <div key={m.id} className="flex items-center justify-between p-2 border rounded text-sm">
                  <div><span className="text-xs text-gray-400 mr-2">[{m.scope}]</span>{m.content}</div>
                  <button onClick={async () => { await api.delete(`/agents/${id}/memories/${m.id}`); fetchMemories() }} className="text-red-400 hover:text-red-600 text-xs">删除</button>
                </div>
              ))}
              {memories.length === 0 && <p className="text-gray-400 text-sm">暂无记忆条目</p>}
            </div>
          </div>
        </div>
      )}

      {/* Tab: Feishu */}
      {activeTab === 5 && (
        <div>
          <p className="text-sm text-gray-500 mb-3">飞书机器人绑定状态：</p>
          {feishuBot ? (
            <div className="p-4 border rounded-md">
              <p>机器人名称：{feishuBot.name}</p>
              <p>App ID：{feishuBot.app_id}</p>
              <p>状态：{feishuBot.status}</p>
            </div>
          ) : (
            <p className="text-gray-400">该 Agent 尚未绑定飞书机器人，请前往「飞书机器人」页面配置</p>
          )}
        </div>
      )}
    </div>
  )
}
