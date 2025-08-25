import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table"
import { Badge } from "./ui/badge"
import { MetricCard } from "./MetricCard"
import { Users, UserPlus, UserCheck, UserX } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const leads = [
  {
    id: 1,
    name: "Sarah Johnson",
    company: "TechStart Inc",
    email: "sarah@techstart.com",
    phone: "+1 (555) 123-4567",
    status: "Hot",
    source: "Website",
    value: "$50,000",
    lastContact: "2024-01-05"
  },
  {
    id: 2,
    name: "Mike Chen",
    company: "Growth Co",
    email: "mike@growthco.com",
    phone: "+1 (555) 987-6543",
    status: "Warm",
    source: "Referral",
    value: "$25,000",
    lastContact: "2024-01-03"
  },
  {
    id: 3,
    name: "Emily Davis",
    company: "Creative Agency",
    email: "emily@creative.com",
    phone: "+1 (555) 456-7890",
    status: "Cold",
    source: "Social Media",
    value: "$15,000",
    lastContact: "2023-12-28"
  },
  {
    id: 4,
    name: "David Wilson",
    company: "Enterprise Ltd",
    email: "david@enterprise.com",
    phone: "+1 (555) 321-0987",
    status: "Hot",
    source: "Email",
    value: "$75,000",
    lastContact: "2024-01-06"
  },
  {
    id: 5,
    name: "Lisa Thompson",
    company: "Startup Hub",
    email: "lisa@startuphub.com",
    phone: "+1 (555) 654-3210",
    status: "Qualified",
    source: "Website",
    value: "$30,000",
    lastContact: "2024-01-04"
  }
]

const leadsByMonth = [
  { month: 'Aug', new: 23, qualified: 12, converted: 5 },
  { month: 'Sep', new: 31, qualified: 18, converted: 8 },
  { month: 'Oct', new: 28, qualified: 15, converted: 6 },
  { month: 'Nov', new: 35, qualified: 21, converted: 9 },
  { month: 'Dec', new: 42, qualified: 25, converted: 11 },
  { month: 'Jan', new: 38, qualified: 23, converted: 10 },
]

const getStatusBadge = (status: string) => {
  const variants = {
    'Hot': 'bg-red-100 text-red-800',
    'Warm': 'bg-orange-100 text-orange-800',
    'Cold': 'bg-blue-100 text-blue-800',
    'Qualified': 'bg-green-100 text-green-800'
  }
  
  return <Badge className={variants[status as keyof typeof variants]}>{status}</Badge>
}

export function LeadsSection() {
  const totalLeads = leads.length
  const hotLeads = leads.filter(l => l.status === 'Hot').length
  const qualifiedLeads = leads.filter(l => l.status === 'Qualified').length
  const totalValue = leads.reduce((sum, lead) => sum + parseInt(lead.value.replace(/[$,]/g, '')), 0)

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Leads"
          value={totalLeads.toString()}
          icon={Users}
        />
        <MetricCard
          title="Hot Leads"
          value={hotLeads.toString()}
          icon={UserPlus}
        />
        <MetricCard
          title="Qualified"
          value={qualifiedLeads.toString()}
          icon={UserCheck}
        />
        <MetricCard
          title="Pipeline Value"
          value={`$${totalValue.toLocaleString()}`}
          icon={UserX}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Lead Pipeline</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={leadsByMonth}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="new" fill="var(--color-chart-1)" name="New Leads" />
                <Bar dataKey="qualified" fill="var(--color-chart-2)" name="Qualified" />
                <Bar dataKey="converted" fill="var(--color-chart-3)" name="Converted" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Leads</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Value</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {leads.slice(0, 5).map((lead) => (
                  <TableRow key={lead.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{lead.name}</div>
                        <div className="text-sm text-muted-foreground">{lead.company}</div>
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(lead.status)}</TableCell>
                    <TableCell>{lead.value}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Leads</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Company</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Value</TableHead>
                <TableHead>Last Contact</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {leads.map((lead) => (
                <TableRow key={lead.id}>
                  <TableCell className="font-medium">{lead.name}</TableCell>
                  <TableCell>{lead.company}</TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div>{lead.email}</div>
                      <div className="text-muted-foreground">{lead.phone}</div>
                    </div>
                  </TableCell>
                  <TableCell>{getStatusBadge(lead.status)}</TableCell>
                  <TableCell>{lead.source}</TableCell>
                  <TableCell>{lead.value}</TableCell>
                  <TableCell>{lead.lastContact}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}