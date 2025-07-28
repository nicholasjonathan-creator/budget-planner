import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { AlertTriangle, Download, Trash2, UserX } from 'lucide-react';
import apiService from '../services/api';
import { useToast } from '../hooks/use-toast';

const AccountDeletion = ({ onAccountDeleted }) => {
  const [accountData, setAccountData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [confirmationText, setConfirmationText] = useState('');
  const [deleteReason, setDeleteReason] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    loadAccountData();
  }, []);

  const loadAccountData = async () => {
    try {
      setLoading(true);
      const response = await apiService.getAccountDeletionPreview();
      setAccountData(response);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load account data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExportData = async () => {
    try {
      setProcessing(true);
      const response = await apiService.exportAccountData();
      
      if (response.success) {
        // Create download link
        const dataStr = JSON.stringify(response.data, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `budget_planner_data_${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
        
        toast({
          title: "Data Exported",
          description: "Your account data has been downloaded successfully",
          variant: "default",
        });
      } else {
        throw new Error(response.error || 'Export failed');
      }
    } catch (error) {
      toast({
        title: "Export Failed",
        description: error.message || "Failed to export account data",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleSoftDelete = async () => {
    try {
      setProcessing(true);
      const response = await apiService.softDeleteAccount(deleteReason);
      
      if (response.success) {
        toast({
          title: "Account Deactivated",
          description: response.message,
          variant: "default",
        });
        onAccountDeleted && onAccountDeleted('soft', response);
      } else {
        throw new Error(response.error || 'Soft delete failed');
      }
    } catch (error) {
      toast({
        title: "Deactivation Failed",
        description: error.message || "Failed to deactivate account",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleHardDelete = async () => {
    try {
      setProcessing(true);
      const response = await apiService.hardDeleteAccount(deleteReason, confirmationText);
      
      if (response.success) {
        toast({
          title: "Account Deleted",
          description: response.message,
          variant: "default",
        });
        onAccountDeleted && onAccountDeleted('hard', response);
      } else {
        throw new Error(response.error || 'Hard delete failed');
      }
    } catch (error) {
      toast({
        title: "Deletion Failed",
        description: error.message || "Failed to delete account",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2">Loading account data...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!accountData || accountData.error) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <div className="text-center text-red-600">
            ⚠️ {accountData?.error || "Failed to load account data"}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Account Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-yellow-600" />
            Account Deletion & Data Management
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">Account Information</h3>
              <div className="space-y-2 text-sm">
                <div><strong>Email:</strong> {accountData.email}</div>
                <div><strong>Username:</strong> {accountData.username || 'Not set'}</div>
                <div><strong>Created:</strong> {new Date(accountData.created_at).toLocaleDateString()}</div>
                <div><strong>Status:</strong> {accountData.is_active ? 'Active' : 'Inactive'}</div>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-3">Data Summary</h3>
              <div className="space-y-2 text-sm">
                <div><strong>Transactions:</strong> {accountData.data_summary.transactions_count}</div>
                <div><strong>SMS Messages:</strong> {accountData.data_summary.sms_count}</div>
                <div><strong>Budget Limits:</strong> {accountData.data_summary.budget_limits_count}</div>
                <div><strong>Phone Records:</strong> {accountData.data_summary.phone_records_count}</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Export */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5 text-blue-600" />
            Export Your Data
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 mb-4">
            Download a complete copy of your account data including transactions, SMS records, and settings.
          </p>
          <Button
            onClick={handleExportData}
            disabled={processing}
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            {processing ? 'Exporting...' : 'Export Data'}
          </Button>
        </CardContent>
      </Card>

      {/* Soft Delete */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserX className="h-5 w-5 text-orange-600" />
            Deactivate Account
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 mb-4">
            Temporarily deactivate your account. Your data will be preserved and you can reactivate later.
          </p>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="deactivateReason">Reason for deactivation (optional)</Label>
              <Input
                id="deactivateReason"
                value={deleteReason}
                onChange={(e) => setDeleteReason(e.target.value)}
                placeholder="Tell us why you're deactivating your account"
              />
            </div>
            
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="outline" className="flex items-center gap-2">
                  <UserX className="h-4 w-4" />
                  Deactivate Account
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Confirm Account Deactivation</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will temporarily deactivate your account. Your data will be preserved and you can reactivate by contacting support.
                    
                    <div className="mt-4 p-4 bg-blue-50 rounded-md">
                      <strong>What happens:</strong>
                      <ul className="list-disc ml-4 mt-2 text-sm">
                        <li>Your account will be temporarily disabled</li>
                        <li>All data will be preserved</li>
                        <li>You can request reactivation later</li>
                        <li>No data will be permanently deleted</li>
                      </ul>
                    </div>
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleSoftDelete} disabled={processing}>
                    {processing ? 'Deactivating...' : 'Deactivate Account'}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </CardContent>
      </Card>

      {/* Hard Delete */}
      <Card className="border-red-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <Trash2 className="h-5 w-5" />
            Permanently Delete Account
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
            <p className="text-red-800 font-medium">⚠️ This action cannot be undone!</p>
            <p className="text-red-700 text-sm mt-1">
              All your data including transactions, SMS records, and settings will be permanently deleted.
            </p>
          </div>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="deleteReason">Reason for deletion (optional)</Label>
              <Input
                id="deleteReason"
                value={deleteReason}
                onChange={(e) => setDeleteReason(e.target.value)}
                placeholder="Tell us why you're deleting your account"
              />
            </div>
            
            <div>
              <Label htmlFor="confirmationText">
                Type "PERMANENTLY DELETE MY ACCOUNT" to confirm
              </Label>
              <Input
                id="confirmationText"
                value={confirmationText}
                onChange={(e) => setConfirmationText(e.target.value)}
                placeholder="PERMANENTLY DELETE MY ACCOUNT"
              />
            </div>
            
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button 
                  variant="destructive" 
                  className="flex items-center gap-2"
                  disabled={confirmationText !== 'PERMANENTLY DELETE MY ACCOUNT'}
                >
                  <Trash2 className="h-4 w-4" />
                  Permanently Delete Account
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle className="text-red-600">
                    Confirm Permanent Account Deletion
                  </AlertDialogTitle>
                  <AlertDialogDescription>
                    <strong>This action cannot be undone!</strong>
                    
                    <div className="mt-4 p-4 bg-red-50 rounded-md">
                      <strong>What will be permanently deleted:</strong>
                      <ul className="list-disc ml-4 mt-2 text-sm">
                        <li>{accountData.data_summary.transactions_count} transactions</li>
                        <li>{accountData.data_summary.sms_count} SMS messages</li>
                        <li>{accountData.data_summary.budget_limits_count} budget limits</li>
                        <li>{accountData.data_summary.phone_records_count} phone records</li>
                        <li>All account settings and preferences</li>
                      </ul>
                    </div>
                    
                    <p className="mt-4 text-sm">
                      We recommend exporting your data before proceeding.
                    </p>
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction 
                    onClick={handleHardDelete} 
                    disabled={processing}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    {processing ? 'Deleting...' : 'Permanently Delete'}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AccountDeletion;