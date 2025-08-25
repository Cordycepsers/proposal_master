import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Badge } from "./ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog"
import { proposalService, type Proposal } from '../services'
import { Plus, FileText, Calendar, CheckCircle, Clock, AlertTriangle, TrendingUp } from "lucide-react"
import { toast } from 'sonner'

export function ProposalManagement() {
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [newProposal, setNewProposal] = useState({
    title: '',
    requirements_ids: [] as string[]
  })

  useEffect(() => {
    fetchProposals()
  }, [])

  const fetchProposals = async () => {
    setLoading(true)
    try {
      const proposalsData = await proposalService.getProposals()
      setProposals(proposalsData)
      toast.success('Proposals loaded successfully')
    } catch (error) {
      console.error('Failed to fetch proposals:', error)
      toast.error('Failed to load proposals')
    } finally {
      setLoading(false)
    }
  }

  const createProposal = async () => {
    try {
      await proposalService.createProposal({
        title: newProposal.title,
        requirements_ids: newProposal.requirements_ids
      })
      toast.success('Proposal created successfully')
      setShowCreateDialog(false)
      setNewProposal({
        title: '',
        requirements_ids: []
      })
      await fetchProposals()
    } catch (error) {
      console.error('Failed to create proposal:', error)
      toast.error('Failed to create proposal')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'awarded':
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'submitted':
        return <Clock className="w-4 h-4 text-blue-500" />
      case 'in_progress':
      case 'in progress':
        return <TrendingUp className="w-4 h-4 text-yellow-500" />
      case 'rejected':
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      default:
        return <FileText className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'awarded':
      case 'completed':
        return 'default'
      case 'submitted':
        return 'secondary'
      case 'in_progress':
      case 'in progress':
        return 'outline'
      case 'rejected':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  // Dashboard metrics
  const totalProposals = proposals.length
  const submittedProposals = proposals.filter(p => p.status?.toLowerCase() === 'submitted').length
  const completedProposals = proposals.filter(p => 
    p.status?.toLowerCase() === 'awarded' || p.status?.toLowerCase() === 'completed'
  ).length

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-3xl font-bold tracking-tight">Proposal Management</h2>
        </div>
        <div className="text-center py-10">Loading proposals...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold tracking-tight">Proposal Management</h2>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Proposal
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Create New Proposal</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Title</label>
                <Input
                  value={newProposal.title}
                  onChange={(e) => setNewProposal({ ...newProposal, title: e.target.value })}
                  placeholder="Proposal title"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={createProposal}>
                  Create Proposal
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Dashboard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Proposals</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalProposals}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Submitted</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{submittedProposals}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completedProposals}</div>
          </CardContent>
        </Card>
      </div>

      {/* Proposals List */}
      <Card>
        <CardHeader>
          <CardTitle>All Proposals</CardTitle>
        </CardHeader>
        <CardContent>
          {proposals.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No proposals yet. Create your first proposal to get started.
            </div>
          ) : (
            <div className="space-y-4">
              {proposals.map((proposal) => (
                <div
                  key={proposal.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-center space-x-4 flex-1">
                    {getStatusIcon(proposal.status)}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium truncate">{proposal.title}</h3>
                      {proposal.summary && (
                        <p className="text-sm text-muted-foreground truncate">{proposal.summary}</p>
                      )}
                      <div className="flex items-center space-x-4 mt-1 text-xs text-muted-foreground">
                        {proposal.due_date && (
                          <span className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            {proposal.due_date}
                          </span>
                        )}
                        {proposal.client && <span>Client: {proposal.client}</span>}
                        {typeof proposal.progress === 'number' && <span>{proposal.progress}% complete</span>}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={getStatusBadgeVariant(proposal.status)}>
                      {proposal.status?.replace('_', ' ').toUpperCase() || 'DRAFT'}
                    </Badge>
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
