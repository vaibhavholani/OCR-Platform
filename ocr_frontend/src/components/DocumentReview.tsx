
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Edit3 } from "lucide-react";
import { Document } from "@/types/document";

interface DocumentReviewProps {
  document: Document;
  onBack: () => void;
  onDocumentUpdate: (document: Document) => void;
}

const DocumentReview = ({ document, onBack, onDocumentUpdate }: DocumentReviewProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState(document.ocrData);
  const [documentStatus, setDocumentStatus] = useState(document.status);

  const handleSave = () => {
    const updatedDocument = {
      ...document,
      ocrData: editedData,
      status: documentStatus
    };
    onDocumentUpdate(updatedDocument);
    setIsEditing(false);
  };

  const handleApprove = () => {
    const approvedDocument = {
      ...document,
      status: 'ready_for_export' as const
    };
    setDocumentStatus('ready_for_export');
    onDocumentUpdate(approvedDocument);
  };

  const handleReject = () => {
    const rejectedDocument = {
      ...document,
      status: 'rejected' as const
    };
    setDocumentStatus('rejected');
    onDocumentUpdate(rejectedDocument);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'reviewing': return 'bg-blue-100 text-blue-800';
      case 'ready_for_export': return 'bg-green-100 text-green-800';
      case 'exported': return 'bg-gray-100 text-gray-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="outline" onClick={onBack}>← Back</Button>
              <div>
                <CardTitle>Document Review</CardTitle>
                <p className="text-sm text-muted-foreground">Review and edit extracted data</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge className={getStatusColor(documentStatus)}>
                {documentStatus.replace('_', ' ').toUpperCase()}
              </Badge>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
              >
                <Edit3 className="h-4 w-4 mr-2" />
                {isEditing ? 'Cancel' : 'Edit'}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Document Info */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Document Information</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <Label>File Name</Label>
                  <p className="font-medium">{document.name}</p>
                </div>
                <div>
                  <Label>Upload Date</Label>
                  <p>{new Date(document.uploadDate).toLocaleDateString()}</p>
                </div>
                <div>
                  <Label>Type</Label>
                  <p>{document.type}</p>
                </div>
                <div>
                  <Label>Template</Label>
                  <p>{document.templateType}</p>
                </div>
              </div>
            </div>

            {/* Extracted Data */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Extracted Data</h3>
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor="invoice_number">Invoice Number</Label>
                    {isEditing ? (
                      <Input
                        id="invoice_number"
                        value={editedData.invoice_number}
                        onChange={(e) => setEditedData({...editedData, invoice_number: e.target.value})}
                      />
                    ) : (
                      <p className="font-medium">{editedData.invoice_number}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="vendor_name">Vendor Name</Label>
                    {isEditing ? (
                      <Input
                        id="vendor_name"
                        value={editedData.vendor_name}
                        onChange={(e) => setEditedData({...editedData, vendor_name: e.target.value})}
                      />
                    ) : (
                      <p className="font-medium">{editedData.vendor_name}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor="invoice_date">Invoice Date</Label>
                    {isEditing ? (
                      <Input
                        id="invoice_date"
                        type="date"
                        value={editedData.invoice_date}
                        onChange={(e) => setEditedData({...editedData, invoice_date: e.target.value})}
                      />
                    ) : (
                      <p className="font-medium">{editedData.invoice_date}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="due_date">Due Date</Label>
                    {isEditing ? (
                      <Input
                        id="due_date"
                        type="date"
                        value={editedData.due_date}
                        onChange={(e) => setEditedData({...editedData, due_date: e.target.value})}
                      />
                    ) : (
                      <p className="font-medium">{editedData.due_date}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <Label htmlFor="subtotal">Subtotal</Label>
                    {isEditing ? (
                      <Input
                        id="subtotal"
                        value={editedData.subtotal}
                        onChange={(e) => setEditedData({...editedData, subtotal: e.target.value})}
                      />
                    ) : (
                      <p className="font-medium">${editedData.subtotal}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="tax_amount">Tax Amount</Label>
                    {isEditing ? (
                      <Input
                        id="tax_amount"
                        value={editedData.tax_amount}
                        onChange={(e) => setEditedData({...editedData, tax_amount: e.target.value})}
                      />
                    ) : (
                      <p className="font-medium">${editedData.tax_amount}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="total_amount">Total Amount</Label>
                    {isEditing ? (
                      <Input
                        id="total_amount"
                        value={editedData.total_amount}
                        onChange={(e) => setEditedData({...editedData, total_amount: e.target.value})}
                      />
                    ) : (
                      <p className="font-medium text-lg">${editedData.total_amount}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Line Items */}
          <div className="mt-6">
            <h3 className="text-lg font-medium mb-4">Line Items</h3>
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left">Description</th>
                    <th className="px-4 py-2 text-left">Quantity</th>
                    <th className="px-4 py-2 text-left">Unit Price</th>
                    <th className="px-4 py-2 text-left">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {editedData.line_items.map((item, index) => (
                    <tr key={index} className="border-t">
                      <td className="px-4 py-2">
                        {isEditing ? (
                          <Input
                            value={item.description}
                            onChange={(e) => {
                              const newItems = [...editedData.line_items];
                              newItems[index].description = e.target.value;
                              setEditedData({...editedData, line_items: newItems});
                            }}
                          />
                        ) : (
                          item.description
                        )}
                      </td>
                      <td className="px-4 py-2">
                        {isEditing ? (
                          <Input
                            type="number"
                            value={item.quantity}
                            onChange={(e) => {
                              const newItems = [...editedData.line_items];
                              newItems[index].quantity = parseInt(e.target.value);
                              setEditedData({...editedData, line_items: newItems});
                            }}
                          />
                        ) : (
                          item.quantity
                        )}
                      </td>
                      <td className="px-4 py-2">
                        {isEditing ? (
                          <Input
                            value={item.unit_price}
                            onChange={(e) => {
                              const newItems = [...editedData.line_items];
                              newItems[index].unit_price = e.target.value;
                              setEditedData({...editedData, line_items: newItems});
                            }}
                          />
                        ) : (
                          `$${item.unit_price}`
                        )}
                      </td>
                      <td className="px-4 py-2">
                        {isEditing ? (
                          <Input
                            value={item.total}
                            onChange={(e) => {
                              const newItems = [...editedData.line_items];
                              newItems[index].total = e.target.value;
                              setEditedData({...editedData, line_items: newItems});
                            }}
                          />
                        ) : (
                          `$${item.total}`
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 mt-6">
            {isEditing ? (
              <Button onClick={handleSave}>Save Changes</Button>
            ) : (
              <>
                {documentStatus !== 'ready_for_export' && documentStatus !== 'rejected' && (
                  <>
                    <Button variant="outline" onClick={handleReject}>
                      <XCircle className="h-4 w-4 mr-2" />
                      Reject
                    </Button>
                    <Button onClick={handleApprove}>
                      <CheckCircle2 className="h-4 w-4 mr-2" />
                      Approve
                    </Button>
                  </>
                )}
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DocumentReview;
