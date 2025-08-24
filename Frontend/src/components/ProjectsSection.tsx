import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table"
import { Badge } from "./ui/badge"
import { Progress } from "./ui/progress"
import { MetricCard } from "./MetricCard"
import { FolderOpen, Clock, CheckCircle, AlertCircle } from "lucide-react"

const projects = [
  {
    id: 1,
    name: "Website Redesign",
    client: "Tech Corp",
    status: "In Progress",
    priority: "High",
    progress: 75,
    dueDate: "2024-02-15",
    budget: "$25,000"
  },
  {
    id: 2,
    name: "Mobile App Development",
    client: "StartupXYZ",
    status: "Planning",
    priority: "Medium",
    progress: 25,
    dueDate: "2024-03-30",
    budget: "$45,000"
  },
  {
    id: 3,
    name: "Brand Identity",
    client: "Fashion Brand",
    status: "In Progress",
    priority: "Low",
    progress: 90,
    dueDate: "2024-01-20",
    budget: "$8,000"
  },
  {
    id: 4,
    name: "E-commerce Platform",
    client: "Retail Co",
    status: "Review",
    priority: "High",
    progress: 95,
    dueDate: "2024-01-10",
    budget: "$65,000"
  },
  {
    id: 5,
    name: "Marketing Campaign",
    client: "Local Business",
    status: "In Progress",
    priority: "Medium",
    progress: 60,
    dueDate: "2024-02-28",
    budget: "$12,000"
  }
]

const getStatusBadge = (status: string) => {
  const variants = {
    'In Progress': 'default',
    'Planning': 'secondary',
    'Review': 'outline',
    'Completed': 'default'
  } as const
  
  return <Badge variant={variants[status as keyof typeof variants] || 'secondary'}>{status}</Badge>
}

const getPriorityBadge = (priority: string) => {
  const colors = {
    'High': 'bg-red-100 text-red-800',
    'Medium': 'bg-yellow-100 text-yellow-800',
    'Low': 'bg-green-100 text-green-800'
  }
  
  return <Badge className={colors[priority as keyof typeof colors]}>{priority}</Badge>
}

export function ProjectsSection() {
  const totalProjects = projects.length
  const inProgressProjects = projects.filter(p => p.status === 'In Progress').length
  const completedProjects = projects.filter(p => p.progress === 100).length
  const overdueProjects = projects.filter(p => new Date(p.dueDate) < new Date()).length

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Projects"
          value={totalProjects.toString()}
          icon={FolderOpen}
        />
        <MetricCard
          title="In Progress"
          value={inProgressProjects.toString()}
          icon={Clock}
        />
        <MetricCard
          title="Completed"
          value={completedProjects.toString()}
          icon={CheckCircle}
        />
        <MetricCard
          title="Overdue"
          value={overdueProjects.toString()}
          changeType="negative"
          icon={AlertCircle}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Open Projects</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Project Name</TableHead>
                <TableHead>Client</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Progress</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Budget</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.map((project) => (
                <TableRow key={project.id}>
                  <TableCell className="font-medium">{project.name}</TableCell>
                  <TableCell>{project.client}</TableCell>
                  <TableCell>{getStatusBadge(project.status)}</TableCell>
                  <TableCell>{getPriorityBadge(project.priority)}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Progress value={project.progress} className="w-16" />
                      <span className="text-sm">{project.progress}%</span>
                    </div>
                  </TableCell>
                  <TableCell>{project.dueDate}</TableCell>
                  <TableCell>{project.budget}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}