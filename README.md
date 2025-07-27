# 🚀 Budget Planner - Secure Deployment Guide

## 🔒 SECURITY FIRST APPROACH

This repository contains **ZERO sensitive data**. All credentials and secrets are managed through environment variables.

## ✨ FEATURES

### 🔐 **User Management**
- Unique UUID-based user identification
- Secure login/logout with JWT tokens
- Phone number validation for WhatsApp integration
- Complete data isolation between users

### 💬 **WhatsApp Integration (Optional)**
- Phone verification system
- SMS forwarding via Twilio WhatsApp
- Automatic transaction parsing from forwarded SMS
- Graceful fallbacks if WhatsApp fails

### 🏦 **Transaction Management**
- Multi-bank SMS parsing (HDFC, SBI, ICICI, Axis, Federal/Scapia)
- Manual transaction CRUD (Create, Read, Update, Delete)
- Delete confirmation dialogs with hard database deletion
- INR currency focus with proper formatting

### 📊 **Analytics & Budgeting**
- Comprehensive spending insights and financial health scores
- Custom + predefined budget categories
- Monthly + weekly budget tracking
- Budget progress indicators and alerts

### 📤 **Data Export**
- Export transactions in PDF, CSV, Excel formats
- Complete user data portability

## 🚀 DEPLOYMENT ARCHITECTURE

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Railway       │    │  MongoDB Atlas  │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│   React App     │    │   FastAPI       │    │   User Data     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │                       │                       
         ▼                       ▼                       
┌─────────────────┐    ┌─────────────────┐              
│   GitHub        │    │   Twilio        │              
│   (Code Repo)   │    │   (WhatsApp)    │              
│   Clean & Safe  │    │   SMS Forward   │              
└─────────────────┘    └─────────────────┘              
```

## 🔐 ENVIRONMENT VARIABLES

### Backend (Railway)
```bash
MONGO_URL=mongodb+srv://...
JWT_SECRET_KEY=your-secret-key
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+...
```

### Frontend (Vercel)  
```bash
REACT_APP_BACKEND_URL=https://your-backend.railway.app/api
GENERATE_SOURCEMAP=false
```

## 🛡️ SECURITY FEATURES

- ✅ **No hardcoded secrets** - All sensitive data in environment variables
- ✅ **User data isolation** - Strict user_id filtering on all queries  
- ✅ **UUID-based IDs** - No MongoDB ObjectID exposure
- ✅ **JWT authentication** - Secure session management
- ✅ **CORS protection** - Restricted to frontend domain

**Built with ❤️ for India 🇮🇳**
