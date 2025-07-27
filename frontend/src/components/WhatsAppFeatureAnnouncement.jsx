import React, { useState, useEffect } from 'react';
import { MessageCircle, X, ArrowRight, Sparkles } from 'lucide-react';
import apiService from '../services/api';

const WhatsAppFeatureAnnouncement = () => {
  const [show, setShow] = useState(false);
  const [phoneStatus, setPhoneStatus] = useState(null);

  useEffect(() => {
    checkAndShowAnnouncement();
  }, []);

  const checkAndShowAnnouncement = async () => {
    try {
      // Check if user has already seen this announcement
      const announcementSeen = localStorage.getItem('whatsapp_feature_announced');
      if (announcementSeen) return;

      // Check phone verification status
      const status = await apiService.getPhoneVerificationStatus();
      setPhoneStatus(status);

      // Show announcement only if phone not verified
      if (!status.phone_verified) {
        setShow(true);
      } else {
        // If already verified, mark as seen
        localStorage.setItem('whatsapp_feature_announced', 'true');
      }
    } catch (error) {
      console.error('Error checking WhatsApp feature status:', error);
    }
  };

  const handleDismiss = () => {
    setShow(false);
    localStorage.setItem('whatsapp_feature_announced', 'true');
  };

  const handleGetStarted = () => {
    // Navigate to WhatsApp tab (you might need to implement this based on your routing)
    const whatsappTab = document.querySelector('[data-tab="whatsapp"]');
    if (whatsappTab) {
      whatsappTab.click();
    }
    setShow(false);
    localStorage.setItem('whatsapp_feature_announced', 'true');
  };

  if (!show) return null;

  return (
    <div className="fixed top-4 right-4 z-40 max-w-sm bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-lg shadow-2xl border border-green-400 animate-slide-in-right">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center">
            <Sparkles className="h-5 w-5 text-yellow-300 mr-2" />
            <span className="font-bold text-sm">NEW FEATURE!</span>
          </div>
          <button
            onClick={handleDismiss}
            className="text-white/70 hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        <div className="mb-4">
          <div className="flex items-center mb-2">
            <MessageCircle className="h-6 w-6 text-green-200 mr-2" />
            <h3 className="font-bold text-lg">WhatsApp SMS Integration</h3>
          </div>
          <p className="text-sm text-white/90 mb-3">
            Forward your bank SMS messages to WhatsApp for automatic transaction tracking - it's FREE and instant!
          </p>
          <div className="bg-white/20 rounded-lg p-3 mb-3">
            <p className="text-xs text-white/95 font-medium mb-1">🚀 How it works:</p>
            <p className="text-xs text-white/90">
              1. Verify your phone number<br/>
              2. Forward bank SMS to our WhatsApp<br/>
              3. Transactions appear automatically!
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-2">
          <button
            onClick={handleGetStarted}
            className="w-full bg-white text-green-600 font-semibold py-2 px-4 rounded-lg hover:bg-green-50 transition-colors flex items-center justify-center"
          >
            <ArrowRight className="h-4 w-4 mr-2" />
            Set Up Now (2 mins)
          </button>
          <button
            onClick={handleDismiss}
            className="w-full text-white/80 text-sm hover:text-white transition-colors"
          >
            Maybe later
          </button>
        </div>
      </div>
    </div>
  );
};

export default WhatsAppFeatureAnnouncement;