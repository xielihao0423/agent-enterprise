import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  Bot, Cpu, Wrench, BookOpen, Brain, MessageSquare,
  Settings, ScrollText, LogOut, Menu
} from 'lucide-react'

const navItems = [
  { to: '/agents', label: 'Agent 管理', icon: Bot },
  { to: '/chat', label: '对话', icon: MessageSquare },
  { to: '/sessions', label: 'Session', icon: Settings },
  { to: '/models', label: '模型配置', icon: Cpu },
  { to: '/skills', label: 'Skill 库', icon: Wrench },
  { to: '/knowledge-bases', label: '知识库', icon: BookOpen },
  { to: '/memory', label: '记忆管理', icon: Brain },
  { to: '/feishu-bots', label: '飞书机器人', icon: MessageSquare },
  { to: '/audit', label: '审计与监控', icon: ScrollText },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  if (!user) {
    navigate('/login')
    return null
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-60 bg-slate-900 text-white flex flex-col">
        <div className="p-4 border-b border-slate-700">
          <h1 className="text-lg font-bold">Agent 平台</h1>
          <p className="text-xs text-slate-400 mt-1">企业级管理台</p>
        </div>
        <nav className="flex-1 overflow-y-auto py-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                  isActive
                    ? 'bg-primary-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-700">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-300">{user.username}</span>
            <button onClick={() => { logout(); navigate('/login') }} className="text-slate-400 hover:text-white">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
