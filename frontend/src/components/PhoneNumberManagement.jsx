import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Phone, Edit, Trash2, History, CheckCircle, XCircle } from 'lucide-react';
import apiService from '../services/api';
import { useToast } from '../hooks/use-toast';

const PhoneNumberManagement = () => {
  const [phoneStatus, setPhoneStatus] = useState(null);
  const [phoneHistory, setPhoneHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [newPhoneNumber, setNewPhoneNumber] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [changeStep, setChangeStep] = useState('idle'); // 'idle', 'verify', 'complete'
  const [showHistory, setShowHistory] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadPhoneData();
  }, []);

  const loadPhoneData = async () => {
    try {
      setLoading(true);
      const [statusResponse, historyResponse] = await Promise.all([
        apiService.getPhoneStatus(),
        apiService.getPhoneHistory()
      ]);
      
      setPhoneStatus(statusResponse);
      setPhoneHistory(historyResponse.history || []);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load phone data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInitiatePhoneChange = async () => {
    if (!newPhoneNumber.trim()) {
      toast({
        title: "Error",
        description: "Please enter a new phone number",
        variant: "destructive",
      });
      return;
    }

    try {
      setProcessing(true);
      const response = await apiService.initiatePhoneChange(newPhoneNumber);
      
      if (response.success) {
        setChangeStep('verify');
        toast({
          title: "Verification Sent",
          description: response.message,
          variant: "default",
        });
      } else {
        if (response.requires_consolidation) {
          toast({
            title: "Phone Number Conflict",
            description: "This phone number is already associated with another account. Please use the account consolidation feature.",
            variant: "destructive",
          });
        } else {
          throw new Error(response.error || 'Failed to initiate phone change');
        }
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Failed to initiate phone number change",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleCompletePhoneChange = async () => {
    if (!verificationCode.trim()) {
      toast({
        title: "Error",
        description: "Please enter the verification code",
        variant: "destructive",
      });
      return;
    }

    try {
      setProcessing(true);
      const response = await apiService.completePhoneChange(newPhoneNumber, verificationCode);
      
      if (response.success) {
        setChangeStep('idle');
        setNewPhoneNumber('');
        setVerificationCode('');
        await loadPhoneData();
        
        toast({
          title: "Phone Number Updated",
          description: response.message,
          variant: "default",
        });
      } else {
        throw new Error(response.error || 'Failed to complete phone change');
      }
    } catch (error) {
      toast({
        title: "Verification Failed",
        description: error.message || "Failed to verify phone number",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleCancelPhoneChange = async () => {
    try {
      setProcessing(true);
      const response = await apiService.cancelPhoneChange(newPhoneNumber);
      
      if (response.success) {
        setChangeStep('idle');
        setNewPhoneNumber('');
        setVerificationCode('');
        
        toast({
          title: "Change Cancelled",
          description: "Phone number change has been cancelled",
          variant: "default",
        });
      } else {
        throw new Error(response.error || 'Failed to cancel phone change');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Failed to cancel phone change",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleRemovePhoneNumber = async () => {
    try {
      setProcessing(true);
      const response = await apiService.removePhoneNumber("User requested removal");
      
      if (response.success) {
        await loadPhoneData();
        toast({
          title: "Phone Number Removed",
          description: response.message,
          variant: "default",
        });
      } else {
        throw new Error(response.error || 'Failed to remove phone number');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Failed to remove phone number",
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
            <span className="ml-2">Loading phone data...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Current Phone Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Phone className="h-5 w-5 text-blue-600" />
            Current Phone Number
          </CardTitle>
        </CardHeader>
        <CardContent>
          {phoneStatus?.has_phone ? (
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="text-lg font-medium">{phoneStatus.phone_number}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant={phoneStatus.verified ? "default" : "secondary"}>
                      {phoneStatus.verified ? (
                        <>
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Verified
                        </>
                      ) : (
                        <>
                          <XCircle className="h-3 w-3 mr-1" />
                          Not Verified
                        </>
                      )}
                    </Badge>
                    {phoneStatus.verified_at && (
                      <span className="text-sm text-gray-500">
                        Verified on {new Date(phoneStatus.verified_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowHistory(!showHistory)}
                  >
                    <History className="h-4 w-4 mr-1" />
                    History
                  </Button>
                  
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="outline" size="sm">
                        <Trash2 className="h-4 w-4 mr-1" />
                        Remove
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Remove Phone Number</AlertDialogTitle>
                        <AlertDialogDescription>
                          Are you sure you want to remove your phone number? This will disable WhatsApp integration and SMS forwarding.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleRemovePhoneNumber} disabled={processing}>
                          {processing ? 'Removing...' : 'Remove Phone Number'}
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Phone className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">No phone number registered</p>
              <p className="text-sm text-gray-500 mt-1">
                Add a phone number to enable WhatsApp integration
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Phone Number Change */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Edit className="h-5 w-5 text-green-600" />
            {phoneStatus?.has_phone ? 'Change Phone Number' : 'Add Phone Number'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {changeStep === 'idle' && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="newPhoneNumber">New Phone Number</Label>
                <Input
                  id="newPhoneNumber"
                  value={newPhoneNumber}
                  onChange={(e) => setNewPhoneNumber(e.target.value)}
                  placeholder="+1234567890"
                  disabled={processing}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Include country code (e.g., +91 for India)
                </p>
              </div>
              
              <Button 
                onClick={handleInitiatePhoneChange}
                disabled={processing || !newPhoneNumber.trim()}
                className="flex items-center gap-2"
              >
                <Phone className="h-4 w-4" />
                {processing ? 'Sending...' : 'Send Verification Code'}
              </Button>
            </div>
          )}
          
          {changeStep === 'verify' && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <p className="text-blue-800 font-medium">Verification code sent to {newPhoneNumber}</p>
                <p className="text-blue-700 text-sm mt-1">
                  Please enter the verification code you received via SMS or WhatsApp
                </p>
              </div>
              
              <div>
                <Label htmlFor="verificationCode">Verification Code</Label>
                <Input
                  id="verificationCode"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder="Enter verification code"
                  disabled={processing}
                />
              </div>
              
              <div className="flex gap-2">
                <Button 
                  onClick={handleCompletePhoneChange}
                  disabled={processing || !verificationCode.trim()}
                  className="flex items-center gap-2"
                >
                  <CheckCircle className="h-4 w-4" />
                  {processing ? 'Verifying...' : 'Verify & Update'}
                </Button>
                
                <Button 
                  variant="outline"
                  onClick={handleCancelPhoneChange}
                  disabled={processing}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Phone History */}
      {showHistory && phoneHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5 text-purple-600" />
              Phone Number History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {phoneHistory.map((record, index) => (
                <div key={record.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant={record.change_status === 'completed' ? 'default' : 
                                      record.change_status === 'cancelled' ? 'destructive' : 'secondary'}>
                          {record.change_status}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {record.action || 'change'}
                        </span>
                      </div>
                      
                      <div className="text-sm space-y-1">
                        {record.old_phone_number && (
                          <div><strong>From:</strong> {record.old_phone_number}</div>
                        )}
                        {record.new_phone_number && (
                          <div><strong>To:</strong> {record.new_phone_number}</div>
                        )}
                        {record.reason && (
                          <div><strong>Reason:</strong> {record.reason}</div>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-right text-sm text-gray-500">
                      <div>
                        {new Date(record.change_initiated_at).toLocaleDateString()}
                      </div>
                      {record.change_completed_at && (
                        <div>
                          Completed: {new Date(record.change_completed_at).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PhoneNumberManagement;