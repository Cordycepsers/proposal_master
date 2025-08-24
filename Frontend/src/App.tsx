import { useState } from 'react'
import { DashboardSidebar } from './components/DashboardSidebar'
import { OverviewSection } from './components/OverviewSection'
import { ProposalManagement } from './components/ProposalManagement'
import { DocumentManagement } from './components/DocumentManagement'
import { ResearchSection } from './components/ResearchSection'

export default function App() {
  const [activeSection, setActiveSection] = useState('overview')

  const renderSection = () => {
    switch (activeSection) {
      case 'overview':
        return <OverviewSection />
      case 'projects':
        return <ProposalManagement />
      case 'documents':
        return <DocumentManagement />
      case 'research':
        return <ResearchSection />
      default:
        return <OverviewSection />
    }
  }

  const getSectionTitle = () => {
    switch (activeSection) {
      case 'overview':
        return 'Dashboard Overview'
      case 'projects':
        return 'Proposal Management'
      case 'documents':
        return 'Document Management'
      case 'research':
        return 'Market Research'
      default:
        return 'Dashboard Overview'
    }
  }

  const getSectionDescription = () => {
    switch (activeSection) {
      case 'overview':
        return 'Get a comprehensive view of your proposal system performance and key metrics'
      case 'projects':
        return 'Track and manage all your active proposals and RFP responses'
      case 'documents':
        return 'Upload, analyze, and manage RFP documents and requirements'
      case 'research':
        return 'Conduct market research and analyze industry trends for better proposals'
      default:
        return 'Get a comprehensive view of your business performance and key metrics'
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <DashboardSidebar activeSection={activeSection} onSectionChange={setActiveSection} />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-card/50 backdrop-blur-sm border-b border-border px-8 py-6">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">
              {getSectionTitle()}
            </h1>
            <p className="text-muted-foreground mt-1">
              {getSectionDescription()}
            </p>
          </div>
        </header>
        
        <main className="flex-1 overflow-auto p-8 bg-gradient-to-br from-background to-muted/20">
          {renderSection()}
        </main>
      </div>
    </div>
  )
}