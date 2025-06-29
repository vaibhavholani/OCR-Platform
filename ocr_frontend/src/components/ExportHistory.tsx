
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, Calendar } from "lucide-react";

interface ExportHistoryProps {
  exportHistory: Array<{
    date: string;
    documents: string[];
    exportData: any[];
  }>;
  onBack: () => void;
}

const ExportHistory = ({ exportHistory, onBack }: ExportHistoryProps) => {
  const handleDownload = (exportData: any[], date: string) => {
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `export_${date}.json`;
    a.click();
  };

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={onBack}>← Back</Button>
          <div>
            <CardTitle>Export History</CardTitle>
            <p className="text-sm text-muted-foreground">View and download previous exports</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {exportHistory.length === 0 ? (
            <div className="text-center py-8">
              <Calendar className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium">No exports yet</h3>
              <p className="text-gray-500">Your export history will appear here</p>
            </div>
          ) : (
            exportHistory.map((export_, index) => (
              <Card key={index} className="border border-gray-200">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">Export from {export_.date}</h4>
                      <p className="text-sm text-gray-500">
                        {export_.documents.length} documents exported
                      </p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {export_.documents.slice(0, 3).map((docName, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {docName}
                          </Badge>
                        ))}
                        {export_.documents.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{export_.documents.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDownload(export_.exportData, export_.date)}
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      Download
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ExportHistory;
