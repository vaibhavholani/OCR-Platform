
export interface Document {
  id: string;
  name: string;
  type: string;
  uploadDate: string;
  status: 'pending' | 'reviewing' | 'ready_for_export' | 'exported' | 'rejected';
  ocrData: {
    invoice_number: string;
    vendor_name: string;
    invoice_date: string;
    due_date: string;
    total_amount: string;
    subtotal: string;
    tax_amount: string;
    line_items: Array<{
      description: string;
      quantity: number;
      unit_price: string;
      total: string;
    }>;
  };
  templateType: string;
  file?: File;
  preview?: string;
}
