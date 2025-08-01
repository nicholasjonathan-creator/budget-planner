import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { TrendingUp, TrendingDown, MessageSquare, Edit, Tag, Calendar, Building, ChevronDown, ChevronUp, Info, Smartphone, Trash2, Edit3 } from 'lucide-react';
import TransactionEditModal from './TransactionEditModal';
import ApiService from '../services/api';
import { useToast } from '../hooks/use-toast';

const TransactionList = ({ transactions, categories, onTransactionUpdate, showDetailedView = false }) => {
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [updatingTransaction, setUpdatingTransaction] = useState(null);
  const [expandedTransactions, setExpandedTransactions] = useState(new Set());
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [transactionToDelete, setTransactionToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
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

  const handleEditTransaction = (transaction) => {
    setSelectedTransaction(transaction);
    setShowEditModal(true);
  };

  const handleDeleteTransaction = (transaction) => {
    setTransactionToDelete(transaction);
    setShowDeleteDialog(true);
  };

  const confirmDeleteTransaction = async () => {
    if (!transactionToDelete) return;

    try {
      setDeleting(true);
      await ApiService.deleteTransaction(transactionToDelete.id);
      
      toast({
        title: "Success",
        description: "Transaction deleted successfully!",
      });

      setShowDeleteDialog(false);
      setTransactionToDelete(null);
      
      if (onTransactionUpdate) {
        await onTransactionUpdate();
      }
    } catch (error) {
      console.error('Error deleting transaction:', error);
      toast({
        title: "Error", 
        description: "Failed to delete transaction. Please try again.",
        variant: "destructive",
      });
    } finally {
      setDeleting(false);
    }
  };

  const handleTransactionUpdated = async (updatedTransaction) => {
    toast({
      title: "Success",
      description: "Transaction updated successfully!",
    });

    if (onTransactionUpdate) {
      await onTransactionUpdate();
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
              <div key={transaction.id}>
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
                            <button
                              onClick={() => toggleTransactionDetails(transaction.id)}
                              className="ml-auto p-2 hover:bg-blue-100 rounded-full border border-blue-300 bg-blue-50"
                              title="Click to view original SMS details"
                            >
                              {isExpanded ? (
                                <ChevronUp className="h-4 w-4 text-blue-600" />
                              ) : (
                                <ChevronDown className="h-4 w-4 text-blue-600" />
                              )}
                            </button>
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
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditTransaction(transaction)}
                            disabled={isUpdating}
                            title="Edit transaction"
                          >
                            <Edit3 className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteTransaction(transaction)}
                            disabled={isUpdating}
                            title="Delete transaction"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setEditingTransaction(transaction.id)}
                            disabled={isUpdating}
                            title="Quick category edit"
                          >
                            <Tag className="h-3 w-3" />
                          </Button>
                        </div>
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
                  {hasSMSData && showDetailedView && isExpanded && (
                    <div className="px-4 pb-4 border-t bg-gradient-to-r from-blue-50 to-indigo-50">
                      <div className="pt-4 space-y-3">
                        <div className="flex items-start gap-3">
                          <Smartphone className="h-5 w-5 text-blue-600 mt-1 flex-shrink-0" />
                          <div className="flex-1">
                            <h4 className="text-sm font-semibold text-blue-800 mb-3">📱 Original SMS Transaction Details</h4>
                            
                            {transaction.raw_data?.sms_text && (
                              <div className="bg-white p-4 rounded-lg border-l-4 border-blue-500 shadow-sm text-sm mb-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <strong className="text-blue-700">Original SMS Message:</strong>
                                  <Badge variant="outline" className="text-xs bg-blue-100 text-blue-800">
                                    {transaction.raw_data.bank || 'Bank SMS'}
                                  </Badge>
                                </div>
                                <div className="bg-gray-50 p-3 rounded border font-mono text-xs text-gray-800 leading-relaxed">
                                  {transaction.raw_data.sms_text}
                                </div>
                              </div>
                            )}
                            
                            <div className="grid grid-cols-2 gap-4 text-xs">
                              {transaction.raw_data?.phone_number && (
                                <div className="bg-white p-3 rounded border">
                                  <span className="font-medium text-gray-600 block mb-1">📞 From Number:</span>
                                  <p className="text-gray-800 font-semibold">{transaction.raw_data.phone_number}</p>
                                </div>
                              )}
                              
                              {transaction.raw_data?.bank && (
                                <div className="bg-white p-3 rounded border">
                                  <span className="font-medium text-gray-600 block mb-1">🏦 Bank:</span>
                                  <p className="text-gray-800 font-semibold">{transaction.raw_data.bank}</p>
                                </div>
                              )}
                              
                              {transaction.raw_data?.parsing_method && (
                                <div className="bg-white p-3 rounded border">
                                  <span className="font-medium text-gray-600 block mb-1">⚙️ Parsing Method:</span>
                                  <p className="text-gray-800 font-semibold">{transaction.raw_data.parsing_method}</p>
                                </div>
                              )}
                              
                              {transaction.raw_data?.parsed_at && (
                                <div className="bg-white p-3 rounded border">
                                  <span className="font-medium text-gray-600 block mb-1">🕒 Processed At:</span>
                                  <p className="text-gray-800 font-semibold">
                                    {new Date(transaction.raw_data.parsed_at).toLocaleDateString('en-IN', {
                                      day: '2-digit',
                                      month: '2-digit', 
                                      year: 'numeric',
                                      hour: '2-digit',
                                      minute: '2-digit'
                                    })}
                                  </p>
                                </div>
                              )}
                            </div>
                            
                            {transaction.source === 'sms_manual' && transaction.raw_data?.manual_classification && (
                              <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-lg text-sm">
                                <div className="flex items-center gap-2">
                                  <Info className="h-4 w-4 text-orange-600 flex-shrink-0" />
                                  <span className="text-orange-800 font-medium">Manual Classification</span>
                                </div>
                                <p className="text-orange-700 mt-1 text-xs">
                                  This transaction was manually classified because the automatic SMS parser couldn't determine the transaction type.
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>

      {/* Transaction Edit Modal */}
      <TransactionEditModal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        transaction={selectedTransaction}
        categories={categories}
        onTransactionUpdated={handleTransactionUpdated}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="sm:max-w-[400px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Trash2 className="h-5 w-5 text-red-600" />
              Delete Transaction
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this transaction? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>

          {transactionToDelete && (
            <div className="py-4">
              <div className="p-4 bg-gray-50 rounded-lg border">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium">{transactionToDelete.description}</div>
                    <div className="text-sm text-gray-600">
                      {new Date(transactionToDelete.date).toLocaleDateString('en-IN', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric'
                      })}
                    </div>
                  </div>
                  <div className={`font-bold ${transactionToDelete.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                    {transactionToDelete.type === 'income' ? '+' : '-'}₹{transactionToDelete.amount.toLocaleString('en-IN')}
                  </div>
                </div>
              </div>
            </div>
          )}

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(false)}
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDeleteTransaction}
              disabled={deleting}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              {deleting ? 'Deleting...' : 'Delete Transaction'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
};

export default TransactionList;