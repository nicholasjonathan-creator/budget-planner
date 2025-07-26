import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { PlusCircle, TrendingUp, TrendingDown, DollarSign, AlertTriangle, MessageSquare, Settings } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import ApiService from '../services/api';
import TransactionForm from './TransactionForm';
import BudgetChart from './BudgetChart';
import TransactionList from './TransactionList';
import BudgetLimitsManager from './BudgetLimitsManager';
import SMSDemo from './SMSDemo';
import ManualClassification from './ManualClassification';
import CurrencyDisplay from './CurrencyDisplay';
import UserProfile from './UserProfile';
import NotificationSettings from './NotificationSettings';
import ProductionEmailManagement from './ProductionEmailManagement';
import { useAuth } from '../contexts/AuthContext';

const BudgetDashboard = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [budgetLimits, setBudgetLimits] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showTransactionForm, setShowTransactionForm] = useState(false);
  const [showSMSDemo, setShowSMSDemo] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(6); // July = 6 (0-indexed)
  const [selectedYear, setSelectedYear] = useState(2025);
  const [monthlySummary, setMonthlySummary] = useState({ income: 0, expense: 0, balance: 0 });
  const [categoryTotals, setCategoryTotals] = useState({});
  const [loading, setLoading] = useState(true);
  const [transactionFilter, setTransactionFilter] = useState('all'); // 'all', 'income', 'expense'
  const [refreshKey, setRefreshKey] = useState(0); // Force refresh key
  const [failedSMSCount, setFailedSMSCount] = useState(0); // Count of failed SMS needing manual validation
  const [multiCurrencyTransactions, setMultiCurrencyTransactions] = useState([]); // Track non-INR transactions
  const [activeTab, setActiveTab] = useState('overview'); // Tab state management
  const { toast } = useToast();

  // Check if user is admin
  const isAdmin = user && user.role === 'admin';

  useEffect(() => {
    loadData();
  }, [selectedMonth, selectedYear, refreshKey]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load all data in parallel
      const [
        transactionsData,
        budgetLimitsData,
        categoriesData,
        summaryData,
        totalsData,
        failedSMSData
      ] = await Promise.all([
        ApiService.getTransactions(selectedMonth, selectedYear),
        ApiService.getBudgetLimits(selectedMonth, selectedYear),
        ApiService.getCategories(),
        ApiService.getMonthlySummary(selectedMonth, selectedYear),
        ApiService.getCategoryTotals(selectedMonth, selectedYear),
        ApiService.getFailedSMS()
      ]);

      setTransactions(transactionsData);
      setBudgetLimits(budgetLimitsData);
      setCategories(categoriesData);
      setMonthlySummary(summaryData);
      setCategoryTotals(totalsData);
      setFailedSMSCount(failedSMSData.success ? failedSMSData.failed_sms.length : 0);
      
      // Detect multi-currency transactions (transactions with non-INR currencies)
      const nonINRTransactions = transactionsData.filter(transaction => {
        // Check if transaction has currency information in raw_data or if description/merchant suggests foreign currency
        const hasNonINRCurrency = transaction.raw_data?.currency && transaction.raw_data.currency !== 'INR' ||
                                  transaction.description?.includes('$') || 
                                  transaction.description?.includes('USD') ||
                                  transaction.description?.includes('EUR') ||
                                  transaction.description?.includes('€') ||
                                  transaction.merchant?.includes('$');
        return hasNonINRCurrency;
      });
      
      setMultiCurrencyTransactions(nonINRTransactions);
      
    } catch (error) {
      console.error('Error loading data:', error);
      toast({
        title: "Error",
        description: "Failed to load data. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getFilteredTransactions = () => {
    if (transactionFilter === 'all') {
      return transactions;
    }
    return transactions.filter(transaction => transaction.type === transactionFilter);
  };

  const handleIncomeClick = () => {
    setTransactionFilter('income');
    setActiveTab('transactions'); // Switch to Transactions tab to show full list
  };

  const handleExpenseClick = () => {
    setTransactionFilter('expense');
    setActiveTab('transactions'); // Switch to Transactions tab to show full list
  };

  const handleShowAllTransactions = () => {
    setTransactionFilter('all');
  };

  const handleManualClassificationComplete = async () => {
    // Show loading state
    setLoading(true);
    
    // Force a complete refresh of all data
    setRefreshKey(prev => prev + 1);
    await loadData();
    
    // Show success message
    toast({
      title: "Dashboard Updated",
      description: "Financial data refreshed with new transaction",
    });
  };

  const handleAddTransaction = async (newTransaction) => {
    try {
      await ApiService.createTransaction(newTransaction);
      setShowTransactionForm(false);
      await loadData(); // Refresh data
      toast({
        title: "Success",
        description: "Transaction added successfully!",
      });
    } catch (error) {
      console.error('Error adding transaction:', error);
      toast({
        title: "Error",
        description: "Failed to add transaction. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleUpdateBudgetLimits = async (newLimits) => {
    try {
      // Create budget limits for categories that don't have them
      const promises = Object.entries(newLimits).map(([categoryId, budget]) => {
        return ApiService.createBudgetLimit({
          category_id: parseInt(categoryId),
          limit: budget.limit,
          month: selectedMonth,
          year: selectedYear
        });
      });

      await Promise.all(promises);
      await loadData(); // Refresh data
      toast({
        title: "Success",
        description: "Budget limits updated successfully!",
      });
    } catch (error) {
      console.error('Error updating budget limits:', error);
      toast({
        title: "Error",
        description: "Failed to update budget limits. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Calculate budget alerts
  const budgetAlerts = budgetLimits.filter(budget => {
    const spent = budget.spent || 0;
    const percentage = (spent / budget.limit) * 100;
    return spent > budget.limit || percentage >= 80;
  }).map(budget => {
    const category = categories.find(c => c.id === budget.category_id);
    const spent = budget.spent || 0;
    const percentage = (spent / budget.limit) * 100;
    return {
      ...budget,
      category,
      percentage,
      isOverBudget: spent > budget.limit,
      isNearLimit: percentage >= 80 && percentage < 100
    };
  });

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-rose-50 via-teal-50 to-indigo-100 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading budget data...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-teal-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Budget Planner</h1>
            <p className="text-gray-600">Track your income, expenses, and stay within budget - Built for India 🇮🇳</p>
          </div>
          <UserProfile />
        </div>

        {/* Month/Year Selector */}
        <div className="mb-6 flex gap-4 items-center">
          <select
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            {monthNames.map((month, index) => (
              <option key={index} value={index}>{month}</option>
            ))}
          </select>
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(parseInt(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            {[2024, 2025, 2026].map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
          <Button
            onClick={() => setShowSMSDemo(true)}
            variant="outline"
            className="ml-auto"
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            SMS Demo
          </Button>
        </div>

        {/* Budget Alerts */}
        {budgetAlerts.length > 0 && (
          <Card className="mb-6 border-l-4 border-l-amber-500 bg-amber-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-amber-800">
                <AlertTriangle className="h-5 w-5" />
                Budget Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {budgetAlerts.map(alert => (
                  <div key={alert.category_id} className="flex items-center justify-between p-3 bg-white rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: alert.category?.color }}></div>
                      <span className="font-medium">{alert.category?.name}</span>
                    </div>
                    <div className="text-right">
                      <span className={`font-bold ${alert.isOverBudget ? 'text-red-600' : 'text-amber-600'}`}>
                        ₹{alert.spent || 0} / ₹{alert.limit}
                      </span>
                      <div className={`text-sm ${alert.isOverBudget ? 'text-red-600' : 'text-amber-600'}`}>
                        {alert.isOverBudget ? 'Over budget!' : 'Near limit'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Manual Validation Needed Section */}
        {failedSMSCount > 0 && (
          <Card className="mb-6 border-l-4 border-l-orange-500 bg-orange-50">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-orange-800">
                  <AlertTriangle className="h-5 w-5" />
                  Manual Validation Needed
                  <Badge variant="outline" className="bg-orange-100 text-orange-800 border-orange-300">
                    {failedSMSCount} SMS pending
                  </Badge>
                </div>
                <Button
                  onClick={() => setActiveTab('manual')}
                  size="sm"
                  className="bg-orange-600 hover:bg-orange-700 text-white"
                >
                  Review Now
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-orange-700 text-sm">
                {failedSMSCount} SMS message{failedSMSCount !== 1 ? 's' : ''} couldn't be automatically processed and require{failedSMSCount === 1 ? 's' : ''} your manual review. 
                These may include transactions with unusual formatting, future dates, or unclear transaction types.
              </p>
              <p className="text-orange-600 text-xs mt-2">
                📱 Click "Review Now" to manually classify these transactions and update your financial summary.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Multi-Currency Display */}
        {multiCurrencyTransactions.length > 0 && (
          <CurrencyDisplay currencies={multiCurrencyTransactions} />
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card 
            className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200 cursor-pointer hover:shadow-lg transition-shadow duration-200"
            onClick={handleIncomeClick}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-emerald-800">Total Income</CardTitle>
              <TrendingUp className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-900">₹{monthlySummary.income.toLocaleString('en-IN')}</div>
              <p className="text-xs text-emerald-600">
                {monthNames[selectedMonth]} {selectedYear} • Click to view details
              </p>
            </CardContent>
          </Card>
          
          <Card 
            className="bg-gradient-to-br from-red-50 to-red-100 border-red-200 cursor-pointer hover:shadow-lg transition-shadow duration-200"
            onClick={handleExpenseClick}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-red-800">Total Expenses</CardTitle>
              <TrendingDown className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-900">₹{monthlySummary.expense.toLocaleString('en-IN')}</div>
              <p className="text-xs text-red-600">
                {monthNames[selectedMonth]} {selectedYear} • Click to view details
              </p>
            </CardContent>
          </Card>
          
          <Card 
            className={`bg-gradient-to-br ${monthlySummary.balance >= 0 ? 'from-blue-50 to-blue-100 border-blue-200' : 'from-red-50 to-red-100 border-red-200'} cursor-pointer hover:shadow-lg transition-shadow duration-200`}
            onClick={handleShowAllTransactions}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${monthlySummary.balance >= 0 ? 'text-blue-800' : 'text-red-800'}`}>Balance</CardTitle>
              <DollarSign className={`h-4 w-4 ${monthlySummary.balance >= 0 ? 'text-blue-600' : 'text-red-600'}`} />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${monthlySummary.balance >= 0 ? 'text-blue-900' : 'text-red-900'}`}>
                ₹{monthlySummary.balance.toLocaleString('en-IN')}
              </div>
              <p className={`text-xs ${monthlySummary.balance >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                {monthlySummary.balance >= 0 ? 'Surplus' : 'Deficit'} • Click to view all
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-6 mb-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="transactions">Transactions</TabsTrigger>
            <TabsTrigger value="budget">Budget Limits</TabsTrigger>
            <TabsTrigger value="charts">Charts</TabsTrigger>
            <TabsTrigger value="manual">
              <Settings className="h-4 w-4 mr-2" />
              Manual
            </TabsTrigger>
            <TabsTrigger value="notifications">
              <MessageSquare className="h-4 w-4 mr-2" />
              Notifications
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Recent Transactions</h2>
                {transactionFilter !== 'all' && (
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline" className="capitalize">
                      {transactionFilter} transactions
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleShowAllTransactions}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      Show all
                    </Button>
                  </div>
                )}
              </div>
              <Button 
                onClick={() => setShowTransactionForm(true)}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                <PlusCircle className="h-4 w-4 mr-2" />
                Add Transaction
              </Button>
            </div>
            <TransactionList 
              transactions={getFilteredTransactions().slice(0, 5)} 
              categories={categories} 
              onTransactionUpdate={loadData}
              showDetailedView={transactionFilter !== 'all'}
            />
          </TabsContent>
          
          <TabsContent value="transactions">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">All Transactions</h2>
                {transactionFilter !== 'all' && (
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline" className="capitalize">
                      {transactionFilter} transactions
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleShowAllTransactions}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      Show all
                    </Button>
                  </div>
                )}
              </div>
              <Button 
                onClick={() => setShowTransactionForm(true)}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                <PlusCircle className="h-4 w-4 mr-2" />
                Add Transaction
              </Button>
            </div>
            <TransactionList 
              transactions={getFilteredTransactions()} 
              categories={categories} 
              onTransactionUpdate={loadData}
              showDetailedView={transactionFilter !== 'all'}
            />
          </TabsContent>
          
          <TabsContent value="budget">
            <BudgetLimitsManager 
              budgetLimits={budgetLimits}
              categories={categories}
              onUpdateLimits={handleUpdateBudgetLimits}
              currentTransactions={transactions}
            />
          </TabsContent>
          
          <TabsContent value="charts">
            <BudgetChart 
              transactions={transactions}
              budgetLimits={budgetLimits}
              categories={categories}
            />
          </TabsContent>
          
          <TabsContent value="manual">
            <ManualClassification 
              key={refreshKey}
              onClassificationComplete={handleManualClassificationComplete}
            />
          </TabsContent>
          
          <TabsContent value="notifications">
            <NotificationSettings />
          </TabsContent>
        </Tabs>

        {/* Transaction Form Modal */}
        {showTransactionForm && (
          <TransactionForm 
            categories={categories}
            selectedMonth={selectedMonth}
            selectedYear={selectedYear}
            onSubmit={handleAddTransaction}
            onCancel={() => setShowTransactionForm(false)}
          />
        )}

        {/* SMS Demo Modal */}
        {showSMSDemo && (
          <SMSDemo 
            onClose={() => setShowSMSDemo(false)}
            onTransactionAdded={loadData}
          />
        )}
      </div>
    </div>
  );
};

export default BudgetDashboard;