import { MetricCard } from "./MetricCard"
import { DashboardChatbot } from "./DashboardChatbot"
import { RecentActivity } from "./RecentActivity"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { FolderOpen, Users, TrendingUp, DollarSign } from "lucide-react"

const monthlyData = [
  { month: 'Jan', projects: 12, leads: 45, revenue: 85000 },
  { month: 'Feb', projects: 15, leads: 52, revenue: 92000 },
  { month: 'Mar', projects: 18, leads: 38, revenue: 78000 },
  { month: 'Apr', projects: 22, leads: 61, revenue: 105000 },
  { month: 'May', projects: 25, leads: 73, revenue: 118000 },
  { month: 'Jun', projects: 28, leads: 69, revenue: 112000 },
]

const leadsBySource = [
  { name: 'Website', value: 35, color: '#7a8f63' },
  { name: 'Referrals', value: 25, color: '#9bb380' },
  { name: 'Social Media', value: 20, color: '#5a6b47' },
  { name: 'Email', value: 15, color: '#b8c9a3' },
  { name: 'Other', value: 5, color: '#6d7f5a' },
]

export function OverviewSection() {
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Projects"
          value="28"
          change="+12% from last month"
          changeType="positive"
          icon={FolderOpen}
        />
        <MetricCard
          title="Total Leads"
          value="247"
          change="+5% from last month"
          changeType="positive"
          icon={Users}
        />
        <MetricCard
          title="Conversion Rate"
          value="24.8%"
          change="-2% from last month"
          changeType="negative"
          icon={TrendingUp}
        />
        <MetricCard
          title="Revenue"
          value="$112,000"
          change="+8% from last month"
          changeType="positive"
          icon={DollarSign}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="border-0 shadow-sm bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg font-semibold">Monthly Trends</CardTitle>
            <p className="text-sm text-muted-foreground">Projects and leads performance over time</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis 
                  dataKey="month" 
                  stroke="var(--color-muted-foreground)"
                  fontSize={12}
                />
                <YAxis 
                  stroke="var(--color-muted-foreground)"
                  fontSize={12}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'var(--color-card)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                  }}
                />
                <Line type="monotone" dataKey="projects" stroke="var(--color-chart-1)" strokeWidth={3} dot={{ fill: 'var(--color-chart-1)', strokeWidth: 2, r: 4 }} />
                <Line type="monotone" dataKey="leads" stroke="var(--color-chart-2)" strokeWidth={3} dot={{ fill: 'var(--color-chart-2)', strokeWidth: 2, r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg font-semibold">Lead Sources</CardTitle>
            <p className="text-sm text-muted-foreground">Distribution of incoming leads by channel</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={leadsBySource}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  stroke="var(--color-background)"
                  strokeWidth={2}
                >
                  {leadsBySource.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'var(--color-card)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="border-0 shadow-sm bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg font-semibold">Revenue Trend</CardTitle>
            <p className="text-sm text-muted-foreground">Last 4 months performance</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={monthlyData.slice(-4)}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis 
                  dataKey="month" 
                  stroke="var(--color-muted-foreground)"
                  fontSize={12}
                />
                <YAxis 
                  stroke="var(--color-muted-foreground)"
                  fontSize={12}
                />
                <Tooltip 
                  formatter={(value) => [`$${value.toLocaleString()}`, 'Revenue']}
                  contentStyle={{
                    backgroundColor: 'var(--color-card)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                  }}
                />
                <Bar dataKey="revenue" fill="var(--color-chart-3)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <DashboardChatbot />

        <RecentActivity />
      </div>
    </div>
  )
}