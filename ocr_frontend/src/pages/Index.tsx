import { useState } from "react";
import DocumentUpload from "@/components/DocumentUpload";
import TemplateSelection from "@/components/TemplateSelection";
import KeyValueExtraction from "@/components/KeyValueExtraction";
import ExportInterface from "@/components/ExportInterface";
import ExportHistory from "@/components/ExportHistory";
import AIAssistant from "@/components/AIAssistant";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  CalendarIcon,
  CheckCircle2,
  DollarSign,
  File,
  FileJson2,
  ListChecks,
  Settings,
  History,
  Bot,
} from "lucide-react";
import TemplateSelector from "@/components/TemplateSelector";
import { Document } from "@/types/document";

const Index = () => {
  const [activeView, setActiveView] = useState<
    | "dashboard"
    | "upload"
    | "template-selection"
    | "key-value-extraction"
    | "export"
    | "history"
    | "templates"
    | "assistant"
  >("dashboard");
  const [documents, setDocuments] = useState<Document[]>([]);
  const [currentDocument, setCurrentDocument] = useState<Document | null>(null);
  const [exportHistory, setExportHistory] = useState<any[]>([]);

  const handleManageTemplates = () => {
    setActiveView("templates");
  };

  const handleViewHistory = () => {
    setActiveView("history");
  };

  const handleShowAssistant = () => {
    setActiveView("assistant");
  };

  const handleDocumentUpload = (doc: Document) => {
    setCurrentDocument(doc);
    setActiveView("template-selection");
  };

  const handleTemplateSelected = (templateType: string) => {
    if (currentDocument) {
      const updatedDoc = { ...currentDocument, templateType };
      setCurrentDocument(updatedDoc);
      setActiveView("key-value-extraction");
    }
  };

  const handleDataSaved = (doc: Document) => {
    setDocuments((prev) => [...prev, doc]);
    setCurrentDocument(null);
    setActiveView("export");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="container mx-auto py-6 px-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
            <div className="space-x-4">
              <Button onClick={() => setActiveView("upload")}>
                <File className="mr-2 h-4 w-4" /> Upload Document
              </Button>
              <Button variant="outline" onClick={() => setActiveView("export")}>
                <FileJson2 className="mr-2 h-4 w-4" /> Export
              </Button>
              <Button variant="outline" onClick={handleViewHistory}>
                <History className="mr-2 h-4 w-4" /> History
              </Button>
              <Button variant="outline" onClick={handleManageTemplates}>
                <Settings className="mr-2 h-4 w-4" /> Templates
              </Button>
              <Button variant="outline" onClick={handleShowAssistant}>
                <Bot className="mr-2 h-4 w-4" /> AI Assistant
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {activeView === "dashboard" && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Total Documents
                  </CardTitle>
                  <File className="h-4 w-4 text-gray-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{documents.length}</div>
                  <p className="text-sm text-gray-500">
                    All uploaded documents
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Approved Documents
                  </CardTitle>
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {
                      documents.filter(
                        (doc) => doc.status === "ready_for_export"
                      ).length
                    }
                  </div>
                  <p className="text-sm text-gray-500">
                    Documents ready for export
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Total Exports
                  </CardTitle>
                  <FileJson2 className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {exportHistory.length}
                  </div>
                  <p className="text-sm text-gray-500">
                    Number of exports performed
                  </p>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>
                    Latest document uploads and approvals
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {documents.length === 0 ? (
                    <div className="text-center py-8">
                      <File className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-4 text-lg font-medium">
                        No documents yet
                      </h3>
                      <p className="text-gray-500">
                        Upload your first document to get started
                      </p>
                      <Button
                        onClick={() => setActiveView("upload")}
                        className="mt-4"
                      >
                        Upload Document
                      </Button>
                    </div>
                  ) : (
                    documents.slice(0, 5).map((doc) => (
                      <div
                        key={doc.id}
                        className="py-2 border-b border-gray-200 last:border-none"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            {doc.status === "ready_for_export" ? (
                              <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
                            ) : (
                              <File className="mr-2 h-4 w-4 text-gray-500" />
                            )}
                            <span>{doc.name}</span>
                          </div>
                          <span className="text-sm text-gray-500">
                            {doc.status === "ready_for_export"
                              ? "Approved"
                              : "Uploaded"}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>

              <AIAssistant documents={documents} />
            </div>
          </>
        )}

        {activeView === "upload" && (
          <DocumentUpload
            onBack={() => setActiveView("dashboard")}
            onDocumentUpload={handleDocumentUpload}
          />
        )}

        {activeView === "template-selection" && currentDocument && (
          <TemplateSelection
            document={currentDocument}
            onBack={() => setActiveView("upload")}
            onTemplateSelected={handleTemplateSelected}
          />
        )}

        {activeView === "key-value-extraction" && currentDocument && (
          <KeyValueExtraction
            document={currentDocument}
            onBack={() => setActiveView("template-selection")}
            onDataSaved={handleDataSaved}
          />
        )}

        {activeView === "export" && (
          <ExportInterface
            documents={documents.filter(
              (doc) => doc.status === "ready_for_export"
            )}
            onBack={() => setActiveView("dashboard")}
            onDocumentsUpdate={(exportedDocs) => {
              setExportHistory((prev) => [
                ...prev,
                {
                  date: new Date().toLocaleDateString(),
                  documents: exportedDocs
                    .filter((doc) => doc.status === "exported")
                    .map((doc) => doc.name),
                  exportData: exportedDocs.filter(
                    (doc) => doc.status === "exported"
                  ),
                },
              ]);
              setDocuments(exportedDocs);
              setActiveView("dashboard");
            }}
          />
        )}

        {activeView === "history" && (
          <ExportHistory
            exportHistory={exportHistory}
            onBack={() => setActiveView("dashboard")}
          />
        )}

        {activeView === "templates" && (
          <TemplateSelector onBack={() => setActiveView("dashboard")} />
        )}

        {activeView === "assistant" && (
          <div className="max-w-4xl mx-auto">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-4">
                  <Button
                    variant="outline"
                    onClick={() => setActiveView("dashboard")}
                  >
                    ← Back
                  </Button>
                  <div>
                    <CardTitle>AI Assistant</CardTitle>
                    <CardDescription>
                      Get help with document processing and management
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <AIAssistant documents={documents} />
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
};

export default Index;
