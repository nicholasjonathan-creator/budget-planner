# 💰 Budget Planner - AI-Powered SMS Transaction Tracking

A modern, full-stack budget planning application with automated SMS transaction parsing and real-time analytics.

## 🚀 Features

- **📱 SMS Transaction Parsing**: Automatically parse bank SMS alerts and create transactions
- **🎯 Smart Categorization**: AI-powered transaction categorization
- **📊 Real-time Analytics**: Beautiful charts and budget insights
- **⚡ Budget Alerts**: Get notified when approaching spending limits
- **🔄 Multi-Bank Support**: Works with HDFC, SBI, ICICI, and more
- **📈 Monthly Trends**: Track spending patterns over time
- **🎨 Modern UI**: Clean, responsive design with dark mode

## 🛠️ Tech Stack

**Frontend:**
- React 19 with TypeScript
- Tailwind CSS + shadcn/ui
- Recharts for data visualization
- Axios for API calls

**Backend:**
- FastAPI (Python)
- MongoDB with Motor (async)
- Pydantic for data validation
- Advanced SMS parsing with regex

**Deployment:**
- Frontend: Vercel
- Backend: Railway
- Database: MongoDB Atlas
- SMS: Twilio webhooks

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and Yarn
- Python 3.11+
- MongoDB (local or Atlas)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/budget-planner.git
   cd budget-planner
   ```

2. **Setup Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Update .env with your MongoDB connection string
   uvicorn server:app --reload
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   yarn install
   cp .env.example .env
   # Update .env with your backend URL
   yarn start
   ```

## 🌍 Production Deployment

### Automated Deployment

Run the deployment script:

```bash
./deploy.sh
```

This will:
- Deploy backend to Railway
- Deploy frontend to Vercel
- Guide you through MongoDB Atlas setup
- Configure environment variables

### Manual Deployment Steps

#### 1. MongoDB Atlas Setup
1. Create account at [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a new cluster (free tier available)
3. Create database user
4. Whitelist IP addresses
5. Get connection string

#### 2. Backend Deployment (Railway)
```bash
cd backend
npm install -g @railway/cli
railway login
railway init
railway up
```

#### 3. Frontend Deployment (Vercel)
```bash
cd frontend
npm install -g vercel
yarn build
vercel --prod
```

## 📱 SMS Integration

### Twilio Setup
1. Create [Twilio account](https://www.twilio.com/)
2. Get phone number
3. Configure webhook URL: `https://your-backend.railway.app/api/sms/receive`
4. Update environment variables

### SMS Forwarding Options
- **IFTTT/Zapier**: Create automation to forward SMS
- **Android SMS Forwarder**: Use apps like SMS Forwarder
- **SMS Gateway**: Use dedicated SMS gateway services

## 📊 Supported Banks

- **HDFC Bank**: Full support
- **State Bank of India (SBI)**: Full support
- **ICICI Bank**: Full support
- **Axis Bank**: Partial support
- **Others**: Easily configurable

## 🔒 Security

- JWT authentication
- Rate limiting
- Input validation
- CORS configuration
- Environment-based secrets
- Database encryption

## 📞 Support

- **GitHub Issues**: [Create an issue](https://github.com/yourusername/budget-planner/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/budget-planner/wiki)

---

<p align="center">
  <strong>Made with ❤️ for better financial management</strong>
</p>
