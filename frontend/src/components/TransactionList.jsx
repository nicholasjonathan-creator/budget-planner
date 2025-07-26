import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { TrendingUp, TrendingDown, MessageSquare, Edit, Tag, Calendar, Building, ChevronDown, ChevronUp, Info, Smartphone } from 'lucide-react';
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
      case 'sms_manual':
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
      case 'sms_manual':
        return 'bg-orange-100 text-orange-800';
      case 'email':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSourceLabel = (source) => {
    switch(source) {
      case 'sms':
        return 'SMS Auto';
      case 'sms_manual':
        return 'SMS Manual';
      case 'email':
        return 'Email';
      default:
        return 'Manual';
    }
  };

  const toggleTransactionDetails = (transactionId) => {
    const newExpanded = new Set(expandedTransactions);
    if (newExpanded.has(transactionId)) {
      newExpanded.delete(transactionId);
    } else {
      newExpanded.add(transactionId);
    }
    setExpandedTransactions(newExpanded);
  };

  const handleUpdateTransaction = async (transactionId, updates) => {
    try {
      setUpdatingTransaction(transactionId);
      await ApiService.updateTransaction(transactionId, updates);
      
      toast({
        title: "Success",
        description: "Transaction updated successfully!",
      });
      
      setEditingTransaction(null);
      if (onTransactionUpdate) {
        await onTransactionUpdate();
      }
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

    return (
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <span>{category?.name || 'Unknown'}</span>
        <span>•</span>
        <div className="flex items-center gap-1">
          <Calendar className="h-3 w-3" />
          <span>{date}</span>
        </div>
        {(transaction.source === 'sms' || transaction.source === 'sms_manual') && transaction.account_number && (
          <>
            <span>•</span>
            <div className="flex items-center gap-1">
              <Building className="h-3 w-3" />
              <span>A/C {transaction.account_number}</span>
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
            const isExpanded = expandedTransactions.has(transaction.id);
            const hasSMSData = transaction.source === 'sms' || transaction.source === 'sms_manual';
            
            return (
              <Collapsible key={transaction.id}>
                <div className="border rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between p-4">
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
                            {hasSMSData ? 
                              (transaction.merchant || `${transaction.type === 'income' ? 'Credit' : 'Debit'} Transaction`) 
                              : transaction.description
                            }
                          </p>
                          <div className="flex items-center gap-1">
                            {getSourceIcon(transaction.source)}
                            <Badge variant="outline" className={`text-xs ${getSourceColor(transaction.source)}`}>
                              {getSourceLabel(transaction.source)}
                            </Badge>
                          </div>
                          {hasSMSData && showDetailedView && (
                            <CollapsibleTrigger
                              onClick={() => toggleTransactionDetails(transaction.id)}
                              className="ml-auto p-1 hover:bg-gray-200 rounded"
                            >
                              {isExpanded ? (
                                <ChevronUp className="h-4 w-4 text-gray-500" />
                              ) : (
                                <ChevronDown className="h-4 w-4 text-gray-500" />
                              )}
                            </CollapsibleTrigger>
                          )}
                        </div>
                        {renderTransactionDetails(transaction)}
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className={`font-bold ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                          {transaction.type === 'income' ? '+' : '-'}₹{transaction.amount.toLocaleString('en-IN')}
                        </div>
                        {hasSMSData && transaction.account_number && (
                          <div className="text-xs text-gray-500">A/C: {transaction.account_number}</div>
                        )}
                      </div>

                      {!isEditing ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingTransaction(transaction.id)}
                          disabled={isUpdating}
                        >
                          <Tag className="h-3 w-3" />
                        </Button>
                      ) : (
                        <div className="flex items-center gap-2">
                          <Select 
                            value={category?.id?.toString() || ''} 
                            onValueChange={(value) => handleUpdateTransaction(transaction.id, { category_id: parseInt(value) })}
                          >
                            <SelectTrigger className="w-40">
                              <SelectValue placeholder="Category" />
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
                            variant="ghost"
                            size="sm"
                            onClick={() => setEditingTransaction(null)}
                          >
                            ✓
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Detailed SMS Information - Expandable */}
                  {hasSMSData && showDetailedView && (
                    <CollapsibleContent isOpen={isExpanded}>
                      <div className="px-4 pb-4 border-t bg-gray-50">
                        <div className="pt-3 space-y-3">
                          <div className="flex items-start gap-3">
                            <Smartphone className="h-4 w-4 text-blue-600 mt-1 flex-shrink-0" />
                            <div className="flex-1">
                              <h4 className="text-sm font-semibold text-gray-700 mb-2">SMS Transaction Details</h4>
                              
                              {transaction.raw_data?.sms_text && (
                                <div className="bg-white p-3 rounded border text-sm">
                                  <strong className="text-gray-600">Original SMS:</strong>
                                  <p className="mt-1 text-gray-800 whitespace-pre-wrap font-mono text-xs">
                                    {transaction.raw_data.sms_text}
                                  </p>
                                </div>
                              )}
                              
                              <div className="mt-3 grid grid-cols-2 gap-4 text-xs">
                                {transaction.raw_data?.phone_number && (
                                  <div>
                                    <span className="font-medium text-gray-600">From:</span>
                                    <p className="text-gray-800">{transaction.raw_data.phone_number}</p>
                                  </div>
                                )}
                                
                                {transaction.raw_data?.bank && (
                                  <div>
                                    <span className="font-medium text-gray-600">Bank:</span>
                                    <p className="text-gray-800">{transaction.raw_data.bank}</p>
                                  </div>
                                )}
                                
                                {transaction.raw_data?.parsing_method && (
                                  <div>
                                    <span className="font-medium text-gray-600">Parsing Method:</span>
                                    <p className="text-gray-800">{transaction.raw_data.parsing_method}</p>
                                  </div>
                                )}
                                
                                {transaction.raw_data?.parsed_at && (
                                  <div>
                                    <span className="font-medium text-gray-600">Processed:</span>
                                    <p className="text-gray-800">
                                      {new Date(transaction.raw_data.parsed_at).toLocaleDateString('en-IN')}
                                    </p>
                                  </div>
                                )}
                              </div>
                              
                              {transaction.source === 'sms_manual' && transaction.raw_data?.manual_classification && (
                                <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded text-xs">
                                  <Info className="h-3 w-3 inline text-orange-600 mr-1" />
                                  <span className="text-orange-800">This transaction was manually classified from a failed SMS parse.</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </CollapsibleContent>
                  )}
                </div>
              </Collapsible>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default TransactionList;