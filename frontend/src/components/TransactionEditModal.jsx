import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "./ui/dialog";
import { Alert, AlertDescription } from "./ui/alert";
import { AlertTriangle, Save, X } from 'lucide-react';
import api from '../services/api';

const TransactionEditModal = ({ 
  isOpen, 
  onClose, 
  transaction, 
  categories = [], 
  onTransactionUpdated 
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    type: 'expense',
    category_id: 1,
    amount: '',
    description: '',
    date: '',
    merchant: '',
    currency: 'INR'
  });

  // Initialize form data when transaction changes
  useEffect(() => {
    if (transaction) {
      setFormData({
        type: transaction.type || 'expense',
        category_id: transaction.category_id || 1,
        amount: transaction.amount?.toString() || '',
        description: transaction.description || '',
        date: transaction.date ? new Date(transaction.date).toISOString().split('T')[0] : '',
        merchant: transaction.merchant || '',
        currency: transaction.currency || 'INR'
      });
    }
  }, [transaction]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.amount || !formData.description) {
      setError('Amount and description are required');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Prepare update data
      const updates = {
        type: formData.type,
        category_id: parseInt(formData.category_id),
        amount: parseFloat(formData.amount),
        description: formData.description,
        date: new Date(formData.date + 'T00:00:00').toISOString(),
        merchant: formData.merchant,
        currency: formData.currency
      };

      const updatedTransaction = await api.updateTransaction(transaction.id, updates);
      
      // Notify parent component
      if (onTransactionUpdated) {
        onTransactionUpdated(updatedTransaction);
      }
      
      onClose();
    } catch (err) {
      console.error('Error updating transaction:', err);
      setError(err.response?.data?.detail || 'Failed to update transaction');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: formData.currency,
      minimumFractionDigits: 2,
    }).format(amount || 0);
  };

  if (!transaction) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Save className="h-5 w-5" />
            Edit Transaction
          </DialogTitle>
          <DialogDescription>
            Make changes to this transaction. Click save when you're done.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert className="border-red-200">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Transaction Type */}
          <div className="space-y-2">
            <Label htmlFor="type">Transaction Type</Label>
            <Select 
              value={formData.type} 
              onValueChange={(value) => handleInputChange('type', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="expense">
                  <span className="text-red-600">💸 Expense</span>
                </SelectItem>
                <SelectItem value="income">
                  <span className="text-green-600">💰 Income</span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Amount */}
          <div className="space-y-2">
            <Label htmlFor="amount">Amount</Label>
            <div className="relative">
              <Input
                id="amount"
                type="number"
                step="0.01"
                placeholder="Enter amount"
                value={formData.amount}
                onChange={(e) => handleInputChange('amount', e.target.value)}
                className="pr-20"
                required
              />
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-500">
                {formData.currency}
              </div>
            </div>
            {formData.amount && (
              <p className="text-xs text-gray-500">
                Preview: {formatCurrency(parseFloat(formData.amount))}
              </p>
            )}
          </div>

          {/* Currency */}
          <div className="space-y-2">
            <Label htmlFor="currency">Currency</Label>
            <Select 
              value={formData.currency} 
              onValueChange={(value) => handleInputChange('currency', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select currency" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="INR">🇮🇳 INR - Indian Rupee</SelectItem>
                <SelectItem value="USD">🇺🇸 USD - US Dollar</SelectItem>
                <SelectItem value="EUR">🇪🇺 EUR - Euro</SelectItem>
                <SelectItem value="GBP">🇬🇧 GBP - British Pound</SelectItem>
                <SelectItem value="JPY">🇯🇵 JPY - Japanese Yen</SelectItem>
                <SelectItem value="PHP">🇵🇭 PHP - Philippine Peso</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Category */}
          <div className="space-y-2">
            <Label htmlFor="category">Category</Label>
            <Select 
              value={formData.category_id.toString()} 
              onValueChange={(value) => handleInputChange('category_id', parseInt(value))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                {categories.map((category) => (
                  <SelectItem key={category.id} value={category.id.toString()}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              placeholder="Enter description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              required
            />
          </div>

          {/* Merchant */}
          <div className="space-y-2">
            <Label htmlFor="merchant">Merchant/Payee</Label>
            <Input
              id="merchant"
              placeholder="Enter merchant or payee name"
              value={formData.merchant}
              onChange={(e) => handleInputChange('merchant', e.target.value)}
            />
          </div>

          {/* Date */}
          <div className="space-y-2">
            <Label htmlFor="date">Date</Label>
            <Input
              id="date"
              type="date"
              value={formData.date}
              onChange={(e) => handleInputChange('date', e.target.value)}
              required
            />
          </div>

          <DialogFooter className="gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default TransactionEditModal;