import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Upload, Search } from "lucide-react";
import { UserDocument } from "@/types/document";

const RecentActivity = () => {
  const [documents, setDocuments] = useState<UserDocument[]>([]);

  useEffect(() => {
    const userId = localStorage.getItem("user_id");
    if (!userId) return;
    fetch(`http://localhost:5000/api/users/${userId}/documents`)
      .then((res) => res.json())
      .then((data) => {
        setDocuments(data.documents || []);
      });
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "processed":
        return (
          <Badge variant="default" className="bg-green-100 text-green-800">
            Processed
          </Badge>
        );
      case "pending":
        return (
          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
            Pending
          </Badge>
        );
      case "processing":
        return (
          <Badge variant="outline" className="bg-blue-100 text-blue-800">
            Processing
          </Badge>
        );
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
          {documents.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No recent activity.
            </div>
          ) : (
            documents.slice(0, 5).map((doc) => (
              <div
                key={doc.doc_id}
                className="flex items-start space-x-4 p-3 rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className="flex-shrink-0">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-foreground truncate">
                      {doc.original_filename}
                    </p>
                    {getStatusBadge(doc.status)}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {doc.file_path}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Uploaded: {new Date(doc.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default RecentActivity;
