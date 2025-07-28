import axios from 'axios';
import Cookies from 'js-cookie';

// Use backend URL directly from environment variable
const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: `${API}/api`,
      timeout: 15000, // Increased timeout to 15 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for authentication and debugging
    this.client.interceptors.request.use(
      (config) => {
        // Add authentication token if available
        const token = Cookies.get('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling with retry logic
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        console.error('API Response Error:', error.response?.data || error.message);
        
        // Handle network errors with retry (for net::ERR_ABORTED issues)
        if (!error.response && !originalRequest._retry && originalRequest.method === 'get') {
          originalRequest._retry = true;
          console.log('Retrying failed GET request after network error...');
          
          // Wait 1 second before retry
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          try {
            return await this.client(originalRequest);
          } catch (retryError) {
            console.error('Retry also failed:', retryError.message);
          }
        }
        
        // Handle 401 errors (unauthorized) - potentially redirect to login
        if (error.response?.status === 401) {
          // Clear invalid auth data
          Cookies.remove('auth_token');
          Cookies.remove('auth_user');
          // Optionally redirect to login page
          // window.location.href = '/';
        }
        
        return Promise.reject(error);
      }
    );
  }

  // ==================== TRANSACTIONS ====================
  async getTransactions(month = null, year = null) {
    const params = {};
    if (month !== null) params.month = month;
    if (year !== null) params.year = year;
    
    const response = await this.client.get('/transactions', { params });
    return response.data;
  }

  async createTransaction(transaction) {
    const response = await this.client.post('/transactions', transaction);
    return response.data;
  }

  async getTransaction(id) {
    const response = await this.client.get(`/transactions/${id}`);
    return response.data;
  }

  async updateTransaction(id, updates) {
    const response = await this.client.put(`/transactions/${id}`, updates);
    return response.data;
  }

  async deleteTransaction(id) {
    const response = await this.client.delete(`/transactions/${id}`);
    return response.data;
  }

  // ==================== ANALYTICS ====================
  async getMonthlySummary(month, year) {
    const response = await this.client.get('/analytics/monthly-summary', {
      params: { month, year }
    });
    return response.data;
  }

  async getCategoryTotals(month, year) {
    const response = await this.client.get('/analytics/category-totals', {
      params: { month, year }
    });
    return response.data;
  }

  // ==================== BUDGET LIMITS ====================
  async getBudgetLimits(month, year) {
    const response = await this.client.get('/budget-limits', {
      params: { month, year }
    });
    return response.data;
  }

  async createBudgetLimit(budgetLimit) {
    const response = await this.client.post('/budget-limits', budgetLimit);
    return response.data;
  }

  // ==================== CATEGORIES ====================
  async getCategories() {
    const response = await this.client.get('/categories');
    return response.data;
  }

  // ==================== SMS ====================
  async receiveSms(phoneNumber, message) {
    const response = await this.client.post('/sms/receive', {
      phone_number: phoneNumber,
      message: message
    });
    return response.data;
  }

  async getUnprocessedSms() {
    const response = await this.client.get('/sms/unprocessed');
    return response.data;
  }

  async reprocessSms(smsId) {
    const response = await this.client.post(`/sms/reprocess/${smsId}`);
    return response.data;
  }

  async getSmsStats() {
    const response = await this.client.get('/sms/stats');
    return response.data;
  }

  async simulateBankSms(bankType = 'hdfc') {
    const response = await this.client.post('/sms/simulate', { bank_type: bankType });
    return response.data;
  }

  async getFailedSMS() {
    const response = await this.client.get('/sms/failed');
    return response.data;
  }

  async manualClassifySMS(smsId, transactionType, amount, description, currency = 'INR') {
    const response = await this.client.post('/sms/manual-classify', {
      sms_id: smsId,
      transaction_type: transactionType,
      amount: amount,
      description: description,
      currency: currency
    });
    return response.data;
  }

  // ==================== ANALYTICS API METHODS ====================

  async getSpendingTrends(timeframe = 'monthly', periods = 6) {
    const response = await this.client.get('/analytics/spending-trends', {
      params: { timeframe, periods }
    });
    return response.data;
  }

  async getFinancialHealthScore() {
    const response = await this.client.get('/analytics/financial-health');
    return response.data;
  }

  async getSpendingPatterns(timeframe = 'monthly') {
    const response = await this.client.get('/analytics/spending-patterns', {
      params: { timeframe }
    });
    return response.data;
  }

  async getBudgetRecommendations() {
    const response = await this.client.get('/analytics/budget-recommendations');
    return response.data;
  }

  async getSpendingAlerts() {
    const response = await this.client.get('/analytics/spending-alerts');
    return response.data;
  }

  async markAlertAsRead(alertId) {
    const response = await this.client.post(`/analytics/mark-alert-read/${alertId}`);
    return response.data;
  }

  async getAnalyticsSummary(timeframe = 'monthly') {
    const response = await this.client.get('/analytics/summary', {
      params: { timeframe }
    });
    return response.data;
  }

  // ==================== ANALYTICS EMAIL API METHODS ====================

  async sendSpendingAlerts() {
    const response = await this.client.post('/analytics/send-spending-alerts');
    return response.data;
  }

  async sendFinancialHealthReport() {
    const response = await this.client.post('/analytics/send-financial-health-report');
    return response.data;
  }

  async sendBudgetRecommendations() {
    const response = await this.client.post('/analytics/send-budget-recommendations');
    return response.data;
  }

  async sendWeeklyDigest() {
    const response = await this.client.post('/analytics/send-weekly-digest');
    return response.data;
  }

  async sendAllAnalyticsNotifications() {
    const response = await this.client.post('/analytics/send-all-notifications');
    return response.data;
  }

  async processScheduledAnalyticsNotifications() {
    const response = await this.client.post('/analytics/process-scheduled-notifications');
    return response.data;
  }

  // ==================== WHATSAPP INTEGRATION ====================
  async getWhatsAppStatus() {
    const response = await this.client.get('/whatsapp/status');
    return response.data;
  }

  // Send WhatsApp message
  async sendWhatsAppMessage(message) {
    try {
      const response = await this.client.post('/whatsapp/send', { message });
      return response.data;
    } catch (error) {
      console.error('Error sending WhatsApp message:', error);
      throw error;
    }
  }

  // ==================== PHONE VERIFICATION ====================
  async sendPhoneVerification(phoneData) {
    try {
      const response = await this.client.post('/phone/send-verification', phoneData);
      return response.data;
    } catch (error) {
      throw { response: { data: error.response?.data || error.message } };
    }
  }

  async verifyPhoneOTP(otpData) {
    try {
      const response = await this.client.post('/phone/verify-otp', otpData);
      return response.data;
    } catch (error) {
      throw { response: { data: error.response?.data || error.message } };
    }
  }

  async resendPhoneOTP() {
    try {
      const response = await this.client.post('/phone/resend-otp');
      return response.data;
    } catch (error) {
      throw { response: { data: error.response?.data || error.message } };
    }
  }

  async unlinkPhoneNumber() {
    try {
      const response = await this.client.delete('/phone/unlink');
      return response.data;
    } catch (error) {
      throw { response: { data: error.response?.data || error.message } };
    }
  }

  async getPhoneVerificationStatus() {
    const response = await this.client.get('/phone/status');
    return response.data;
  }
  // ==================== MONITORING ENDPOINTS ====================
  
  // Get system health status
  async getSystemHealth() {
    try {
      const response = await this.api.get('/monitoring/health');
      return response.data;
    } catch (error) {
      console.error('Error getting system health:', error);
      throw error;
    }
  }

  // Check user sync status (triggered by user actions like force refresh)
  async checkUserSyncStatus() {
    try {
      const response = await this.api.post('/monitoring/user-sync-check');
      return response.data;
    } catch (error) {
      console.error('Error checking user sync status:', error);
      throw error;
    }
  }

  // Get recent monitoring alerts
  async getRecentAlerts(timeWindow = 60) {
    try {
      const response = await this.api.get(`/monitoring/alerts?time_window=${timeWindow}`);
      return response.data;
    } catch (error) {
      console.error('Error getting recent alerts:', error);
      throw error;
    }
  }

  // Get WhatsApp service status for monitoring
  async getWhatsAppServiceStatus() {
    try {
      const response = await this.client.get('/monitoring/whatsapp-status');
      return response.data;
    } catch (error) {
      console.error('Error getting WhatsApp service status:', error);
      throw error;
    }
  }

  // Run monitoring cycle (admin function)
  async runMonitoringCycle(timeWindow = 10) {
    try {
      const response = await this.api.post(`/monitoring/run-cycle?time_window=${timeWindow}`);
      return response.data;
    } catch (error) {
      console.error('Error running monitoring cycle:', error);
      throw error;
    }
  }

  // Account consolidation methods
  async getConsolidationPreview(phoneNumber) {
    try {
      const response = await this.client.get(`/account/consolidation/preview?phone_number=${encodeURIComponent(phoneNumber)}`);
      return response.data;
    } catch (error) {
      console.error('Error getting consolidation preview:', error);
      throw error;
    }
  }

  async transferPhoneNumber(phoneNumber) {
    try {
      const response = await this.client.post(`/account/consolidation/transfer-phone?phone_number=${encodeURIComponent(phoneNumber)}`);
      return response.data;
    } catch (error) {
      console.error('Error transferring phone number:', error);
      throw error;
    }
  }

  async consolidateAccounts(phoneNumber) {
    try {
      const response = await this.client.post(`/account/consolidation/full-merge?phone_number=${encodeURIComponent(phoneNumber)}`);
      return response.data;
    } catch (error) {
      console.error('Error consolidating accounts:', error);
      throw error;
    }
  }

}

export default new ApiService();