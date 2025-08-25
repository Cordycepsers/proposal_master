import { BarChart3, FileText, TrendingUp, Home, Upload } from "lucide-react"
import { Button } from "./ui/button"
import { SectionType } from "../contexts/AppContext"

interface DashboardSidebarProps {
  activeSection: SectionType
  onSectionChange: (section: SectionType) => void
}

export function DashboardSidebar({ activeSection, onSectionChange }: DashboardSidebarProps) {
  const navItems: Array<{ id: SectionType; label: string; icon: any }> = [
    { id: 'overview', label: 'Overview', icon: Home },
    { id: 'projects', label: 'Proposals', icon: BarChart3 },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'research', label: 'Research', icon: TrendingUp },
  ]

  return (
    <div className="w-72 h-full bg-sidebar border-r border-sidebar-border">
      <div className="p-8">
        <div className="mb-8">
          <h2 className="text-sidebar-foreground text-xl font-medium tracking-tight">
            Proposal Master
          </h2>
          <p className="text-sidebar-foreground/70 text-sm mt-2">
            AI-powered proposal management system for RFP analysis and response automation
          </p>
        </div>
        
        <nav className="space-y-3">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = activeSection === item.id
            return (
              <Button
                key={item.id}
                variant={isActive ? "default" : "ghost"}
                className={`w-full justify-start h-12 px-4 ${
                  isActive 
                    ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-sm" 
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                }`}
                onClick={() => onSectionChange(item.id)}
              >
                <Icon className="mr-3 h-5 w-5" />
                <span className="font-medium">{item.label}</span>
              </Button>
            )
          })}
        </nav>

        <div className="mt-12 p-4 bg-sidebar-accent rounded-lg">
          <h4 className="text-sidebar-accent-foreground font-medium mb-2">Need Help?</h4>
          <p className="text-sidebar-accent-foreground/80 text-sm mb-3">
            Our support team is here to assist you with any questions.
          </p>
          <Button 
            size="sm" 
            className="bg-sidebar-primary hover:bg-sidebar-primary/90 text-sidebar-primary-foreground"
          >
            Contact Support
          </Button>
        </div>
      </div>
    </div>
  )
}