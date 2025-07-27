# 🏦 Budget Planner - Clean & GitHub-Ready

A comprehensive budget management application built with React and FastAPI, featuring SMS transaction parsing, WhatsApp integration, and advanced analytics.

## ✨ Features

### 🔐 **User Management**
- Secure JWT-based authentication
- User registration and login
- Multi-user support with data isolation
- Profile management

### 💰 **Transaction Management**
- Manual transaction entry (income/expense)
- Multi-bank SMS parsing support (HDFC, SBI, ICICI, Axis, Federal Bank)
- Transaction categorization and tagging
- Monthly/weekly transaction summaries
- Search and filter functionality

### 📊 **Analytics & Budgeting**
- Real-time spending insights
- Budget limits and tracking
- Financial health scoring
- Visual charts and graphs
- Monthly/weekly spending patterns

### 📱 **WhatsApp Integration (Optional)**
- Phone verification system
- SMS forwarding via Twilio WhatsApp
- Automatic transaction parsing from forwarded SMS
- Fallback to manual entry if WhatsApp fails

### 📤 **Data Export**
- Export transactions in PDF, CSV, Excel formats
- Complete user data portability

## 🚀 Quick Start

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- MongoDB (local or Atlas)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd budget-planner
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.template .env
   # Edit .env with your configuration
   python server.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   yarn install
   cp .env.template .env
   # Edit .env with your configuration
   yarn start
   ```

4. **Database Setup**
   - MongoDB will be automatically initialized on first run
   - Default categories and indexes will be created

## 🔧 Configuration

### Required Environment Variables

#### Backend (.env)
```bash
# Database
MONGO_URL=mongodb://localhost:27017/budget_planner

# Authentication
JWT_SECRET=your-secret-key-here

# Optional: WhatsApp Integration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886

# Optional: Email Notifications
SENDGRID_API_KEY=your_sendgrid_api_key
SENDER_EMAIL=noreply@yourdomain.com
```

#### Frontend (.env)
```bash
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001

# Environment
NODE_ENV=development
```

## 🌐 Deployment

### Backend (Railway/Render)
1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Deploy with automatic builds

### Frontend (Vercel/Netlify)
1. Connect your GitHub repository
2. Set `REACT_APP_BACKEND_URL` to your backend URL
3. Deploy with automatic builds

### Database (MongoDB Atlas)
1. Create a cluster
2. Get connection string
3. Update `MONGO_URL` in backend environment

## 📱 SMS Parsing Support

The application supports automatic transaction parsing from SMS notifications from major Indian banks:

- **HDFC Bank** - Debit/Credit card transactions, UPI, Net Banking
- **SBI** - Account transactions, UPI payments
- **ICICI Bank** - Various transaction types
- **Axis Bank** - Card and UPI transactions
- **Federal Bank/Scapia** - Card transactions

## 🛡️ Security Features

- ✅ **No hardcoded secrets** - All sensitive data in environment variables
- ✅ **User data isolation** - Strict user_id filtering on all queries
- ✅ **JWT authentication** - Secure session management
- ✅ **CORS protection** - Restricted to frontend domain
- ✅ **UUID-based IDs** - No MongoDB ObjectID exposure

## 🔄 Development Workflow

1. **Make changes** to frontend or backend code
2. **Test locally** using the development servers
3. **Commit changes** to GitHub
4. **Deploy** automatically via connected platforms

## 📝 API Documentation

The backend provides a comprehensive REST API with the following endpoints:

- **Authentication**: `/api/auth/` - Login, register, token management
- **Transactions**: `/api/transactions/` - CRUD operations
- **Analytics**: `/api/analytics/` - Spending insights and reports
- **SMS**: `/api/sms/` - SMS parsing and processing
- **WhatsApp**: `/api/whatsapp/` - WhatsApp integration
- **Users**: `/api/users/` - User management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ for India 🇮🇳**
