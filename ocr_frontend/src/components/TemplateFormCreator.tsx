
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon, Search } from "lucide-react";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";

interface Template {
  id: string;
  name: string;
  description: string;
  fields: string[];
  isCustom?: boolean;
  templateData?: any;
}

interface TemplateFormCreatorProps {
  onBack: () => void;
  templateType?: string;
  templateData?: Template | null;
  isEditing?: boolean;
  onTemplateSaved?: (templateData: any, templateFields: string[]) => void;
}

const TemplateFormCreator = ({ onBack, templateType = 'register-basic', templateData, isEditing = false, onTemplateSaved }: TemplateFormCreatorProps) => {
  const { toast } = useToast();
  
  const [formData, setFormData] = useState({
    supplier: "",
    party: "",
    billNumber: "",
    registerDate: null as Date | null,
    amount: "",
    gstPercentage: ""
  });

  const [supplierOpen, setSupplierOpen] = useState(false);
  const [partyOpen, setPartyOpen] = useState(false);
  const [extraFields, setExtraFields] = useState<Array<{id: string, key: string, value: string}>>([]);
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');

  // Load template data if available
  useEffect(() => {
    if (templateData && templateData.templateData) {
      const data = templateData.templateData;
      
      // Set form data
      setFormData({
        supplier: data.supplier || "",
        party: data.party || "",
        billNumber: data.billNumber || "",
        registerDate: data.registerDate ? new Date(data.registerDate) : null,
        amount: data.amount || "",
        gstPercentage: data.gstPercentage || ""
      });

      // Set extra fields
      const templateFields = getTemplateFields();
      const extraFieldsFromTemplate = Object.entries(data)
        .filter(([key]) => !templateFields.includes(key))
        .map(([key, value], index) => ({
          id: `loaded-${index}`,
          key,
          value: String(value)
        }));
      
      setExtraFields(extraFieldsFromTemplate);
    }
  }, [templateData, templateType]);

  // Mock data for dropdowns
  const suppliers = [
    { value: "supplier1", label: "ABC Corp" },
    { value: "supplier2", label: "XYZ Ltd" },
    { value: "supplier3", label: "Global Supplies Inc" },
    { value: "supplier4", label: "Metro Trading Co" }
  ];

  const parties = [
    { value: "party1", label: "Client A" },
    { value: "party2", label: "Client B" },
    { value: "party3", label: "Client C" },
    { value: "party4", label: "Internal Department" }
  ];

  const isGSTTemplate = templateType === 'register-gst';

  const handleAddExtraField = () => {
    if (newKey.trim() && newValue.trim()) {
      setExtraFields(prev => [...prev, {
        id: Date.now().toString(),
        key: newKey.trim(),
        value: newValue.trim()
      }]);
      setNewKey('');
      setNewValue('');
    }
  };

  const handleRemoveExtraField = (id: string) => {
    setExtraFields(prev => prev.filter(field => field.id !== id));
  };

  const handleUpdateExtraField = (id: string, key: string, value: string) => {
    setExtraFields(prev => prev.map(field => 
      field.id === id ? { ...field, key, value } : field
    ));
  };

  const handleReset = () => {
    setFormData({
      supplier: "",
      party: "",
      billNumber: "",
      registerDate: null,
      amount: "",
      gstPercentage: ""
    });
    setExtraFields([]);
  };

  const handleSaveDraft = () => {
    console.log("Draft saved:", formData);
    toast({
      title: "Draft Saved",
      description: "Your template draft has been saved locally.",
    });
  };

  const handleSubmit = () => {
    // Combine template fields with extra fields
    const templateFields = getTemplateFields();
    const extraFieldKeys = extraFields.map(field => field.key);
    const allFields = [...templateFields, ...extraFieldKeys];
    
    // Combine all data
    const combinedData = { ...formData };
    extraFields.forEach(field => {
      combinedData[field.key] = field.value;
    });

    console.log("Register entry submitted:", combinedData);
    
    // Save as new template if we have extra fields
    if (extraFields.length > 0 && onTemplateSaved) {
      onTemplateSaved(combinedData, allFields);
      toast({
        title: "Template Saved!",
        description: "Your custom template has been saved and can be reused.",
      });
    } else {
      toast({
        title: "Data Submitted!",
        description: "Your register entry has been submitted successfully.",
      });
    }
  };

  const getTemplateFields = () => {
    switch (templateType) {
      case 'register-basic':
        return ['supplier', 'party', 'billNumber', 'registerDate', 'amount'];
      case 'register-gst':
        return ['supplier', 'party', 'billNumber', 'registerDate', 'amount', 'gstPercentage'];
      default:
        return ['supplier', 'party', 'billNumber', 'registerDate', 'amount'];
    }
  };

  // Keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.altKey) {
      switch (e.key.toLowerCase()) {
        case 'r':
          e.preventDefault();
          handleReset();
          break;
        case 'd':
          e.preventDefault();
          handleSaveDraft();
          break;
        case 's':
          e.preventDefault();
          handleSubmit();
          break;
      }
    }
  };

  const getTemplateTitle = () => {
    if (isEditing) {
      return isGSTTemplate ? "Edit Register Entry - With GST Template" : "Edit Register Entry - Basic Template";
    }
    return isGSTTemplate ? "Register Entry Template - With GST" : "Register Entry Template - Basic";
  };

  return (
    <div onKeyDown={handleKeyDown} tabIndex={-1} className="outline-none">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <div className="flex items-center gap-4">
            <Button variant="outline" onClick={onBack}>← Back</Button>
            <div>
              <CardTitle>{getTemplateTitle()}</CardTitle>
              <p className="text-sm text-muted-foreground">
                {isEditing ? "Modify your register entry form template" : "Create and customize your register entry form"}
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Card className="bg-white border border-gray-200">
            <CardContent className="p-6">
              <div className="space-y-6">
                {/* Top Row: Supplier and Party */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Supplier Field */}
                  <div className="space-y-2">
                    <Label htmlFor="supplier">Supplier</Label>
                    <Popover open={supplierOpen} onOpenChange={setSupplierOpen}>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          role="combobox"
                          aria-expanded={supplierOpen}
                          className="w-full justify-between"
                        >
                          {formData.supplier
                            ? suppliers.find((supplier) => supplier.value === formData.supplier)?.label
                            : "Select supplier..."}
                          <Search className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-full p-0">
                        <Command>
                          <CommandInput placeholder="Search supplier..." />
                          <CommandList>
                            <CommandEmpty>No supplier found.</CommandEmpty>
                            <CommandGroup>
                              {suppliers.map((supplier) => (
                                <CommandItem
                                  key={supplier.value}
                                  value={supplier.value}
                                  onSelect={(currentValue) => {
                                    setFormData({ ...formData, supplier: currentValue });
                                    setSupplierOpen(false);
                                  }}
                                >
                                  {supplier.label}
                                </CommandItem>
                              ))}
                            </CommandGroup>
                          </CommandList>
                        </Command>
                      </PopoverContent>
                    </Popover>
                  </div>

                  {/* Party Field */}
                  <div className="space-y-2">
                    <Label htmlFor="party">Party</Label>
                    <Popover open={partyOpen} onOpenChange={setPartyOpen}>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          role="combobox"
                          aria-expanded={partyOpen}
                          className="w-full justify-between"
                        >
                          {formData.party
                            ? parties.find((party) => party.value === formData.party)?.label
                            : "Select party..."}
                          <Search className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-full p-0">
                        <Command>
                          <CommandInput placeholder="Search party..." />
                          <CommandList>
                            <CommandEmpty>No party found.</CommandEmpty>
                            <CommandGroup>
                              {parties.map((party) => (
                                <CommandItem
                                  key={party.value}
                                  value={party.value}
                                  onSelect={(currentValue) => {
                                    setFormData({ ...formData, party: currentValue });
                                    setPartyOpen(false);
                                  }}
                                >
                                  {party.label}
                                </CommandItem>
                              ))}
                            </CommandGroup>
                          </CommandList>
                        </Command>
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>

                {/* Bottom Row: Bill Number, Register Date, Amount, and GST (if applicable) */}
                <div className={`grid grid-cols-1 gap-6 ${isGSTTemplate ? 'md:grid-cols-2 lg:grid-cols-4' : 'md:grid-cols-3'}`}>
                  {/* Bill Number Field */}
                  <div className="space-y-2">
                    <Label htmlFor="billNumber">Bill Number</Label>
                    <Input
                      id="billNumber"
                      type="text"
                      placeholder="Enter bill number"
                      value={formData.billNumber}
                      onChange={(e) => setFormData({ ...formData, billNumber: e.target.value })}
                      className="w-full"
                    />
                  </div>

                  {/* Register Date Field */}
                  <div className="space-y-2">
                    <Label htmlFor="registerDate">Register Date</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !formData.registerDate && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {formData.registerDate ? format(formData.registerDate, "PPP") : "Pick a date"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={formData.registerDate}
                          onSelect={(date) => setFormData({ ...formData, registerDate: date })}
                          initialFocus
                          className="pointer-events-auto"
                        />
                      </PopoverContent>
                    </Popover>
                  </div>

                  {/* Amount Field */}
                  <div className="space-y-2">
                    <Label htmlFor="amount">Amount</Label>
                    <Input
                      id="amount"
                      type="number"
                      placeholder="0.00"
                      value={formData.amount}
                      onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                      className="w-full"
                      step="0.01"
                      min="0"
                    />
                  </div>

                  {/* GST Percentage Field - Only for GST template */}
                  {isGSTTemplate && (
                    <div className="space-y-2">
                      <Label htmlFor="gstPercentage">GST %</Label>
                      <Input
                        id="gstPercentage"
                        type="number"
                        placeholder="18"
                        value={formData.gstPercentage}
                        onChange={(e) => setFormData({ ...formData, gstPercentage: e.target.value })}
                        className="w-full"
                        step="0.01"
                        min="0"
                        max="100"
                      />
                    </div>
                  )}
                </div>

                {/* Extra Fields Section */}
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold mb-4">Add Custom Fields</h3>
                  
                  {/* Add New Field */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="space-y-2">
                      <Label htmlFor="newKey">Field Name</Label>
                      <Input
                        id="newKey"
                        value={newKey}
                        onChange={(e) => setNewKey(e.target.value)}
                        placeholder="Enter field name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="newValue">Field Value</Label>
                      <Input
                        id="newValue"
                        value={newValue}
                        onChange={(e) => setNewValue(e.target.value)}
                        placeholder="Enter field value"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>&nbsp;</Label>
                      <Button 
                        onClick={handleAddExtraField}
                        disabled={!newKey.trim() || !newValue.trim()}
                        className="w-full"
                      >
                        Add Field
                      </Button>
                    </div>
                  </div>

                  {/* Display Extra Fields */}
                  {extraFields.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="font-medium">Custom Fields:</h4>
                      {extraFields.map((field) => (
                        <div key={field.id} className="grid grid-cols-1 md:grid-cols-3 gap-4 p-3 bg-gray-50 rounded-lg">
                          <Input
                            value={field.key}
                            onChange={(e) => handleUpdateExtraField(field.id, e.target.value, field.value)}
                            placeholder="Field name"
                          />
                          <Input
                            value={field.value}
                            onChange={(e) => handleUpdateExtraField(field.id, field.key, e.target.value)}
                            placeholder="Field value"
                          />
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRemoveExtraField(field.id)}
                            className="w-full"
                          >
                            Remove
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col sm:flex-row gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleReset}
                    className="flex-1"
                  >
                    Reset Form <span className="ml-2 text-xs text-muted-foreground">(Alt+R)</span>
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleSaveDraft}
                    className="flex-1"
                  >
                    Save Draft <span className="ml-2 text-xs text-muted-foreground">(Alt+D)</span>
                  </Button>
                  <Button
                    type="submit"
                    onClick={handleSubmit}
                    className="flex-1 bg-blue-600 hover:bg-blue-700"
                  >
                    {extraFields.length > 0 ? 'Save as New Template' : (isEditing ? 'Update Template' : 'Submit Register Entry')} 
                    <span className="ml-2 text-xs text-blue-100">(Alt+S)</span>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </div>
  );
};

export default TemplateFormCreator;
