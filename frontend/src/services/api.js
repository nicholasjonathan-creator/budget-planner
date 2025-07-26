import axios from 'axios';
import Cookies from 'js-cookie';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API,
      timeout: 10000,
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

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        
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
}

export default new ApiService();