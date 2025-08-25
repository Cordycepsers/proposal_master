import React, { createContext, useContext, useState, ReactNode } from 'react'

export type SectionType = 'overview' | 'projects' | 'documents' | 'research'

interface AppContextType {
  activeSection: SectionType
  setActiveSection: (section: SectionType) => void
  getSectionTitle: (section?: SectionType) => string
  getSectionDescription: (section?: SectionType) => string
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export const useApp = (): AppContextType => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

interface AppProviderProps {
  children: ReactNode
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [activeSection, setActiveSection] = useState<SectionType>('overview')

  const getSectionTitle = (section: SectionType = activeSection): string => {
    switch (section) {
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

  const getSectionDescription = (section: SectionType = activeSection): string => {
    switch (section) {
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

  const value: AppContextType = {
    activeSection,
    setActiveSection,
    getSectionTitle,
    getSectionDescription,
  }

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}
