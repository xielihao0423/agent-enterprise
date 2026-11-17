import { useState, useEffect } from 'react'
import api from '../api/client'

export default function Audit() {
  const [tab, setTab] = useState(0)
  const [logs, setLogs] = useState<any[]>([])
  const [tokenData, setTokenData] = useState<any>(null)
  const [errorData, setErrorData] = useState<any>(null)

  const fetchLogs = async () => {
    const res: any = await api.get('/audit-logs')
    if (res.code === 0) setLogs(res.data.items)
  }

  const fetchToken = async () => {
    const res: any = await api.get('/metrics/token-usage')
    if (res.code === 0) setTokenData(res.data)
  }

  const fetchErrors = async () => {
    const res: any = await api.get('/metrics/errors')
    if (res.code === 0) setErrorData(res.data)
  }

  useEffect(() => { fetchLogs() }, [])

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">审计与监控</h2>
      <div className="flex gap-1 border-b mb-4">
        {['审计日志', 'Token 用量', '错误监控'].map((t, i) => (
          <button key={t} onClick={() => { setTab(i); if (i === 0) fetchLogs(); if (i === 1) fetchToken(); if (i === 2) fetchErrors() }} className={`px-4 py-2 text-sm font-medium border-b-2 ${tab === i ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500'}`}>{t}</button>
        ))}
      </div>
      {tab === 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b"><tr><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作人</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">目标</th><th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th></tr></thead>
            <tbody className="divide-y divide-gray-200">
              {logs.map(l => (<tr key={l.id} className="hover:bg-gray-50"><td className="px-4 py-3 text-sm">{l.operator || '-'}</td><td className="px-4 py-3 text-sm">{l.action}</td><td className="px-4 py-3 text-sm">{l.target_type} #{l.target_id}</td><td className="px-4 py-3 text-sm text-gray-500">{l.created_at?.slice(0, 19).replace('T', ' ') || '-'}</td></tr>))}
              {logs.length === 0 && <tr><td colSpan={4} className="text-center py-8 text-gray-400">暂无审计日志</td></tr>}
            </tbody>
          </table>
        </div>
      )}
      {tab === 1 && <div className="bg-white rounded-lg shadow p-8 text-center text-gray-400">暂无 Token 用量数据</div>}
      {tab === 2 && <div className="bg-white rounded-lg shadow p-8 text-center text-gray-400">暂无错误记录</div>}
    </div>
  )
}
