
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Upload, Search } from "lucide-react";

const RecentActivity = () => {
  const activities = [
    {
      id: 1,
      type: "upload",
      title: "Invoice_ABC_2024.pdf",
      description: "Uploaded and processed successfully",
      time: "2 minutes ago",
      status: "completed",
      icon: Upload
    },
    {
      id: 2,
      type: "review",
      title: "Utility_Bill_March.pdf",
      description: "Requires manual verification",
      time: "15 minutes ago",
      status: "pending",
      icon: Search
    },
    {
      id: 3,
      type: "processed",
      title: "Vendor_XYZ_Invoice.pdf",
      description: "Data extracted and exported",
      time: "1 hour ago",
      status: "completed",
      icon: FileText
    },
    {
      id: 4,
      type: "upload",
      title: "Service_Invoice_2024.pdf",
      description: "Processing OCR extraction",
      time: "2 hours ago",
      status: "processing",
      icon: Upload
    }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="default" className="bg-green-100 text-green-800">Completed</Badge>;
      case "pending":
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case "processing":
        return <Badge variant="outline" className="bg-blue-100 text-blue-800">Processing</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-4 p-3 rounded-lg hover:bg-accent/50 transition-colors">
              <div className="flex-shrink-0">
                <activity.icon className="h-5 w-5 text-muted-foreground" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-foreground truncate">
                    {activity.title}
                  </p>
                  {getStatusBadge(activity.status)}
                </div>
                <p className="text-sm text-muted-foreground">{activity.description}</p>
                <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default RecentActivity;
