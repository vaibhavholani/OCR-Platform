import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Plus,
  Save,
  FileText,
  Trash2,
  Eye,
  Database,
  Check,
  X,
  FileSpreadsheet,
  CheckCircle,
  Bot,
} from "lucide-react";
import { Document } from "@/types/document";
import ProgressIndicator from "./ProgressIndicator";
import { useToast } from "@/hooks/use-toast";
import AIAssistant from "./AIAssistant";

interface KeyValueExtractionProps {
  document: Document;
  onBack: () => void;
  onDataSaved: (document: Document) => void;
}

interface ExtraField {
  id: string;
  key: string;
  value: string;
  type: "text" | "number" | "date" | "email" | "url";
  approved: boolean;
}

interface FieldApproval {
  [key: string]: boolean;
}

const KeyValueExtraction = ({
  document,
  onBack,
  onDataSaved,
}: KeyValueExtractionProps) => {
  const { toast } = useToast();

  // Provide proper default structure for ocrData
  const defaultOcrData = {
    invoice_number: "",
    vendor_name: "",
    invoice_date: "",
    due_date: "",
    total_amount: "",
    subtotal: "",
    tax_amount: "",
    line_items: [],
  };

  const [extractedData, setExtractedData] = useState(
    document.ocrData || defaultOcrData
  );
  const [fieldApprovals, setFieldApprovals] = useState<FieldApproval>({});
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [selectedTemplateFields, setSelectedTemplateFields] = useState<
    string[]
  >([]);
  const [showChat, setShowChat] = useState(false);

  // Create and manage object URL for uploaded file
  useEffect(() => {
    let url: string | null = null;
    console.log("document.file:", document.file);
    console.log("document.preview:", document.preview);

    if (document.file && document.file instanceof File) {
      url = URL.createObjectURL(document.file);
      setImageUrl(url);
      console.log("Generated imageUrl:", url, "File type:", document.file.type);
    } else if (document.preview) {
      setImageUrl(document.preview);
    } else {
      setImageUrl(null);
    }

    return () => {
      if (url) {
        URL.revokeObjectURL(url);
      }
    };
  }, [document.file, document.preview]);

  // Initialize selected template fields
  useEffect(() => {
    setSelectedTemplateFields(getTemplateFields());
    // Inject mock data when template changes
    setExtractedData((prev) => ({
      ...prev,
      ...getMockDataForTemplate(document.templateType),
    }));
  }, [document.templateType]);

  const saveCustomTemplate = (templateFields: string[]) => {
    try {
      const existingTemplates = JSON.parse(
        localStorage.getItem("customTemplates") || "[]"
      );
      const newTemplate = {
        id: `custom-${Date.now()}`,
        name: `Custom Template - ${document.name}`,
        description: `Custom template with ${templateFields.length} fields created from ${document.name}`,
        fields: templateFields,
        isCustom: true,
        templateData: { ...extractedData },
      };

      const updatedTemplates = [...existingTemplates, newTemplate];
      localStorage.setItem("customTemplates", JSON.stringify(updatedTemplates));

      return newTemplate;
    } catch (error) {
      console.error("Error saving custom template:", error);
      return null;
    }
  };

  const handleExtractedDataChange = (key: string, value: string) => {
    setExtractedData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleFieldApproval = (fieldKey: string, approved: boolean) => {
    setFieldApprovals((prev) => ({
      ...prev,
      [fieldKey]: approved,
    }));

    // If field is rejected, remove it from selected template fields
    if (!approved) {
      setSelectedTemplateFields((prev) =>
        prev.filter((field) => field !== fieldKey)
      );
    } else {
      // If field is approved and not in selected fields, add it back
      setSelectedTemplateFields((prev) => {
        if (!prev.includes(fieldKey)) {
          return [...prev, fieldKey];
        }
        return prev;
      });
    }
  };

  const handleApproveAll = () => {
    const allFields = getTemplateFields();
    const newApprovals: FieldApproval = {};
    allFields.forEach((field) => {
      newApprovals[field] = true;
    });
    setFieldApprovals(newApprovals);
    setSelectedTemplateFields(allFields);

    toast({
      title: "All Fields Approved!",
      description: "All template fields have been approved.",
    });
  };

  const handleSaveData = () => {
    // Only include approved fields
    const approvedData = { ...extractedData };

    // Filter template fields by approval
    getTemplateFields().forEach((field) => {
      if (fieldApprovals[field] !== true) {
        // Remove field if not explicitly approved
        delete approvedData[field];
      }
    });

    const updatedDocument: Document = {
      ...document,
      ocrData: approvedData,
      status: "ready_for_export",
    };

    onDataSaved(updatedDocument);

    toast({
      title: "Success!",
      description: "Document data has been saved successfully.",
    });
  };

  const handleSaveAsTemplate = () => {
    const approvedFields = getTemplateFields().filter(
      (field) => fieldApprovals[field] === true
    );

    const savedTemplate = saveCustomTemplate(approvedFields);
    if (savedTemplate) {
      toast({
        title: "Template Saved!",
        description: `Custom template "${savedTemplate.name}" has been saved and can be reused.`,
      });
    }

    // Also save the data
    handleSaveData();
  };

  const getTemplateFields = () => {
    switch (document.templateType) {
      case "register-basic":
        return ["supplier", "party", "billNumber", "registerDate", "amount"];
      case "register-gst":
        return [
          "supplier",
          "party",
          "billNumber",
          "registerDate",
          "amount",
          "gstPercentage",
        ];
      case "invoice-standard":
        return [
          "invoiceNumber",
          "vendorName",
          "invoiceDate",
          "dueDate",
          "totalAmount",
          "subtotal",
          "taxAmount",
        ];
      default:
        return Object.keys(extractedData);
    }
  };

  const formatFieldName = (field: string) => {
    return (
      field.charAt(0).toUpperCase() + field.slice(1).replace(/([A-Z])/g, " $1")
    );
  };

  // Add this function to provide mock data for each template
  function getMockDataForTemplate(templateType: string) {
    switch (templateType) {
      case "register-basic":
        return {
          supplier: "Acme Corp",
          party: "John Doe",
          billNumber: "BILL-1234",
          registerDate: "2024-07-01",
          amount: "1500.00",
        };
      case "register-gst":
        return {
          supplier: "GST Supplies Ltd",
          party: "Jane Smith",
          billNumber: "GST-5678",
          registerDate: "2024-07-02",
          amount: "2000.00",
          gstPercentage: "18%",
        };
      case "invoice-standard":
        return {
          invoiceNumber: "INV-2024-001",
          vendorName: "Vendor X",
          invoiceDate: "2024-07-03",
          dueDate: "2024-08-03",
          totalAmount: "2500.00",
          subtotal: "2100.00",
          taxAmount: "400.00",
        };
      default:
        return {};
    }
  }

  return (
    <div className="max-w-7xl mx-auto relative">
      <ProgressIndicator
        currentStep={3}
        steps={[
          { id: 1, name: "Upload", description: "Upload Document" },
          { id: 2, name: "Template", description: "Choose Template" },
          {
            id: 3,
            name: "Extract and save data",
            description: "Extract and save data",
          },
          { id: 4, name: "Export", description: "Export your data" },
        ]}
      />

      <div className="flex flex-col lg:flex-row gap-6 mt-6">
        {/* Document Preview Panel - Left Sidebar */}
        <div className="w-full lg:w-1/2 h-auto lg:h-[80vh] overflow-y-auto flex flex-col">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Document
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="aspect-[3/4] bg-gray-50 rounded-lg border overflow-hidden">
                {imageUrl &&
                document.file &&
                document.file.type.startsWith("image/") ? (
                  <img
                    src={imageUrl}
                    alt={document.name}
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      setImageUrl(null);
                      console.error("Image failed to load:", e);
                    }}
                  />
                ) : imageUrl &&
                  document.file &&
                  document.file.type.toLowerCase().includes("pdf") ? (
                  <iframe
                    src={imageUrl}
                    title={document.name}
                    className="w-full h-full"
                    style={{ minHeight: 400 }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="text-center p-4">
                      <FileText className="h-16 w-16 text-gray-400 mx-auto mb-3" />
                      <p className="text-sm font-medium text-gray-600">
                        {document.name}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {document.file || document.preview
                          ? "Unable to preview this file. Please ensure it's a valid image or PDF."
                          : "Loading document..."}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Key-Value Extraction Panel - Right Side */}
        <div className="w-full lg:w-1/2 h-auto lg:h-[80vh] overflow-y-auto flex flex-col">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-4">
                <Button variant="outline" onClick={onBack}>
                  ← Back
                </Button>
                <div>
                  <CardTitle>Extract & Edit Data</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Review, approve/reject fields and add custom data
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Template Fields Section */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      Template Fields ({document.templateType})
                    </h3>
                    <Button
                      onClick={handleApproveAll}
                      variant="outline"
                      size="sm"
                      className="text-green-600 border-green-600 hover:bg-green-50"
                    >
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Approve All
                    </Button>
                  </div>
                  {/* Removed Template Field Selection Dropdown */}
                  <div className="space-y-4">
                    {getTemplateFields()
                      .filter((field) => selectedTemplateFields.includes(field))
                      .map((field) => (
                        <div
                          key={field}
                          className="flex items-center gap-4 p-4 border rounded-lg"
                        >
                          <div className="flex-1 space-y-2">
                            <Label htmlFor={field}>
                              {formatFieldName(field)}
                            </Label>
                            <Input
                              id={field}
                              value={extractedData[field] || ""}
                              onChange={(e) =>
                                handleExtractedDataChange(field, e.target.value)
                              }
                              placeholder={`Enter ${formatFieldName(
                                field
                              ).toLowerCase()}`}
                              className="w-full"
                            />
                          </div>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant={
                                fieldApprovals[field] === true
                                  ? "default"
                                  : "outline"
                              }
                              onClick={() => handleFieldApproval(field, true)}
                              className={
                                fieldApprovals[field] === true
                                  ? "bg-green-600 hover:bg-green-700 text-white"
                                  : "text-green-600 border-green-600 hover:bg-green-50"
                              }
                            >
                              <Check className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant={
                                fieldApprovals[field] === false
                                  ? "default"
                                  : "outline"
                              }
                              onClick={() => handleFieldApproval(field, false)}
                              className={
                                fieldApprovals[field] === false
                                  ? "bg-red-600 hover:bg-red-700 text-white"
                                  : "text-red-600 border-red-600 hover:bg-red-50"
                              }
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      {/* Save Buttons below the flex row */}
      <div className="flex gap-4 justify-center mt-6">
        <Button
          onClick={handleSaveData}
          className="flex-1 max-w-xs bg-blue-600 hover:bg-blue-700 text-lg py-3"
        >
          <Save className="mr-2 h-5 w-5" />
          Save Data
        </Button>
      </div>
      {/* Floating AI Chatbot Button and Chat Box */}
      <div>
        {/* Floating Button */}
        <button
          type="button"
          className="fixed bottom-8 right-8 z-50 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg w-14 h-14 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-blue-400"
          onClick={() => setShowChat((prev) => !prev)}
          aria-label="Chat with AI Assistant"
        >
          <Bot className="h-7 w-7" />
        </button>
        {/* Floating Chat Box */}
        {showChat && (
          <div className="fixed bottom-28 right-8 z-50 w-80 max-w-full shadow-2xl rounded-xl bg-white border border-gray-200 animate-fade-in">
            <div className="flex justify-end p-2">
              <button
                className="text-gray-400 hover:text-gray-600"
                onClick={() => setShowChat(false)}
                aria-label="Close chat"
              >
                <span className="text-xl font-bold">×</span>
              </button>
            </div>
            <AIAssistant documents={[]} />
          </div>
        )}
      </div>
    </div>
  );
};

export default KeyValueExtraction;
