import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';

const AccountConsolidation = ({ phoneNumber, onConsolidationComplete }) => {
  const [consolidationPreview, setConsolidationPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [processingAction, setProcessingAction] = useState(null);

  useEffect(() => {
    if (phoneNumber) {
      loadConsolidationPreview();
    }
  }, [phoneNumber]);

  const loadConsolidationPreview = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getConsolidationPreview(phoneNumber);
      setConsolidationPreview(response);
    } catch (err) {
      setError('Failed to load consolidation preview: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTransferPhoneOnly = async () => {
    setProcessingAction('transfer');
    setError(null);
    
    try {
      const response = await apiService.transferPhoneNumber(phoneNumber);
      
      if (response.success) {
        onConsolidationComplete && onConsolidationComplete('transfer', response);
      } else {
        setError(response.error || 'Failed to transfer phone number');
      }
    } catch (err) {
      setError('Failed to transfer phone number: ' + err.message);
    } finally {
      setProcessingAction(null);
    }
  };

  const handleFullConsolidation = async () => {
    setProcessingAction('consolidate');
    setError(null);
    
    try {
      const response = await apiService.consolidateAccounts(phoneNumber);
      
      if (response.success) {
        onConsolidationComplete && onConsolidationComplete('consolidate', response);
      } else {
        setError(response.error || 'Failed to consolidate accounts');
      }
    } catch (err) {
      setError('Failed to consolidate accounts: ' + err.message);
    } finally {
      setProcessingAction(null);
    }
  };

  if (loading) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2">Loading consolidation preview...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <div className="text-center">
            <div className="text-red-600 mb-4">⚠️ {error}</div>
            <Button onClick={loadConsolidationPreview} variant="outline">
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!consolidationPreview) {
    return null;
  }

  const { source_account, target_account, consolidation_plan } = consolidationPreview;

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🔗 Account Consolidation for {phoneNumber}
            <Badge variant="outline">{consolidation_plan.action}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            {/* Source Account */}
            <div>
              <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                📱 Phone Number Account
                <Badge variant="secondary">Source</Badge>
              </h3>
              <div className="space-y-2 text-sm">
                <div><strong>Email:</strong> {source_account.email}</div>
                <div><strong>Username:</strong> {source_account.username}</div>
                <div><strong>Phone:</strong> {source_account.phone_number}</div>
                <div><strong>Phone Verified:</strong> {source_account.phone_verified ? '✅ Yes' : '❌ No'}</div>
                <div><strong>Created:</strong> {new Date(source_account.created_at).toLocaleDateString()}</div>
              </div>
              
              <Separator className="my-4" />
              
              <div className="space-y-2 text-sm">
                <div><strong>Transactions:</strong> {source_account.transaction_count}</div>
                <div><strong>SMS Messages:</strong> {source_account.sms_count}</div>
                <div><strong>Budget Limits:</strong> {source_account.budget_limits_count}</div>
              </div>
              
              {source_account.recent_transactions && source_account.recent_transactions.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium mb-2">Recent Transactions:</h4>
                  <div className="space-y-1 text-xs">
                    {source_account.recent_transactions.map((transaction, index) => (
                      <div key={index} className="flex justify-between">
                        <span>{transaction.description}</span>
                        <span className={transaction.type === 'expense' ? 'text-red-600' : 'text-green-600'}>
                          ₹{transaction.amount}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Target Account */}
            <div>
              <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                👤 Your Current Account
                <Badge variant="default">Target</Badge>
              </h3>
              <div className="space-y-2 text-sm">
                <div><strong>Email:</strong> {target_account.email}</div>
                <div><strong>Username:</strong> {target_account.username}</div>
                <div><strong>Phone:</strong> {target_account.phone_number || 'Not set'}</div>
                <div><strong>Phone Verified:</strong> {target_account.phone_verified ? '✅ Yes' : '❌ No'}</div>
                <div><strong>Created:</strong> {new Date(target_account.created_at).toLocaleDateString()}</div>
              </div>
              
              <Separator className="my-4" />
              
              <div className="space-y-2 text-sm">
                <div><strong>Transactions:</strong> {target_account.transaction_count}</div>
                <div><strong>SMS Messages:</strong> {target_account.sms_count}</div>
                <div><strong>Budget Limits:</strong> {target_account.budget_limits_count}</div>
              </div>
              
              {target_account.recent_transactions && target_account.recent_transactions.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium mb-2">Recent Transactions:</h4>
                  <div className="space-y-1 text-xs">
                    {target_account.recent_transactions.map((transaction, index) => (
                      <div key={index} className="flex justify-between">
                        <span>{transaction.description}</span>
                        <span className={transaction.type === 'expense' ? 'text-red-600' : 'text-green-600'}>
                          ₹{transaction.amount}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Consolidation Options */}
      <Card>
        <CardHeader>
          <CardTitle>🎯 Consolidation Options</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Transfer Phone Only */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">Option 1: Transfer Phone Number Only</h3>
              <p className="text-sm text-gray-600 mb-3">
                Transfer the phone number {phoneNumber} to your current account. 
                The other account will remain separate with its data intact.
              </p>
              <p className="text-sm text-blue-600 mb-3">
                ✅ Quick and safe • ✅ Keep accounts separate • ✅ Enable WhatsApp for current account
              </p>
              
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button 
                    variant="outline" 
                    disabled={processingAction === 'transfer'}
                  >
                    {processingAction === 'transfer' ? 'Processing...' : 'Transfer Phone Number'}
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Confirm Phone Number Transfer</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will transfer the phone number {phoneNumber} to your current account ({target_account.email}).
                      
                      The other account will remain active but will lose access to WhatsApp integration.
                      
                      Are you sure you want to proceed?
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={handleTransferPhoneOnly}>
                      Yes, Transfer Phone Number
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>

            {/* Full Consolidation */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">Option 2: Full Account Consolidation</h3>
              <p className="text-sm text-gray-600 mb-3">
                Merge all data from the phone number account into your current account. 
                This includes transactions, SMS messages, and budget limits.
              </p>
              <p className="text-sm text-orange-600 mb-3">
                ⚠️ Permanent action • ⚠️ Other account will be deactivated
              </p>
              
              <div className="text-sm bg-gray-50 p-3 rounded mb-3">
                <strong>Data to be transferred:</strong>
                <ul className="list-disc ml-4 mt-1">
                  <li>{consolidation_plan.data_to_transfer.transactions} transactions</li>
                  <li>{consolidation_plan.data_to_transfer.sms_messages} SMS messages</li>
                  <li>{consolidation_plan.data_to_transfer.budget_limits} budget limits</li>
                  <li>Phone verification status</li>
                </ul>
              </div>
              
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button 
                    variant="destructive" 
                    disabled={processingAction === 'consolidate'}
                  >
                    {processingAction === 'consolidate' ? 'Processing...' : 'Full Account Consolidation'}
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Confirm Full Account Consolidation</AlertDialogTitle>
                    <AlertDialogDescription>
                      <strong>⚠️ This action cannot be undone!</strong>
                      
                      This will:
                      • Transfer ALL data from {source_account.email} to {target_account.email}
                      • Deactivate the source account ({source_account.email})
                      • Merge {consolidation_plan.data_to_transfer.transactions} transactions
                      • Merge {consolidation_plan.data_to_transfer.sms_messages} SMS messages
                      • Merge {consolidation_plan.data_to_transfer.budget_limits} budget limits
                      
                      Are you absolutely sure you want to proceed?
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={handleFullConsolidation}>
                      Yes, Consolidate All Data
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AccountConsolidation;