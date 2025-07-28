import React, { useState } from 'react';
import { AlertDialog, AlertDialogContent, AlertDialogDescription, AlertDialogHeader, AlertDialogTitle } from './ui/alert-dialog';
import { Button } from './ui/button';
import AccountConsolidation from './AccountConsolidation';

const AccountConsolidationModal = ({ isOpen, onClose, phoneNumber }) => {
  const [consolidationResult, setConsolidationResult] = useState(null);

  const handleConsolidationComplete = (action, result) => {
    setConsolidationResult({ action, result });
    
    // Close modal after 3 seconds
    setTimeout(() => {
      onClose();
      setConsolidationResult(null);
    }, 3000);
  };

  if (consolidationResult) {
    return (
      <AlertDialog open={isOpen} onOpenChange={onClose}>
        <AlertDialogContent className="max-w-2xl">
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              ✅ Consolidation Complete
            </AlertDialogTitle>
            <AlertDialogDescription>
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="text-green-800">
                    <strong>Success!</strong> {consolidationResult.result.message}
                  </div>
                  
                  {consolidationResult.action === 'transfer' && (
                    <div className="mt-3 text-sm text-green-700">
                      <div>📱 Phone number transferred successfully</div>
                      <div>🔗 WhatsApp integration is now enabled for your account</div>
                      <div>💬 You can now forward SMS messages to the WhatsApp number</div>
                    </div>
                  )}
                  
                  {consolidationResult.action === 'consolidate' && (
                    <div className="mt-3 text-sm text-green-700">
                      <div>🔄 Account consolidation completed</div>
                      <div>📊 All data has been merged into your current account</div>
                      <div>🔗 WhatsApp integration is now active</div>
                      
                      {consolidationResult.result.consolidation_results && (
                        <div className="mt-2 space-y-1">
                          <div>• {consolidationResult.result.consolidation_results.transactions_transferred} transactions transferred</div>
                          <div>• {consolidationResult.result.consolidation_results.sms_messages_transferred} SMS messages transferred</div>
                          <div>• {consolidationResult.result.consolidation_results.budget_limits_transferred} budget limits transferred</div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="text-center text-sm text-gray-600">
                  This modal will close automatically in a few seconds...
                </div>
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
        </AlertDialogContent>
      </AlertDialog>
    );
  }

  return (
    <AlertDialog open={isOpen} onOpenChange={onClose}>
      <AlertDialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center gap-2">
            🔗 Account Consolidation
          </AlertDialogTitle>
          <AlertDialogDescription>
            We found that phone number {phoneNumber} is associated with another account. 
            Choose how you'd like to handle this:
          </AlertDialogDescription>
        </AlertDialogHeader>
        
        <div className="mt-4">
          <AccountConsolidation 
            phoneNumber={phoneNumber} 
            onConsolidationComplete={handleConsolidationComplete}
          />
        </div>
        
        <div className="flex justify-end mt-6">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default AccountConsolidationModal;