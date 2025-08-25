import { ReactNode } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useApp, SectionType } from '../contexts/AppContext'
import { DashboardSidebar } from './DashboardSidebar'

interface DashboardLayoutProps {
  children: ReactNode
}

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { getSectionTitle, getSectionDescription, setActiveSection } = useApp()

  // Map URL paths to section types
  const pathToSection: Record<string, SectionType> = {
    '/overview': 'overview',
    '/proposals': 'projects',
    '/documents': 'documents',
    '/research': 'research'
  }

  // Get current section from URL
  const currentSection = pathToSection[location.pathname] || 'overview'

  // Handle section changes by navigating to appropriate URL
  const handleSectionChange = (section: SectionType) => {
    const sectionToPath: Record<SectionType, string> = {
      'overview': '/overview',
      'projects': '/proposals',
      'documents': '/documents',
      'research': '/research'
    }
    
    setActiveSection(section)
    navigate(sectionToPath[section])
  }

  return (
    <>
      <DashboardSidebar 
        activeSection={currentSection} 
        onSectionChange={handleSectionChange} 
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-card/50 backdrop-blur-sm border-b border-border px-8 py-6">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">
              {getSectionTitle(currentSection)}
            </h1>
            <p className="text-muted-foreground mt-1">
              {getSectionDescription(currentSection)}
            </p>
          </div>
        </header>
        
        <main className="flex-1 overflow-auto p-8 bg-gradient-to-br from-background to-muted/20">
          {children}
        </main>
      </div>
    </>
  )
}
