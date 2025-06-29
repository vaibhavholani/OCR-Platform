
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Edit, Plus, Trash2 } from "lucide-react";
import TemplateFormCreator from "./TemplateFormCreator";

interface Template {
  id: string;
  name: string;
  description: string;
  fields: string[];
  isCustom?: boolean;
  templateData?: any; // Store the actual field values
}

interface TemplateSelectorProps {
  onBack: () => void;
  onTemplateCreated?: (template: Template) => void;
}

const TemplateSelector = ({ onBack, onTemplateCreated }: TemplateSelectorProps) => {
  const [selectedView, setSelectedView] = useState<'list' | 'create' | 'edit'>('list');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [selectedTemplateData, setSelectedTemplateData] = useState<Template | null>(null);

  const defaultTemplates: Template[] = [
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
    }
  ];

  // Load custom templates from localStorage
  const loadCustomTemplates = (): Template[] => {
    try {
      const saved = localStorage.getItem('customTemplates');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  };

  const [customTemplates, setCustomTemplates] = useState<Template[]>(loadCustomTemplates);
  const allTemplates = [...defaultTemplates, ...customTemplates];

  const saveCustomTemplate = (template: Template) => {
    const updatedTemplates = [...customTemplates, template];
    setCustomTemplates(updatedTemplates);
    localStorage.setItem('customTemplates', JSON.stringify(updatedTemplates));
    onTemplateCreated?.(template);
  };

  const deleteCustomTemplate = (templateId: string) => {
    const updatedTemplates = customTemplates.filter(t => t.id !== templateId);
    setCustomTemplates(updatedTemplates);
    localStorage.setItem('customTemplates', JSON.stringify(updatedTemplates));
  };

  const handleCreateNew = () => {
    setSelectedTemplate('register-basic');
    setSelectedTemplateData(null);
    setSelectedView('create');
  };

  const handleEditTemplate = (templateId: string) => {
    const template = allTemplates.find(t => t.id === templateId);
    setSelectedTemplate(templateId);
    setSelectedTemplateData(template || null);
    setSelectedView('edit');
  };

  const handleUseTemplate = (templateId: string) => {
    const template = allTemplates.find(t => t.id === templateId);
    setSelectedTemplate(templateId);
    setSelectedTemplateData(template || null);
    setSelectedView('create');
  };

  const handleBackToList = () => {
    setSelectedView('list');
    setSelectedTemplate('');
    setSelectedTemplateData(null);
  };

  const handleTemplateSaved = (templateData: any, templateFields: string[]) => {
    if (selectedView === 'create') {
      // Create new custom template
      const newTemplate: Template = {
        id: `custom-${Date.now()}`,
        name: `Custom Template - ${new Date().toLocaleDateString()}`,
        description: `Custom template with ${templateFields.length} fields`,
        fields: templateFields,
        isCustom: true,
        templateData: templateData // Store the actual values
      };
      saveCustomTemplate(newTemplate);
    }
    handleBackToList();
  };

  if (selectedView === 'create' || selectedView === 'edit') {
    return (
      <TemplateFormCreator 
        onBack={handleBackToList}
        templateType={selectedTemplate}
        templateData={selectedTemplateData}
        isEditing={selectedView === 'edit'}
        onTemplateSaved={handleTemplateSaved}
      />
    );
  }

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={onBack}>← Back</Button>
          <div>
            <CardTitle>Template Management</CardTitle>
            <p className="text-sm text-muted-foreground">Create and manage your form templates</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Create New Template */}
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Available Templates</h3>
            <Button onClick={handleCreateNew} className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Create New Template
            </Button>
          </div>

          {/* Default Templates */}
          <div>
            <h4 className="text-md font-medium mb-3 text-gray-700">Default Templates</h4>
            <div className="grid gap-4">
              {defaultTemplates.map((template) => (
                <Card key={template.id} className="border border-gray-200">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-semibold text-lg">{template.name}</h4>
                        <p className="text-sm text-muted-foreground mt-1">{template.description}</p>
                        <div className="mt-3">
                          <p className="text-xs text-gray-500 mb-2">Fields included:</p>
                          <div className="flex flex-wrap gap-1">
                            {template.fields.map((field) => (
                              <span 
                                key={field} 
                                className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-md"
                              >
                                {field.charAt(0).toUpperCase() + field.slice(1).replace(/([A-Z])/g, ' $1')}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleEditTemplate(template.id)}
                          className="flex items-center gap-1"
                        >
                          <Edit className="h-3 w-3" />
                          Edit
                        </Button>
                        <Button 
                          size="sm"
                          onClick={() => handleUseTemplate(template.id)}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          Use Template
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Custom Templates */}
          {customTemplates.length > 0 && (
            <div>
              <h4 className="text-md font-medium mb-3 text-gray-700">Custom Templates</h4>
              <div className="grid gap-4">
                {customTemplates.map((template) => (
                  <Card key={template.id} className="border border-green-200 bg-green-50">
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold text-lg">{template.name}</h4>
                            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-md font-medium">
                              Custom
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">{template.description}</p>
                          <div className="mt-3">
                            <p className="text-xs text-gray-500 mb-2">Fields included:</p>
                            <div className="flex flex-wrap gap-1">
                              {template.fields.map((field) => (
                                <span 
                                  key={field} 
                                  className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-md"
                                >
                                  {field.charAt(0).toUpperCase() + field.slice(1).replace(/([A-Z])/g, ' $1')}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div className="flex gap-2 ml-4">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => deleteCustomTemplate(template.id)}
                            className="flex items-center gap-1 text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-3 w-3" />
                            Delete
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleEditTemplate(template.id)}
                            className="flex items-center gap-1"
                          >
                            <Edit className="h-3 w-3" />
                            Edit
                          </Button>
                          <Button 
                            size="sm"
                            onClick={() => handleUseTemplate(template.id)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            Use Template
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default TemplateSelector;
