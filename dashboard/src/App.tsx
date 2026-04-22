import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/common/Sidebar'
import Header from './components/common/Header'
import ChatPage from './pages/ChatPage'
import VoicePage from './pages/VoicePage'
import PipelinesPage from './pages/PipelinesPage'
import FlowBuilderPage from './pages/FlowBuilderPage'
import ProvidersPage from './pages/ProvidersPage'

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/voice" element={<VoicePage />} />
            <Route path="/pipelines" element={<PipelinesPage />} />
            <Route path="/flow-builder" element={<FlowBuilderPage />} />
            <Route path="/flow-builder/:id" element={<FlowBuilderPage />} />
            <Route path="/providers" element={<ProvidersPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
