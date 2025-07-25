import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { PlusCircle, TrendingUp, TrendingDown, DollarSign, AlertTriangle } from 'lucide-react';
import { mockTransactions, mockCategories, mockBudgetLimits, getCategoryById, calculateCategoryTotals } from './mock/mockData';
import TransactionForm from './TransactionForm';
import BudgetChart from './BudgetChart';
import TransactionList from './TransactionList';
import BudgetLimitsManager from './BudgetLimitsManager';

const BudgetDashboard = () => {
  const [transactions, setTransactions] = useState([]);
  const [budgetLimits, setBudgetLimits] = useState({});
  const [showTransactionForm, setShowTransactionForm] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  useEffect(() => {
    // Load data from localStorage or use mock data
    const savedTransactions = localStorage.getItem('budget_transactions');
    const savedBudgetLimits = localStorage.getItem('budget_limits');
    
    if (savedTransactions) {
      setTransactions(JSON.parse(savedTransactions));
    } else {
      setTransactions(mockTransactions);
    }
    
    if (savedBudgetLimits) {
      setBudgetLimits(JSON.parse(savedBudgetLimits));
    } else {
      setBudgetLimits(mockBudgetLimits);
    }
  }, []);

  useEffect(() => {
    // Save to localStorage whenever data changes
    localStorage.setItem('budget_transactions', JSON.stringify(transactions));
    localStorage.setItem('budget_limits', JSON.stringify(budgetLimits));
  }, [transactions, budgetLimits]);

  const currentMonthTransactions = transactions.filter(transaction => {
    const transactionDate = new Date(transaction.date);
    return transactionDate.getMonth() === selectedMonth && transactionDate.getFullYear() === selectedYear;
  });

  const totals = calculateCategoryTotals(currentMonthTransactions);
  const totalIncome = currentMonthTransactions
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + t.amount, 0);
  const totalExpenses = currentMonthTransactions
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0);
  const balance = totalIncome - totalExpenses;

  // Calculate budget alerts
  const budgetAlerts = Object.entries(budgetLimits).map(([categoryId, budget]) => {
    const spent = currentMonthTransactions
      .filter(t => t.categoryId === parseInt(categoryId) && t.type === 'expense')
      .reduce((sum, t) => sum + t.amount, 0);
    const percentage = (spent / budget.limit) * 100;
    return {
      categoryId: parseInt(categoryId),
      spent,
      limit: budget.limit,
      percentage,
      isOverBudget: spent > budget.limit,
      isNearLimit: percentage >= 80 && percentage < 100
    };
  }).filter(alert => alert.isOverBudget || alert.isNearLimit);

  const handleAddTransaction = (newTransaction) => {
    const transaction = {
      ...newTransaction,
      id: Date.now(),
      date: new Date().toISOString().split('T')[0]
    };
    setTransactions([...transactions, transaction]);
    setShowTransactionForm(false);
  };

  const handleUpdateBudgetLimits = (newLimits) => {
    setBudgetLimits(newLimits);
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-teal-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Budget Planner</h1>
          <p className="text-gray-600">Track your income, expenses, and stay within budget</p>
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
                {budgetAlerts.map(alert => {
                  const category = getCategoryById(alert.categoryId);
                  return (
                    <div key={alert.categoryId} className="flex items-center justify-between p-3 bg-white rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-4 h-4 rounded-full" style={{ backgroundColor: category.color }}></div>
                        <span className="font-medium">{category.name}</span>
                      </div>
                      <div className="text-right">
                        <span className={`font-bold ${alert.isOverBudget ? 'text-red-600' : 'text-amber-600'}`}>
                          ${alert.spent} / ${alert.limit}
                        </span>
                        <div className={`text-sm ${alert.isOverBudget ? 'text-red-600' : 'text-amber-600'}`}>
                          {alert.isOverBudget ? 'Over budget!' : 'Near limit'}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-emerald-800">Total Income</CardTitle>
              <TrendingUp className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-900">${totalIncome.toFixed(2)}</div>
              <p className="text-xs text-emerald-600">
                {monthNames[selectedMonth]} {selectedYear}
              </p>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-red-800">Total Expenses</CardTitle>
              <TrendingDown className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-900">${totalExpenses.toFixed(2)}</div>
              <p className="text-xs text-red-600">
                {monthNames[selectedMonth]} {selectedYear}
              </p>
            </CardContent>
          </Card>
          
          <Card className={`bg-gradient-to-br ${balance >= 0 ? 'from-blue-50 to-blue-100 border-blue-200' : 'from-red-50 to-red-100 border-red-200'}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${balance >= 0 ? 'text-blue-800' : 'text-red-800'}`}>Balance</CardTitle>
              <DollarSign className={`h-4 w-4 ${balance >= 0 ? 'text-blue-600' : 'text-red-600'}`} />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${balance >= 0 ? 'text-blue-900' : 'text-red-900'}`}>
                ${balance.toFixed(2)}
              </div>
              <p className={`text-xs ${balance >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                {balance >= 0 ? 'Surplus' : 'Deficit'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="transactions">Transactions</TabsTrigger>
            <TabsTrigger value="budget">Budget Limits</TabsTrigger>
            <TabsTrigger value="charts">Charts</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Recent Transactions</h2>
              <Button 
                onClick={() => setShowTransactionForm(true)}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                <PlusCircle className="h-4 w-4 mr-2" />
                Add Transaction
              </Button>
            </div>
            <TransactionList transactions={currentMonthTransactions.slice(0, 5)} />
          </TabsContent>
          
          <TabsContent value="transactions">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">All Transactions</h2>
              <Button 
                onClick={() => setShowTransactionForm(true)}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                <PlusCircle className="h-4 w-4 mr-2" />
                Add Transaction
              </Button>
            </div>
            <TransactionList transactions={currentMonthTransactions} />
          </TabsContent>
          
          <TabsContent value="budget">
            <BudgetLimitsManager 
              budgetLimits={budgetLimits}
              onUpdateLimits={handleUpdateBudgetLimits}
              currentTransactions={currentMonthTransactions}
            />
          </TabsContent>
          
          <TabsContent value="charts">
            <BudgetChart 
              transactions={currentMonthTransactions}
              budgetLimits={budgetLimits}
            />
          </TabsContent>
        </Tabs>

        {/* Transaction Form Modal */}
        {showTransactionForm && (
          <TransactionForm 
            onSubmit={handleAddTransaction}
            onCancel={() => setShowTransactionForm(false)}
          />
        )}
      </div>
    </div>
  );
};

export default BudgetDashboard;