import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/client'

export default function SessionDetail() {
  const { id } = useParams()
  const [session, setSession] = useState<any>(null)
  const [messages, setMessages] = useState<any[]>([])

  const fetch = async () => {
    const [sRes, mRes]: any = await Promise.all([
      api.get(`/sessions/${id}`),
      api.get(`/sessions/${id}/messages`)
    ])
    if (sRes.code === 0) setSession(sRes.data)
    if (mRes.code === 0) setMessages(mRes.data.items)
  }

  useEffect(() => { fetch() }, [id])

  if (!session) return <div className="p-6">加载中...</div>

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Session #{session.id}</h2>
      <div className="mb-4 flex gap-4 text-sm">
        <span>Agent ID: {session.agent_id}</span>
        <span>来源: {session.source === 'feishu' ? '飞书' : 'Web'}</span>
        <span>状态: {session.status}</span>
        <span>创建时间: {session.created_at?.slice(0, 19).replace('T', ' ')}</span>
      </div>
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium mb-3">消息历史</h3>
        <div className="space-y-3 max-h-[60vh] overflow-y-auto">
          {messages.map(m => (
            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[70%] px-4 py-2 rounded-lg ${m.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                <div className="text-xs opacity-60 mb-1">{m.role === 'user' ? '用户' : m.role === 'assistant' ? 'Agent' : 'Tool'} · {m.created_at?.slice(11, 19)}</div>
                <div className="text-sm whitespace-pre-wrap">{m.content}</div>
                {m.token_usage > 0 && <div className="text-xs opacity-50 mt-1">Tokens: {m.token_usage}</div>}
              </div>
            </div>
          ))}
          {messages.length === 0 && <div className="text-center text-gray-400 py-8">暂无消息</div>}
        </div>
      </div>
    </div>
  )
}
