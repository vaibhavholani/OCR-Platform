
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, FileText } from "lucide-react";
import { Document } from "@/types/document";
import ProgressIndicator from "./ProgressIndicator";

interface TemplateSelectionProps {
  document: Document;
  onBack: () => void;
  onTemplateSelected: (templateType: string) => void;
}

const TemplateSelection = ({ document, onBack, onTemplateSelected }: TemplateSelectionProps) => {
  const templates = [
    {
      id: 'register-basic',
      name: 'Register Entry - Basic',
      description: 'Basic register entry with Supplier, Party, Bill Number, Date, and Amount',
      fields: ['supplier', 'party', 'billNumber', 'registerDate', 'amount']
    },
    {
      id: 'register-gst',
      name: 'Register Entry - With GST',
      description: 'Register entry with additional GST Percentage field',
      fields: ['supplier', 'party', 'billNumber', 'registerDate', 'amount', 'gstPercentage']
    },
    {
      id: 'invoice-standard',
      name: 'Standard Invoice',
      description: 'Standard invoice template with line items and totals',
      fields: ['invoiceNumber', 'vendorName', 'invoiceDate', 'dueDate', 'totalAmount', 'subtotal', 'taxAmount']
    }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <ProgressIndicator currentStep={2} />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        {/* Document Preview Panel */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Document Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <FileText className="h-8 w-8 text-blue-500" />
                <div className="flex-1">
                  <p className="text-sm font-medium">{document.name}</p>
                  <p className="text-xs text-gray-500">Uploaded successfully</p>
                </div>
              </div>
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-xs text-blue-600 font-medium">Preview</p>
                <p className="text-sm text-gray-600 mt-1">Document is ready for template selection</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Template Selection Panel */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-4">
                <Button variant="outline" onClick={onBack}>← Back</Button>
                <div>
                  <CardTitle>Select Template</CardTitle>
                  <p className="text-sm text-muted-foreground">Choose a template for data extraction</p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {templates.map((template) => (
                  <Card key={template.id} className="border border-gray-200 hover:border-blue-300 transition-colors cursor-pointer">
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h4 className="font-semibold text-lg">{template.name}</h4>
                          <p className="text-sm text-muted-foreground mt-1">{template.description}</p>
                          <div className="mt-3">
                            <p className="text-xs text-gray-500 mb-2">Fields included:</p>
                            <div className="flex flex-wrap gap-1">
                              {template.fields.map((field) => (
                                <Badge key={field} variant="outline" className="text-xs">
                                  {field.charAt(0).toUpperCase() + field.slice(1).replace(/([A-Z])/g, ' $1')}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                        <Button 
                          onClick={() => onTemplateSelected(template.id)}
                          className="ml-4 bg-blue-600 hover:bg-blue-700"
                        >
                          <Check className="mr-2 h-4 w-4" />
                          Select Template
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TemplateSelection;
