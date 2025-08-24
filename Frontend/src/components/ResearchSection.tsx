import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { MetricCard } from "./MetricCard"
import { TrendingUp, TrendingDown, Target, Globe } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts'

const marketTrends = [
  { month: 'Jul', webDev: 85, mobileApp: 92, branding: 78, ecommerce: 88 },
  { month: 'Aug', webDev: 88, mobileApp: 89, branding: 82, ecommerce: 91 },
  { month: 'Sep', webDev: 92, mobileApp: 95, branding: 85, ecommerce: 89 },
  { month: 'Oct', webDev: 89, mobileApp: 98, branding: 88, ecommerce: 93 },
  { month: 'Nov', webDev: 95, mobileApp: 94, branding: 91, ecommerce: 96 },
  { month: 'Dec', webDev: 98, mobileApp: 97, branding: 94, ecommerce: 99 },
]

const competitorData = [
  { name: 'Our Company', marketShare: 15, growth: 12 },
  { name: 'Competitor A', marketShare: 22, growth: 8 },
  { name: 'Competitor B', marketShare: 18, growth: 15 },
  { name: 'Competitor C', marketShare: 12, growth: -3 },
  { name: 'Others', marketShare: 33, growth: 5 },
]

const industryInsights = [
  {
    title: "Web Development Demand",
    trend: "up",
    value: "+18%",
    description: "Increased demand for responsive web applications"
  },
  {
    title: "Mobile App Projects",
    trend: "up",
    value: "+25%",
    description: "Growing mobile-first approach across industries"
  },
  {
    title: "Traditional Marketing",
    trend: "down",
    value: "-12%",
    description: "Shift towards digital marketing strategies"
  },
  {
    title: "E-commerce Solutions",
    trend: "up",
    value: "+30%",
    description: "Surge in online retail platform development"
  }
]

export function ResearchSection() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Market Share"
          value="15%"
          change="+2% from last quarter"
          changeType="positive"
          icon={Target}
        />
        <MetricCard
          title="Industry Growth"
          value="12%"
          change="YoY growth rate"
          changeType="positive"
          icon={TrendingUp}
        />
        <MetricCard
          title="Market Size"
          value="$2.4B"
          change="Total addressable market"
          icon={Globe}
        />
        <MetricCard
          title="Competition Index"
          value="68"
          change="Market competitiveness score"
          icon={Target}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Service Demand Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={marketTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="webDev" stackId="1" stroke="var(--color-chart-1)" fill="var(--color-chart-1)" />
                <Area type="monotone" dataKey="mobileApp" stackId="1" stroke="var(--color-chart-2)" fill="var(--color-chart-2)" />
                <Area type="monotone" dataKey="branding" stackId="1" stroke="var(--color-chart-3)" fill="var(--color-chart-3)" />
                <Area type="monotone" dataKey="ecommerce" stackId="1" stroke="var(--color-chart-4)" fill="var(--color-chart-4)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Competitive Landscape</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={competitorData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="marketShare" fill="var(--color-chart-1)" name="Market Share %" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Industry Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {industryInsights.map((insight, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <div className="flex items-center space-x-3">
                    {insight.trend === 'up' ? (
                      <TrendingUp className="h-5 w-5 text-green-600" />
                    ) : (
                      <TrendingDown className="h-5 w-5 text-red-600" />
                    )}
                    <div>
                      <h4 className="font-medium">{insight.title}</h4>
                      <p className="text-sm text-muted-foreground">{insight.description}</p>
                    </div>
                  </div>
                  <div className={`font-semibold ${insight.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                    {insight.value}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Growth Opportunities</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-3 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">AI Integration Services</h4>
                <p className="text-sm text-muted-foreground">High demand for AI-powered solutions across industries</p>
                <div className="mt-2 text-sm font-medium text-green-600">Opportunity Score: 85/100</div>
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">Sustainable Tech Solutions</h4>
                <p className="text-sm text-muted-foreground">Growing focus on environmentally conscious technology</p>
                <div className="mt-2 text-sm font-medium text-green-600">Opportunity Score: 78/100</div>
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">Remote Work Tools</h4>
                <p className="text-sm text-muted-foreground">Continued demand for remote collaboration platforms</p>
                <div className="mt-2 text-sm font-medium text-green-600">Opportunity Score: 72/100</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}