import React, { useState, useEffect } from 'react';
import { MessageCircle, Phone, CheckCircle, AlertCircle, Copy, Send, Shield } from 'lucide-react';
import apiService from '../services/api';
import { useToast } from '../hooks/use-toast';
import PhoneVerification from './PhoneVerification';
import SMSDemo from './SMSDemo';

const WhatsAppIntegration = () => {
  const [whatsappData, setWhatsappData] = useState(null);
  const [phoneStatus, setPhoneStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [whatsappStatus, phoneVerificationStatus] = await Promise.all([
        apiService.getWhatsAppStatus(),
        apiService.getPhoneVerificationStatus()
      ]);
      setWhatsappData(whatsappStatus);
      setPhoneStatus(phoneVerificationStatus);
    } catch (error) {
      console.error('Error loading data:', error);
      toast({
        title: "Error",
        description: "Failed to load WhatsApp integration status",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied!",
      description: "Copied to clipboard",
      variant: "default",
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <MessageCircle className="h-12 w-12 text-green-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-900">WhatsApp Integration</h2>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Forward your bank SMS messages to our WhatsApp number for automatic transaction processing. 
          It's FREE and works instantly!
        </p>
      </div>

      {/* Phone Verification Required */}
      {!phoneStatus?.phone_verified && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
          <div className="flex items-center justify-center mb-4">
            <Shield className="h-8 w-8 text-orange-600 mr-3" />
            <h3 className="text-lg font-semibold text-orange-800">Phone Verification Required</h3>
          </div>
          <p className="text-orange-700 text-center mb-6">
            To securely process your SMS forwards, please verify your phone number first.
          </p>
          <PhoneVerification />
        </div>
      )}

      {/* WhatsApp Features (only show when phone is verified) */}
      {phoneStatus?.phone_verified && (
        <>
          {/* WhatsApp Number Card */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-green-800 flex items-center">
                  <Phone className="h-5 w-5 mr-2" />
                  WhatsApp Number
                </h3>
                <p className="text-2xl font-bold text-green-900 mt-2">
                  {whatsappData?.whatsapp_number}
                </p>
                <p className="text-sm text-green-700 mt-1">
                  Your verified number: <span className="font-mono bg-green-100 px-2 py-1 rounded">
                    {phoneStatus?.phone_number}
                  </span>
                </p>
              </div>
              <button
                onClick={() => copyToClipboard(whatsappData?.whatsapp_number)}
                className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center hover:bg-green-700 transition-colors"
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy Number
              </button>
            </div>
          </div>

          {/* Setup Instructions */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <CheckCircle className="h-5 w-5 mr-2 text-blue-600" />
              How to Use (Phone Verified ✅)
            </h3>
            <div className="space-y-3">
              <div className="flex items-start">
                <div className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold mr-3 mt-0.5">
                  1
                </div>
                <p className="text-gray-700">Forward any bank SMS to <strong>{whatsappData?.whatsapp_number}</strong> on WhatsApp</p>
              </div>
              <div className="flex items-start">
                <div className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold mr-3 mt-0.5">
                  2
                </div>
                <p className="text-gray-700">Your SMS will be processed automatically within seconds</p>
              </div>
              <div className="flex items-start">
                <div className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold mr-3 mt-0.5">
                  3
                </div>
                <p className="text-gray-700">Transaction appears in your dashboard instantly</p>
              </div>
              <div className="flex items-start">
                <div className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold mr-3 mt-0.5">
                  4
                </div>
                <p className="text-gray-700">Get WhatsApp confirmation message with transaction details</p>
              </div>
            </div>
          </div>

          {/* Supported Banks */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-800 mb-3">Supported Banks</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {whatsappData?.supported_banks?.map((bank, index) => (
                <div key={index} className="bg-blue-100 text-blue-800 px-3 py-2 rounded-lg text-center font-medium">
                  {bank}
                </div>
              ))}
            </div>
          </div>

        </>
      )}

      {/* How it Works */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-yellow-800 mb-3">Security & Privacy</h3>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-yellow-700">
          <div>
            <h4 className="font-semibold mb-2">🔐 Secure Processing</h4>
            <p>Only verified phone numbers can forward SMS messages</p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">👤 User Isolation</h4>
            <p>Your transactions are private and isolated to your account</p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">⚡ Instant Processing</h4>
            <p>SMS parsed and transactions created in real-time</p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">🇮🇳 Built for India</h4>
            <p>Supports all major Indian banks and payment systems</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WhatsAppIntegration;