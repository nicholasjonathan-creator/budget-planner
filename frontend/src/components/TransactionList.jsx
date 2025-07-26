import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { TrendingUp, TrendingDown, MessageSquare, Edit, Tag, Calendar, Building, CreditCard, ChevronDown, ChevronUp, Info, Smartphone } from 'lucide-react';
import ApiService from '../services/api';
import { useToast } from '../hooks/use-toast';

const TransactionList = ({ transactions, categories, onTransactionUpdate, showDetailedView = false }) => {
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [updatingTransaction, setUpdatingTransaction] = useState(null);
  const [expandedTransactions, setExpandedTransactions] = useState(new Set());
  const { toast } = useToast();

  const getCategoryById = (categoryId) => {
    return categories.find(cat => cat.id === categoryId);
  };

  const getSourceIcon = (source) => {
    switch(source) {
      case 'sms':
        return <MessageSquare className="h-4 w-4 text-blue-600" />;
      case 'email':
        return <Edit className="h-4 w-4 text-purple-600" />;
      default:
        return <Edit className="h-4 w-4 text-gray-600" />;
    }
  };

  const getSourceColor = (source) => {
    switch(source) {
      case 'sms':
        return 'bg-blue-100 text-blue-800';
      case 'email':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleUpdateTransaction = async (transactionId, updates) => {
    try {
      setUpdatingTransaction(transactionId);
      await ApiService.updateTransaction(transactionId, updates);
      
      toast({
        title: "Success",
        description: "Transaction updated successfully!",
      });
      
      if (onTransactionUpdate) {
        onTransactionUpdate();
      }
      
      setEditingTransaction(null);
    } catch (error) {
      console.error('Error updating transaction:', error);
      toast({
        title: "Error",
        description: "Failed to update transaction. Please try again.",
        variant: "destructive",
      });
    } finally {
      setUpdatingTransaction(null);
    }
  };

  const renderTransactionDetails = (transaction) => {
    const category = getCategoryById(transaction.category_id);
    const date = new Date(transaction.date).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: '2-digit', 
      year: 'numeric'
    });
    
    const time = new Date(transaction.date).toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit'
    });

    return (
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <span>{category?.name || 'Unknown'}</span>
        <span>•</span>
        <div className="flex items-center gap-1">
          <Calendar className="h-3 w-3" />
          <span>{date}</span>
        </div>
        {transaction.source === 'sms' && (
          <>
            <span>•</span>
            <div className="flex items-center gap-1">
              <Building className="h-3 w-3" />
              <span>{transaction.account_number ? `A/C ${transaction.account_number}` : 'Unknown'}</span>
            </div>
          </>
        )}
        {transaction.merchant && (
          <>
            <span>•</span>
            <span className="font-medium">{transaction.merchant}</span>
          </>
        )}
        {transaction.balance && (
          <>
            <span>•</span>
            <span className="text-green-600">Bal: ₹{transaction.balance.toLocaleString('en-IN')}</span>
          </>
        )}
      </div>
    );
  };

  if (transactions.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-gray-500">No transactions found for this period.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Transactions
          <Badge variant="secondary">{transactions.length}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {transactions.map(transaction => {
            const category = getCategoryById(transaction.category_id);
            const isEditing = editingTransaction === transaction.id;
            const isUpdating = updatingTransaction === transaction.id;
            
            return (
              <div 
                key={transaction.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1">
                  <div className="flex items-center gap-2">
                    {transaction.type === 'income' ? (
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-600" />
                    )}
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: category?.color || '#gray' }}
                    ></div>
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium">
                        {transaction.source === 'sms' ? 
                          (transaction.merchant || `${transaction.type === 'income' ? 'Credit' : 'Debit'} Transaction`) 
                          : transaction.description
                        }
                      </p>
                      <div className="flex items-center gap-1">
                        {getSourceIcon(transaction.source)}
                        <Badge variant="outline" className={`text-xs ${getSourceColor(transaction.source)}`}>
                          {transaction.source.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                    
                    {renderTransactionDetails(transaction)}
                    
                    {isEditing && (
                      <div className="mt-3 flex items-center gap-2">
                        <Select
                          value={transaction.category_id.toString()}
                          onValueChange={(value) => {
                            handleUpdateTransaction(transaction.id, { category_id: parseInt(value) });
                          }}
                        >
                          <SelectTrigger className="w-48">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {categories.map(cat => (
                              <SelectItem key={cat.id} value={cat.id.toString()}>
                                <div className="flex items-center gap-2">
                                  <div 
                                    className="w-3 h-3 rounded-full"
                                    style={{ backgroundColor: cat.color }}
                                  ></div>
                                  {cat.name}
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => setEditingTransaction(null)}
                        >
                          Cancel
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setEditingTransaction(isEditing ? null : transaction.id)}
                    disabled={isUpdating}
                  >
                    <Tag className="h-4 w-4" />
                  </Button>
                  
                  <div className="text-right">
                    <p className={`font-bold ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                      {transaction.type === 'income' ? '+' : '-'}₹{transaction.amount.toLocaleString('en-IN')}
                    </p>
                    {transaction.source === 'sms' && transaction.raw_data?.bank && (
                      <p className="text-xs text-gray-500">
                        {transaction.raw_data.bank}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default TransactionList;