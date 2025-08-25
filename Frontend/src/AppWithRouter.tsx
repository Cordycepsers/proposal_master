import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AppProvider } from './contexts/AppContext'
import { DashboardLayout } from './components/DashboardLayout'
import { OverviewSection } from './components/OverviewSection'
import { ProposalManagement } from './components/ProposalManagement'
import { DocumentManagement } from './components/DocumentManagement'
import { ResearchSection } from './components/ResearchSection'

export default function App() {
  return (
    <AppProvider>
      <Router>
        <div className="flex h-screen bg-background">
          <Routes>
            <Route path="/" element={<Navigate to="/overview" replace />} />
            <Route path="/overview" element={<DashboardLayout><OverviewSection /></DashboardLayout>} />
            <Route path="/proposals" element={<DashboardLayout><ProposalManagement /></DashboardLayout>} />
            <Route path="/documents" element={<DashboardLayout><DocumentManagement /></DashboardLayout>} />
            <Route path="/research" element={<DashboardLayout><ResearchSection /></DashboardLayout>} />
            <Route path="*" element={<Navigate to="/overview" replace />} />
          </Routes>
        </div>
        <Toaster position="top-right" richColors />
      </Router>
    </AppProvider>
  )
}
