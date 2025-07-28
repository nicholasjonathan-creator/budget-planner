import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { MessageSquare, Trash2, Copy, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import apiService from '../services/api';
import { useToast } from '../hooks/use-toast';

const SMSManagement = () => {
  const [smsList, setSmsList] = useState([]);
  const [duplicates, setDuplicates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showDuplicates, setShowDuplicates] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadSMSData();
  }, [currentPage]);

  const loadSMSData = async () => {
    try {
      setLoading(true);
      const response = await apiService.getSMSList(currentPage, 20);
      setSmsList(response.sms_list || []);
      setTotalPages(response.total_pages || 1);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load SMS data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadDuplicates = async () => {
    try {
      setProcessing(true);
      const response = await apiService.findDuplicateSMS();
      setDuplicates(response.duplicate_groups || []);
      setShowDuplicates(true);
      
      toast({
        title: "Duplicates Found",
        description: `Found ${response.duplicate_groups.length} duplicate groups`,
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to find duplicates",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleDeleteSMS = async (smsId) => {
    try {
      setProcessing(true);
      const response = await apiService.deleteSMS(smsId);
      
      if (response.success) {
        await loadSMSData();
        toast({
          title: "SMS Deleted",
          description: "SMS and associated transaction deleted successfully",
          variant: "default",
        });
      } else {
        throw new Error(response.message || 'Failed to delete SMS');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Failed to delete SMS",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleResolveDuplicate = async (smsHash, keepSmsId) => {
    try {
      setProcessing(true);
      const response = await apiService.resolveDuplicateSMS(smsHash, keepSmsId);
      
      if (response.success) {
        await loadDuplicates();
        await loadSMSData();
        toast({
          title: "Duplicates Resolved",
          description: response.message,
          variant: "default",
        });
      } else {
        throw new Error(response.message || 'Failed to resolve duplicates');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Failed to resolve duplicates",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const truncateMessage = (message, maxLength = 100) => {
    if (message.length <= maxLength) return message;
    return message.substring(0, maxLength) + '...';
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied",
      description: "Message copied to clipboard",
      variant: "default",
    });
  };

  if (loading) {
    return (
      <Card className="w-full max-w-6xl mx-auto">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2">Loading SMS data...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* SMS Management Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-blue-600" />
              SMS Management
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={loadDuplicates}
                disabled={processing}
                className="flex items-center gap-2"
              >
                <AlertTriangle className="h-4 w-4" />
                {processing ? 'Scanning...' : 'Find Duplicates'}
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowDuplicates(!showDuplicates)}
              >
                {showDuplicates ? 'Show All SMS' : 'Show Duplicates'}
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Duplicate SMS Management */}
      {showDuplicates && duplicates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Duplicate SMS Groups ({duplicates.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {duplicates.map((group, index) => (
                <div key={group.sms_hash} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <Badge variant="destructive">{group.count} duplicates</Badge>
                      <p className="text-sm text-gray-600 mt-1">
                        Hash: {group.sms_hash}
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(group.message)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  
                  <div className="bg-gray-50 rounded p-3 mb-3">
                    <p className="text-sm font-mono">
                      {truncateMessage(group.message, 200)}
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Choose which SMS to keep:</p>
                    <div className="grid gap-2">
                      {group.sms_ids.map((smsId, smsIndex) => (
                        <div key={smsId} className="flex items-center justify-between p-2 border rounded">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">SMS {smsIndex + 1}</Badge>
                            <span className="text-sm">
                              {new Date(group.timestamps[smsIndex]).toLocaleString()}
                            </span>
                          </div>
                          <Button
                            size="sm"
                            onClick={() => handleResolveDuplicate(group.sms_hash, smsId)}
                            disabled={processing}
                          >
                            Keep This
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* SMS List */}
      {!showDuplicates && (
        <Card>
          <CardHeader>
            <CardTitle>
              All SMS Messages ({smsList.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {smsList.map((sms) => (
                <div key={sms.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-2">
                      <Badge variant={sms.processed ? "default" : "secondary"}>
                        {sms.processed ? (
                          <>
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Processed
                          </>
                        ) : (
                          <>
                            <XCircle className="h-3 w-3 mr-1" />
                            Failed
                          </>
                        )}
                      </Badge>
                      <span className="text-sm text-gray-600">
                        From: {sms.phone_number}
                      </span>
                      <span className="text-sm text-gray-600">
                        {new Date(sms.timestamp).toLocaleString()}
                      </span>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(sms.message)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Delete SMS</AlertDialogTitle>
                            <AlertDialogDescription>
                              Are you sure you want to delete this SMS? This will also delete any associated transaction.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction 
                              onClick={() => handleDeleteSMS(sms.id)}
                              disabled={processing}
                            >
                              {processing ? 'Deleting...' : 'Delete'}
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 rounded p-3">
                    <p className="text-sm font-mono">
                      {sms.message}
                    </p>
                  </div>
                  
                  {sms.transaction_id && (
                    <div className="mt-2 text-sm text-green-600">
                      ✓ Transaction created: {sms.transaction_id}
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center gap-2 mt-6">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                
                <span className="flex items-center px-4 text-sm">
                  Page {currentPage} of {totalPages}
                </span>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SMSManagement;