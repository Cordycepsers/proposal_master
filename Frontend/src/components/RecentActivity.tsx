import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"
import { Avatar, AvatarFallback } from "./ui/avatar"
import { Clock, CheckCircle, AlertCircle, UserPlus } from "lucide-react"

const activities = [
  {
    id: 1,
    type: 'project_update',
    message: 'Brand Identity project completed',
    user: 'Sarah Johnson',
    time: '2 hours ago',
    icon: CheckCircle,
    iconColor: 'text-green-600'
  },
  {
    id: 2,
    type: 'new_lead',
    message: 'New hot lead from TechStart Inc',
    user: 'Mike Chen',
    time: '4 hours ago',
    icon: UserPlus,
    iconColor: 'text-blue-600'
  },
  {
    id: 3,
    type: 'deadline',
    message: 'E-commerce Platform due in 2 days',
    user: 'System',
    time: '6 hours ago',
    icon: AlertCircle,
    iconColor: 'text-orange-600'
  },
  {
    id: 4,
    type: 'project_start',
    message: 'Website Redesign entered review phase',
    user: 'Emily Davis',
    time: '1 day ago',
    icon: Clock,
    iconColor: 'text-gray-600'
  },
  {
    id: 5,
    type: 'lead_converted',
    message: 'Lead converted to project - $30,000',
    user: 'David Wilson',
    time: '1 day ago',
    icon: CheckCircle,
    iconColor: 'text-green-600'
  }
]

export function RecentActivity() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => {
            const Icon = activity.icon
            return (
              <div key={activity.id} className="flex items-start gap-3">
                <div className={`p-2 rounded-full bg-muted ${activity.iconColor}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">{activity.message}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-muted-foreground">{activity.user}</span>
                    <span className="text-xs text-muted-foreground">•</span>
                    <span className="text-xs text-muted-foreground">{activity.time}</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}