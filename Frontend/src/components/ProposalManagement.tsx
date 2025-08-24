import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Badge } from "./ui/badge"
import { Textarea } from "./ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog"
import { Plus, FileText, Calendar, User, Target, TrendingUp, CheckCircle, Clock, AlertTriangle } from "lucide-react"

// Mock API service for proposals
const mockProposalService = {
  async getProposals() {
    return {
      data: {
        proposals: [
          {
            id: "1",
            title: "Government IT Services Contract",
            status: "in_progress",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            document_id: "1",
            summary: "Comprehensive IT services proposal for federal government agency including cloud migration, cybersecurity, and ongoing support.",
            deadline: "2024-09-15",
            value: 2500000,
            probability: 75
          },
          {
            id: "2",
            title: "Healthcare Management System",
            status: "draft",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            document_id: "2",
            summary: "Custom healthcare management platform for regional hospital network.",
            deadline: "2024-08-30",
            value: 1200000,
            probability: 60
          },
          {
            id: "3",
            title: "Smart City Infrastructure",
            status: "submitted",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            summary: "IoT and data analytics platform for smart city initiatives.",
            deadline: "2024-07-20",
            value: 3800000,
            probability: 45
          }
        ],
        total: 3
      }
    }
  },

  async createProposal(data: any) {
    return {
      data: {
        proposal_id: Math.random().toString(36),
        title: data.title,
        status: "draft",
        message: "Proposal created successfully"
      }
    }
  }
}

interface Proposal {
  id: string
  title: string
  status: string
  created_at: string
  updated_at: string
  document_id?: string
  summary?: string
  deadline?: string
  value?: number
  probability?: number
}

export function ProposalManagement() {
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [newProposal, setNewProposal] = useState({
    title: '',
    summary: '',
    deadline: '',
    value: '',
    probability: ''
  })

  useEffect(() => {
    fetchProposals()
  }, [])

  const fetchProposals = async () => {
    setLoading(true)
    try {
      const response = await mockProposalService.getProposals()
      if (response.data) {
        setProposals(response.data.proposals)
      }
    } catch (error) {
      console.error('Failed to fetch proposals:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProposal = async () => {
    try {
      await mockProposalService.createProposal(newProposal)
      setShowCreateDialog(false)
      setNewProposal({ title: '', summary: '', deadline: '', value: '', probability: '' })
      await fetchProposals()
    } catch (error) {
      console.error('Failed to create proposal:', error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'submitted':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'in_progress':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'draft':
        return <FileText className="h-4 w-4 text-gray-500" />
      case 'won':
        return <Target className="h-4 w-4 text-green-600" />
      case 'lost':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      submitted: 'default',
      in_progress: 'secondary',
      draft: 'outline',
      won: 'default',
      lost: 'destructive'
    } as const
    
    return (
      <Badge variant={variants[status as keyof typeof variants] || 'outline'}>
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    )
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const totalValue = proposals.reduce((sum, proposal) => sum + (proposal.value || 0), 0)
  const averageProbability = proposals.length > 0 
    ? proposals.reduce((sum, proposal) => sum + (proposal.probability || 0), 0) / proposals.length 
    : 0

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Proposals</p>
                <p className="text-2xl font-bold">{proposals.length}</p>
              </div>
              <FileText className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Value</p>
                <p className="text-2xl font-bold">{formatCurrency(totalValue)}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg. Win Probability</p>
                <p className="text-2xl font-bold">{averageProbability.toFixed(1)}%</p>
              </div>
              <Target className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Proposals List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Active Proposals</CardTitle>
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  New Proposal
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                  <DialogTitle>Create New Proposal</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Title</label>
                    <Input
                      value={newProposal.title}
                      onChange={(e) => setNewProposal({ ...newProposal, title: e.target.value })}
                      placeholder="Enter proposal title"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Summary</label>
                    <Textarea
                      value={newProposal.summary}
                      onChange={(e) => setNewProposal({ ...newProposal, summary: e.target.value })}
                      placeholder="Brief description of the proposal"
                      rows={3}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium">Deadline</label>
                      <Input
                        type="date"
                        value={newProposal.deadline}
                        onChange={(e) => setNewProposal({ ...newProposal, deadline: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Estimated Value</label>
                      <Input
                        type="number"
                        value={newProposal.value}
                        onChange={(e) => setNewProposal({ ...newProposal, value: e.target.value })}
                        placeholder="0"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Win Probability (%)</label>
                    <Input
                      type="number"
                      value={newProposal.probability}
                      onChange={(e) => setNewProposal({ ...newProposal, probability: e.target.value })}
                      placeholder="0-100"
                      min="0"
                      max="100"
                    />
                  </div>
                  <div className="flex gap-2 pt-4">
                    <Button onClick={handleCreateProposal} className="flex-1">
                      Create Proposal
                    </Button>
                    <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <p>Loading proposals...</p>
            </div>
          ) : proposals.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No proposals yet</p>
              <p className="text-sm">Create your first proposal to get started</p>
            </div>
          ) : (
            <div className="space-y-4">
              {proposals.map((proposal) => (
                <div key={proposal.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getStatusIcon(proposal.status)}
                        <h4 className="font-medium">{proposal.title}</h4>
                        {getStatusBadge(proposal.status)}
                      </div>
                      
                      {proposal.summary && (
                        <p className="text-sm text-muted-foreground mb-3">
                          {proposal.summary}
                        </p>
                      )}

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        {proposal.deadline && (
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            <span>Due: {formatDate(proposal.deadline)}</span>
                          </div>
                        )}
                        {proposal.value && (
                          <div className="flex items-center gap-1">
                            <TrendingUp className="h-3 w-3" />
                            <span>Value: {formatCurrency(proposal.value)}</span>
                          </div>
                        )}
                        {proposal.probability && (
                          <div className="flex items-center gap-1">
                            <Target className="h-3 w-3" />
                            <span>Win Rate: {proposal.probability}%</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          <span>Updated: {formatDate(proposal.updated_at)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-2 ml-4">
                      <Button variant="outline" size="sm">
                        Edit
                      </Button>
                      <Button variant="outline" size="sm">
                        View
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
