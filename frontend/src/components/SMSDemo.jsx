import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { X, MessageSquare, Zap, TrendingUp, TrendingDown } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import ApiService from '../services/api';

const SMSDemo = ({ onClose, onTransactionAdded }) => {
  const [phoneNumber, setPhoneNumber] = useState('+919876543210');
  const [message, setMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingResult, setProcessingResult] = useState(null);
  const [smsStats, setSmsStats] = useState({});
  const { toast } = useToast();

  const sampleMessages = [
    {
      bank: 'HDFC',
      message: 'Dear Customer, Rs 250.00 debited from your account ending 1234 at STARBUCKS COFFEE on 25-Jul-25. Available balance: Rs 15750.00'
    },
    {
      bank: 'SBI',
      message: 'Your account 1234 has been debited by Rs 120.50 for transaction at DOMINOS PIZZA on 25/07/2025. Balance: Rs 8879.50'
    },
    {
      bank: 'ICICI',
      message: 'Your card ending 9876 used for Rs 45.00 at UBER TRIP on 25-Jul-25. Available balance: Rs 3455.00'
    },
    {
      bank: 'Income',
      message: 'Rs 5000.00 credited to your account 5678 - SALARY PAYMENT on 01-Jul-25. Available balance: Rs 25000.00'
    }
  ];

  useEffect(() => {
    loadSmsStats();
  }, []);

  const loadSmsStats = async () => {
    try {
      const stats = await ApiService.getSmsStats();
      setSmsStats(stats);
    } catch (error) {
      console.error('Error loading SMS stats:', error);
    }
  };

  const handleProcessSms = async () => {
    if (!message.trim()) {
      toast({
        title: "Error",
        description: "Please enter an SMS message to process",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    setProcessingResult(null);

    try {
      const result = await ApiService.receiveSms(phoneNumber, message);
      setProcessingResult(result);
      
      if (result.success) {
        toast({
          title: "Success",
          description: "SMS processed and transaction added successfully!",
        });
        onTransactionAdded(); // Refresh parent data
      } else {
        toast({
          title: "Processing Failed",
          description: result.message || "Could not parse transaction from SMS",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error processing SMS:', error);
      toast({
        title: "Error",
        description: "Failed to process SMS. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
      loadSmsStats(); // Refresh stats
    }
  };

  const handleSimulateBank = async (bankType) => {
    setIsProcessing(true);
    setProcessingResult(null);

    try {
      const result = await ApiService.simulateBankSms(bankType);
      setProcessingResult(result);
      
      toast({
        title: "Success",
        description: `${result.messages_processed} sample ${bankType.toUpperCase()} transactions processed!`,
      });
      
      onTransactionAdded(); // Refresh parent data
    } catch (error) {
      console.error('Error simulating bank SMS:', error);
      toast({
        title: "Error",
        description: "Failed to simulate bank SMS. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
      loadSmsStats(); // Refresh stats
    }
  };

  const handleUseSample = (sampleMessage) => {
    setMessage(sampleMessage);
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={(e) => {
        // Close modal when clicking the overlay (but not the modal content)
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl font-bold flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            SMS Transaction Processing Demo
          </CardTitle>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onClose();
            }}
            className="h-8 w-8 p-0 hover:bg-gray-100"
          >
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-blue-900">{smsStats.total_sms || 0}</div>
                <p className="text-sm text-blue-600">Total SMS</p>
              </CardContent>
            </Card>
            <Card className="bg-green-50 border-green-200">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-green-900">{smsStats.processed_sms || 0}</div>
                <p className="text-sm text-green-600">Processed</p>
              </CardContent>
            </Card>
            <Card className="bg-purple-50 border-purple-200">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-purple-900">
                  {smsStats.success_rate ? `${smsStats.success_rate.toFixed(1)}%` : '0%'}
                </div>
                <p className="text-sm text-purple-600">Success Rate</p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Bank Simulation */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Quick Bank Simulation</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {['hdfc', 'sbi', 'icici'].map(bank => (
                <Button
                  key={bank}
                  onClick={() => handleSimulateBank(bank)}
                  disabled={isProcessing}
                  className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
                >
                  <Zap className="h-4 w-4 mr-2" />
                  Simulate {bank.toUpperCase()}
                </Button>
              ))}
            </div>
          </div>

          {/* Custom SMS Processing */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Test Custom SMS</h3>
            
            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+91XXXXXXXXXX"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="message">SMS Message</Label>
              <Textarea
                id="message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Paste your bank SMS here..."
                rows={4}
              />
            </div>

            <Button 
              onClick={handleProcessSms}
              disabled={isProcessing || !message.trim()}
              className="w-full bg-indigo-600 hover:bg-indigo-700"
            >
              {isProcessing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processing...
                </>
              ) : (
                <>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Process SMS
                </>
              )}
            </Button>
          </div>

          {/* Sample Messages */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Sample Messages</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {sampleMessages.map((sample, index) => (
                <Card key={index} className="border-l-4 border-l-indigo-500">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant="outline">{sample.bank}</Badge>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleUseSample(sample.message)}
                      >
                        Use Sample
                      </Button>
                    </div>
                    <p className="text-sm text-gray-600 truncate">{sample.message}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Processing Result */}
          {processingResult && (
            <Card className={`border-l-4 ${processingResult.success ? 'border-l-green-500 bg-green-50' : 'border-l-red-500 bg-red-50'}`}>
              <CardContent className="p-4">
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  {processingResult.success ? (
                    <>
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      Processing Successful
                    </>
                  ) : (
                    <>
                      <TrendingDown className="h-4 w-4 text-red-600" />
                      Processing Failed
                    </>
                  )}
                </h3>
                <p className="text-sm">{processingResult.message}</p>
                
                {processingResult.bank_type && (
                  <div className="mt-2">
                    <p className="text-sm font-medium">Bank: {processingResult.bank_type.toUpperCase()}</p>
                    <p className="text-sm">Messages Processed: {processingResult.messages_processed}</p>
                    <p className="text-sm">Success Rate: {processingResult.results?.filter(r => r.success).length || 0}/{processingResult.results?.length || 0}</p>
                  </div>
                )}
                
                {processingResult.transaction_id && (
                  <div className="mt-2">
                    <Badge variant="outline">Transaction ID: {processingResult.transaction_id}</Badge>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Info Section */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-4">
              <h3 className="font-semibold mb-2">How SMS Parsing Works</h3>
              <ul className="text-sm space-y-1 text-blue-800">
                <li>• Automatically detects transaction amounts and types (debit/credit)</li>
                <li>• Extracts merchant names and account information</li>
                <li>• Auto-categorizes transactions based on merchant keywords</li>
                <li>• Supports multiple bank SMS formats (HDFC, SBI, ICICI, etc.)</li>
                <li>• Stores raw SMS data for audit and reprocessing</li>
              </ul>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </div>
  );
};

export default SMSDemo;