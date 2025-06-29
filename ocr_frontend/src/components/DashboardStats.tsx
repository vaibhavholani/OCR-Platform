
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Upload, Search, Settings } from "lucide-react";

const DashboardStats = () => {
  const stats = [
    {
      title: "Total Processed",
      value: "1,247",
      description: "Invoices processed this month",
      icon: FileText,
      trend: "+12%"
    },
    {
      title: "Pending Review",
      value: "23",
      description: "Awaiting verification",
      icon: Search,
      trend: "-3%"
    },
    {
      title: "Templates Active",
      value: "8",
      description: "Configured templates",
      icon: Settings,
      trend: "+2"
    },
    {
      title: "Processing Queue",
      value: "0",
      description: "Currently processing",
      icon: Upload,
      trend: "0%"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <Card key={index} className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {stat.title}
            </CardTitle>
            <stat.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stat.value}</div>
            <p className="text-xs text-muted-foreground">
              {stat.description}
            </p>
            <div className="flex items-center pt-2">
              <span className={`text-xs font-medium ${
                stat.trend.startsWith('+') ? 'text-green-600' : 
                stat.trend.startsWith('-') ? 'text-red-600' : 
                'text-muted-foreground'
              }`}>
                {stat.trend} from last month
              </span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default DashboardStats;
