import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { AlertCircle, CheckCircle, CreditCard, TrendingDown, TrendingUp } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import ApiService from '../services/api';

const ManualClassification = ({ onClassificationComplete }) => {
  const [failedSMS, setFailedSMS] = useState([]);
  const [loading, setLoading] = useState(true);
  const [classifying, setClassifying] = useState(null);
  const [classificationData, setClassificationData] = useState({
    sms_id: '',
    transaction_type: '',
    amount: '',
    description: ''
  });
  const { toast } = useToast();

  useEffect(() => {
    loadFailedSMS();
  }, []);

  const loadFailedSMS = async () => {
    try {
      setLoading(true);
      const response = await ApiService.getFailedSMS();
      if (response.success) {
        setFailedSMS(response.failed_sms || []);
      } else {
        toast({
          title: "Error",
          description: "Failed to load failed SMS messages",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error loading failed SMS:', error);
      toast({
        title: "Error",
        description: "Failed to load failed SMS messages",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClassifyClick = (sms) => {
    setClassifying(sms.id);
    setClassificationData({
      sms_id: sms.id,
      transaction_type: '',
      amount: '',
      description: ''
    });
  };

  const handleInputChange = (field, value) => {
    setClassificationData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmitClassification = async () => {
    if (!classificationData.transaction_type || !classificationData.amount) {
      toast({
        title: "Error",
        description: "Please select transaction type and enter amount",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await ApiService.manualClassifySMS(
        classificationData.sms_id,
        classificationData.transaction_type,
        parseFloat(classificationData.amount),
        classificationData.description
      );

      if (response.success) {
        toast({
          title: "Success",
          description: "SMS classified successfully!",
        });
        
        // Remove the classified SMS from the list
        setFailedSMS(prev => prev.filter(sms => sms.id !== classificationData.sms_id));
        setClassifying(null);
        setClassificationData({
          sms_id: '',
          transaction_type: '',
          amount: '',
          description: ''
        });
        
        // Notify parent component
        if (onClassificationComplete) {
          onClassificationComplete();
        }
      } else {
        toast({
          title: "Error",
          description: response.error || "Failed to classify SMS",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error classifying SMS:', error);
      toast({
        title: "Error",
        description: "Failed to classify SMS",
        variant: "destructive",
      });
    }
  };

  const handleCancelClassification = () => {
    setClassifying(null);
    setClassificationData({
      sms_id: '',
      transaction_type: '',
      amount: '',
      description: ''
    });
  };

  const extractAmountFromSMS = (smsText) => {
    // Try to extract amount from SMS text using regex
    const amountMatches = smsText.match(/(?:rs|inr|₹)\.?\s*([\d,]+(?:\.\d{2})?)/i);
    if (amountMatches) {
      return amountMatches[1].replace(/,/g, '');
    }
    return '';
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-yellow-600" />
            Manual Classification
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Loading failed SMS messages...</p>
        </CardContent>
      </Card>
    );
  }

  if (failedSMS.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            Manual Classification
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-green-600">🎉 All SMS messages have been processed successfully!</p>
          <p className="text-gray-500 text-sm mt-2">No failed messages require manual classification.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-yellow-600" />
          Manual Classification
          <Badge variant="secondary">{failedSMS.length} failed</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <p className="text-gray-600 text-sm">
            These SMS messages couldn't be automatically classified. Please manually specify if they are debit or credit transactions.
          </p>
          
          {failedSMS.map(sms => (
            <div key={sms.id} className="border rounded-lg p-4 space-y-3">
              <div className="bg-gray-50 p-3 rounded text-sm">
                <strong>SMS Message:</strong>
                <p className="mt-1">{sms.message}</p>
              </div>
              
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span>From: {sms.phone_number}</span>
                <span>•</span>
                <span>Time: {sms.timestamp || 'Unknown'}</span>
              </div>
              
              {classifying === sms.id ? (
                <div className="space-y-4 border-t pt-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="transaction_type">Transaction Type</Label>
                      <Select 
                        value={classificationData.transaction_type} 
                        onValueChange={(value) => handleInputChange('transaction_type', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="debit">
                            <div className="flex items-center gap-2">
                              <TrendingDown className="h-4 w-4 text-red-600" />
                              <span>Debit (Expense)</span>
                            </div>
                          </SelectItem>
                          <SelectItem value="credit">
                            <div className="flex items-center gap-2">
                              <TrendingUp className="h-4 w-4 text-green-600" />
                              <span>Credit (Income)</span>
                            </div>
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="amount">Amount (₹)</Label>
                      <Input
                        id="amount"
                        type="number"
                        step="0.01"
                        placeholder="Enter amount"
                        value={classificationData.amount}
                        onChange={(e) => handleInputChange('amount', e.target.value)}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="description">Description (Optional)</Label>
                    <Input
                      id="description"
                      placeholder="Enter description"
                      value={classificationData.description}
                      onChange={(e) => handleInputChange('description', e.target.value)}
                    />
                  </div>
                  
                  <div className="flex gap-2">
                    <Button 
                      onClick={handleSubmitClassification}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Classify
                    </Button>
                    <Button 
                      variant="outline"
                      onClick={handleCancelClassification}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-yellow-600">
                    {sms.reason}
                  </span>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleClassifyClick(sms)}
                  >
                    <CreditCard className="h-4 w-4 mr-2" />
                    Classify
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default ManualClassification;