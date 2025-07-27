import React, { useState, useEffect } from 'react';
import { Phone, Shield, CheckCircle, AlertCircle, Clock, Trash2 } from 'lucide-react';
import apiService from '../services/api';
import { useToast } from '../hooks/use-toast';

const PhoneVerification = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState('input'); // 'input', 'verify', 'verified'
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [phoneStatus, setPhoneStatus] = useState(null);
  const [statusLoading, setStatusLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadPhoneStatus();
  }, []);

  const loadPhoneStatus = async () => {
    try {
      setStatusLoading(true);
      const status = await apiService.getPhoneVerificationStatus();
      setPhoneStatus(status);
      
      if (status.phone_verified) {
        setStep('verified');
        setPhoneNumber(status.phone_number || '');
      }
    } catch (error) {
      console.error('Error loading phone status:', error);
    } finally {
      setStatusLoading(false);
    }
  };

  const handleSendVerification = async () => {
    if (!phoneNumber.trim()) {
      toast({
        title: "Error",
        description: "Please enter your phone number",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      await apiService.sendPhoneVerification({ phone_number: phoneNumber });
      
      toast({
        title: "Verification Sent!",
        description: "Check your WhatsApp for the verification code",
        variant: "default",
      });
      
      setStep('verify');
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to send verification code",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (!otp.trim()) {
      toast({
        title: "Error",
        description: "Please enter the verification code",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      await apiService.verifyPhoneOTP({ otp: otp });
      
      toast({
        title: "Success!",
        description: "Phone number verified successfully",
        variant: "default",
      });
      
      setStep('verified');
      await loadPhoneStatus();
    } catch (error) {
      toast({
        title: "Verification Failed",
        description: error.response?.data?.detail || "Invalid verification code",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    try {
      setResendLoading(true);
      await apiService.resendPhoneOTP();
      
      toast({
        title: "Code Resent",
        description: "New verification code sent to your WhatsApp",
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to resend verification code",
        variant: "destructive",
      });
    } finally {
      setResendLoading(false);
    }
  };

  const handleUnlinkPhone = async () => {
    if (!confirm('Are you sure you want to unlink your phone number? You will no longer be able to forward SMS messages.')) {
      return;
    }

    try {
      setLoading(true);
      await apiService.unlinkPhoneNumber();
      
      toast({
        title: "Phone Unlinked",
        description: "Your phone number has been removed from your account",
        variant: "default",
      });
      
      setStep('input');
      setPhoneNumber('');
      setOtp('');
      await loadPhoneStatus();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to unlink phone number",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (statusLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <Shield className="h-12 w-12 text-blue-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-900">Phone Verification</h2>
        </div>
        <p className="text-gray-600">
          Verify your phone number to securely receive WhatsApp SMS forwarding
        </p>
      </div>

      {/* Security Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <Shield className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-semibold mb-1">Security First</p>
            <p>Only verified phone numbers can forward SMS messages to ensure your transactions stay secure and private.</p>
          </div>
        </div>
      </div>

      {/* Verification Steps */}
      {step === 'input' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              WhatsApp Phone Number
            </label>
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+91 9876543210"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Include country code (e.g., +91 for India)
            </p>
          </div>

          <button
            onClick={handleSendVerification}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
            ) : (
              <Phone className="h-5 w-5 mr-2" />
            )}
            Send Verification Code
          </button>
        </div>
      )}

      {step === 'verify' && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
              <p className="text-sm text-green-800">
                Verification code sent to <strong>{phoneNumber}</strong>
              </p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter Verification Code
            </label>
            <input
              type="text"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="123456"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center text-2xl font-mono"
              maxLength={6}
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter the 6-digit code sent to your WhatsApp
            </p>
          </div>

          <div className="space-y-3">
            <button
              onClick={handleVerifyOTP}
              disabled={loading || otp.length !== 6}
              className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              ) : (
                <CheckCircle className="h-5 w-5 mr-2" />
              )}
              Verify Phone Number
            </button>

            <button
              onClick={handleResendOTP}
              disabled={resendLoading}
              className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              {resendLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
              ) : (
                <Clock className="h-4 w-4 mr-2" />
              )}
              Resend Code
            </button>
          </div>
        </div>
      )}

      {step === 'verified' && phoneStatus && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-green-800 mb-2">Phone Verified!</h3>
            <p className="text-green-700 mb-2">
              <strong>{phoneStatus.phone_number}</strong>
            </p>
            <p className="text-sm text-green-600">
              You can now forward bank SMS messages to WhatsApp for automatic processing.
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800 mb-2">How to Use:</h4>
            <ol className="text-sm text-blue-700 space-y-1">
              <li>1. Forward your bank SMS to +14155238886</li>
              <li>2. SMS will be processed automatically</li>
              <li>3. Transaction appears in your dashboard</li>
              <li>4. Get WhatsApp confirmation message</li>
            </ol>
          </div>

          <button
            onClick={handleUnlinkPhone}
            disabled={loading}
            className="w-full bg-red-100 text-red-700 py-2 px-4 rounded-lg hover:bg-red-200 disabled:bg-gray-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600 mr-2"></div>
            ) : (
              <Trash2 className="h-4 w-4 mr-2" />
            )}
            Unlink Phone Number
          </button>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h4 className="font-semibold text-yellow-800 mb-2">Important Notes:</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• Only verified numbers can receive SMS forwards</li>
          <li>• Each phone number can be linked to only one account</li>
          <li>• SMS processing happens instantly after verification</li>
          <li>• Your phone number is stored securely and never shared</li>
        </ul>
      </div>
    </div>
  );
};

export default PhoneVerification;