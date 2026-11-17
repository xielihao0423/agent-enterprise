import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Login from './pages/Login'
import Layout from './components/Layout'
import Agents from './pages/Agents'
import AgentDetail from './pages/AgentDetail'
import Models from './pages/Models'
import Skills from './pages/Skills'
import KnowledgeBases from './pages/KnowledgeBases'
import Memory from './pages/Memory'
import FeishuBots from './pages/FeishuBots'
import Sessions from './pages/Sessions'
import SessionDetail from './pages/SessionDetail'
import Chat from './pages/Chat'
import Audit from './pages/Audit'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/agents" replace />} />
            <Route path="agents" element={<Agents />} />
            <Route path="agents/:id" element={<AgentDetail />} />
            <Route path="models" element={<Models />} />
            <Route path="skills" element={<Skills />} />
            <Route path="knowledge-bases" element={<KnowledgeBases />} />
            <Route path="memory" element={<Memory />} />
            <Route path="feishu-bots" element={<FeishuBots />} />
            <Route path="sessions" element={<Sessions />} />
            <Route path="sessions/:id" element={<SessionDetail />} />
            <Route path="chat" element={<Chat />} />
            <Route path="audit" element={<Audit />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
