
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Download, FileJson, FileSpreadsheet, FileText, CheckCircle2 } from "lucide-react";
import { Document } from "@/types/document";
import { useToast } from "@/hooks/use-toast";

interface ExportInterfaceProps {
  documents: Document[];
  onBack: () => void;
  onDocumentsUpdate: (documents: Document[]) => void;
}

const ExportInterface = ({ documents, onBack, onDocumentsUpdate }: ExportInterfaceProps) => {
  const { toast } = useToast();
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [exportFormat, setExportFormat] = useState<'json' | 'csv' | 'txt'>('json');

  const handleSelectAll = () => {
    if (selectedDocs.length === documents.length) {
      setSelectedDocs([]);
    } else {
      setSelectedDocs(documents.map(doc => doc.id));
    }
  };

  const handleDocSelect = (docId: string) => {
    setSelectedDocs(prev => 
      prev.includes(docId) 
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const exportToJSON = (data: any[]) => {
    return JSON.stringify(data, null, 2);
  };

  const exportToCSV = (data: any[]) => {
    if (data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvHeaders = headers.join(',');
    const csvRows = data.map(row => 
      headers.map(header => {
        const value = row[header];
        return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
      }).join(',')
    );
    
    return [csvHeaders, ...csvRows].join('\n');
  };

  const exportToTXT = (data: any[]) => {
    return data.map(item => {
      return Object.entries(item)
        .map(([key, value]) => `${key}: ${value}`)
        .join('\n');
    }).join('\n\n---\n\n');
  };

  const handleExport = () => {
    if (selectedDocs.length === 0) {
      toast({
        title: "No documents selected",
        description: "Please select at least one document to export.",
        variant: "destructive"
      });
      return;
    }

    const selectedDocuments = documents.filter(doc => selectedDocs.includes(doc.id));
    
    // Mark selected documents as exported
    const updatedDocuments = documents.map(doc => 
      selectedDocs.includes(doc.id) 
        ? { ...doc, status: 'exported' as const }
        : doc
    );

    // Prepare export data with all OCR data
    const exportData = selectedDocuments.map(doc => ({
      document_name: doc.name,
      template_type: doc.templateType,
      upload_date: doc.uploadDate,
      ...doc.ocrData
    }));

    let content: string;
    let mimeType: string;
    let fileExtension: string;

    switch (exportFormat) {
      case 'csv':
        content = exportToCSV(exportData);
        mimeType = 'text/csv';
        fileExtension = 'csv';
        break;
      case 'txt':
        content = exportToTXT(exportData);
        mimeType = 'text/plain';
        fileExtension = 'txt';
        break;
      default:
        content = exportToJSON(exportData);
        mimeType = 'application/json';
        fileExtension = 'json';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bulk_export_${new Date().toISOString().split('T')[0]}.${fileExtension}`;
    a.click();
    URL.revokeObjectURL(url);

    onDocumentsUpdate(updatedDocuments);
    
    toast({
      title: "Export successful!",
      description: `${selectedDocs.length} documents exported as ${exportFormat.toUpperCase()}.`,
    });
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'csv': return <FileSpreadsheet className="h-4 w-4" />;
      case 'txt': return <FileText className="h-4 w-4" />;
      default: return <FileJson className="h-4 w-4" />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <Button variant="outline" onClick={onBack}>← Back</Button>
            <div>
              <CardTitle>Export Documents</CardTitle>
              <p className="text-sm text-muted-foreground">Select documents and format for bulk export</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Export Controls */}
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <Button variant="outline" onClick={handleSelectAll}>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  {selectedDocs.length === documents.length ? 'Deselect All' : 'Select All'}
                </Button>
                <div className="text-sm text-gray-600">
                  {selectedDocs.length} of {documents.length} selected
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Format:</span>
                  <Select value={exportFormat} onValueChange={(value: 'json' | 'csv' | 'txt') => setExportFormat(value)}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="json">
                        <div className="flex items-center gap-2">
                          <FileJson className="h-4 w-4" />
                          JSON
                        </div>
                      </SelectItem>
                      <SelectItem value="csv">
                        <div className="flex items-center gap-2">
                          <FileSpreadsheet className="h-4 w-4" />
                          CSV
                        </div>
                      </SelectItem>
                      <SelectItem value="txt">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          TXT
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <Button 
                  onClick={handleExport}
                  disabled={selectedDocs.length === 0}
                  className="flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  {getFormatIcon(exportFormat)}
                  Export ({selectedDocs.length})
                </Button>
              </div>
            </div>

            {/* Documents List */}
            <div className="space-y-3">
              {documents.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-4 text-lg font-medium">No documents ready for export</h3>
                  <p className="text-gray-500">Complete document processing to see exportable documents here</p>
                </div>
              ) : (
                documents.map((doc) => (
                  <Card key={doc.id} className="border border-gray-200 hover:border-blue-300 transition-colors">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Checkbox
                            checked={selectedDocs.includes(doc.id)}
                            onCheckedChange={() => handleDocSelect(doc.id)}
                          />
                          <div className="flex-1">
                            <h4 className="font-medium">{doc.name}</h4>
                            <div className="flex items-center gap-2 mt-1">
                              <p className="text-sm text-gray-500">
                                Template: {doc.templateType}
                              </p>
                              <Badge variant="outline" className="text-xs">
                                {doc.ocrData.vendor_name || 'Unknown Vendor'}
                              </Badge>
                              {doc.ocrData.total_amount && (
                                <Badge variant="outline" className="text-xs">
                                  ${doc.ocrData.total_amount}
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">Ready</Badge>
                          <div className="text-xs text-gray-500">
                            {doc.uploadDate}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ExportInterface;
