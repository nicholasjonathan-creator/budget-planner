import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Target,
  AlertTriangle,
  Award,
  BarChart3,
  PieChart,
  LineChart,
  DollarSign,
  Lightbulb,
  Bell,
  Clock,
  Calendar
} from 'lucide-react';
import api from '../services/api';

const AnalyticsDashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTimeframe, setActiveTimeframe] = useState('monthly');
  const [alerts, setAlerts] = useState([]);
  const [sendingEmails, setSendingEmails] = useState(false);

  useEffect(() => {
    loadAnalyticsData();
    loadSpendingAlerts();
  }, [activeTimeframe]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      const summary = await api.getAnalyticsSummary(activeTimeframe);
      setAnalyticsData(summary);
      setError(null);
    } catch (err) {
      console.error('Error loading analytics data:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const loadSpendingAlerts = async () => {
    try {
      const alertsData = await api.getSpendingAlerts();
      setAlerts(alertsData);
    } catch (err) {
      console.error('Error loading spending alerts:', err);
    }
  };

  const handleMarkAlertRead = async (alertId) => {
    try {
      await api.markAlertAsRead(alertId);
      setAlerts(alerts.map(alert => 
        alert.id === alertId ? { ...alert, is_read: true } : alert
      ));
    } catch (err) {
      console.error('Error marking alert as read:', err);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'increasing':
        return <TrendingUp className="h-4 w-4 text-red-500" />;
      case 'decreasing':
        return <TrendingDown className="h-4 w-4 text-green-500" />;
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getHealthScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert className="border-red-200">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">Comprehensive insights into your financial health</p>
        </div>
        <div className="flex space-x-2">
          {['weekly', 'monthly', 'quarterly'].map((timeframe) => (
            <Button
              key={timeframe}
              variant={activeTimeframe === timeframe ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveTimeframe(timeframe)}
            >
              {timeframe.charAt(0).toUpperCase() + timeframe.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Financial Health Score */}
      {analyticsData?.financial_health && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-blue-600" />
              Financial Health Score
            </CardTitle>
            <CardDescription>Overall assessment of your financial wellbeing</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className={`text-4xl font-bold p-4 rounded-lg ${getHealthScoreColor(analyticsData.financial_health.score)}`}>
                {analyticsData.financial_health.score}/100
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">
                  Grade: {analyticsData.financial_health.grade}
                </div>
                <div className="text-sm text-gray-600">
                  Savings Rate: {analyticsData.financial_health.savings_rate.toFixed(1)}%
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center">
                <div className="text-sm text-gray-600">Income Stability</div>
                <div className="text-lg font-semibold">
                  {(analyticsData.financial_health.income_stability * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600">Expense Control</div>
                <div className="text-lg font-semibold">
                  {(analyticsData.financial_health.expense_control * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600">Budget Adherence</div>
                <div className="text-lg font-semibold">
                  {(analyticsData.financial_health.budget_adherence * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600">Debt Ratio</div>
                <div className="text-lg font-semibold">
                  {(analyticsData.financial_health.debt_to_income_ratio * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {analyticsData.financial_health.recommendations?.length > 0 && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  Recommendations
                </h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  {analyticsData.financial_health.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-blue-600">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Spending Alerts */}
      {alerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-orange-600" />
              Spending Alerts
              <Badge variant="secondary">{alerts.filter(a => !a.is_read).length} unread</Badge>
            </CardTitle>
            <CardDescription>Unusual spending patterns and anomalies</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {alerts.slice(0, 5).map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-lg border ${getSeverityColor(alert.severity)} ${
                    alert.is_read ? 'opacity-60' : ''
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">{alert.title}</div>
                      <div className="text-sm mt-1">{alert.description}</div>
                      {alert.amount > 0 && (
                        <div className="text-sm font-medium mt-1">
                          Amount: {formatCurrency(alert.amount)}
                        </div>
                      )}
                    </div>
                    {!alert.is_read && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleMarkAlertRead(alert.id)}
                      >
                        Mark Read
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Analytics Tabs */}
      <Tabs defaultValue="trends" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="trends" className="flex items-center gap-2">
            <LineChart className="h-4 w-4" />
            Trends
          </TabsTrigger>
          <TabsTrigger value="patterns" className="flex items-center gap-2">
            <PieChart className="h-4 w-4" />
            Patterns
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Budget Tips
          </TabsTrigger>
          <TabsTrigger value="summary" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Summary
          </TabsTrigger>
        </TabsList>

        {/* Spending Trends Tab */}
        <TabsContent value="trends">
          <Card>
            <CardHeader>
              <CardTitle>Spending Trends</CardTitle>
              <CardDescription>
                Your spending patterns over the last {analyticsData?.spending_trends?.length || 0} periods
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analyticsData?.spending_trends?.length > 0 ? (
                <div className="space-y-4">
                  {analyticsData.spending_trends.map((trend, index) => (
                    <div key={index} className="flex justify-between items-center p-4 border rounded-lg">
                      <div>
                        <div className="font-medium">{trend.period}</div>
                        <div className="text-2xl font-bold text-gray-900">
                          {formatCurrency(trend.total_amount)}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center gap-2 mb-1">
                          {getTrendIcon(trend.trend_direction)}
                          <span className={`font-medium ${
                            trend.change_percentage > 0 ? 'text-red-600' : 
                            trend.change_percentage < 0 ? 'text-green-600' : 'text-gray-600'
                          }`}>
                            {trend.change_percentage > 0 ? '+' : ''}{trend.change_percentage.toFixed(1)}%
                          </span>
                        </div>
                        <div className="text-sm text-gray-600">
                          {trend.change_amount > 0 ? '+' : ''}{formatCurrency(trend.change_amount)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No spending trends data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Spending Patterns Tab */}
        <TabsContent value="patterns">
          <Card>
            <CardHeader>
              <CardTitle>Spending Patterns</CardTitle>
              <CardDescription>Category-wise spending analysis</CardDescription>
            </CardHeader>
            <CardContent>
              {analyticsData?.spending_patterns?.length > 0 ? (
                <div className="space-y-4">
                  {analyticsData.spending_patterns.map((pattern, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="font-medium">Category {pattern.category_id}</div>
                          <div className="text-sm text-gray-600">
                            {pattern.transaction_count} transactions
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold">
                            {formatCurrency(pattern.total_amount)}
                          </div>
                          <div className="text-sm text-gray-600">
                            {pattern.percentage_of_total.toFixed(1)}% of total
                          </div>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Average: </span>
                          <span className="font-medium">{formatCurrency(pattern.average_amount)}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Trend: </span>
                          <span className={`font-medium ${
                            pattern.trend_compared_to_previous > 0 ? 'text-red-600' : 
                            pattern.trend_compared_to_previous < 0 ? 'text-green-600' : 'text-gray-600'
                          }`}>
                            {pattern.trend_compared_to_previous > 0 ? '+' : ''}
                            {pattern.trend_compared_to_previous.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      
                      {pattern.peak_spending_times?.length > 0 && (
                        <div className="mt-2 flex gap-2">
                          {pattern.peak_spending_times.map((time, timeIndex) => (
                            <Badge key={timeIndex} variant="secondary" className="text-xs">
                              <Clock className="h-3 w-3 mr-1" />
                              {time}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No spending patterns data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Budget Recommendations Tab */}
        <TabsContent value="recommendations">
          <Card>
            <CardHeader>
              <CardTitle>AI-Powered Budget Recommendations</CardTitle>
              <CardDescription>Smart suggestions to optimize your budget</CardDescription>
            </CardHeader>
            <CardContent>
              {analyticsData?.budget_recommendations?.length > 0 ? (
                <div className="space-y-4">
                  {analyticsData.budget_recommendations.map((rec, index) => (
                    <div key={index} className="p-4 border rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <div className="font-medium">Category {rec.category_id}</div>
                          <div className="text-sm text-gray-600 mt-1">{rec.reasoning}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-gray-600">Confidence</div>
                          <div className="font-medium">
                            {(rec.confidence_score * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Current Budget: </span>
                          <span className="font-medium">
                            {rec.current_budget ? formatCurrency(rec.current_budget) : 'Not set'}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Recommended: </span>
                          <span className="font-medium text-blue-600">
                            {formatCurrency(rec.recommended_budget)}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Potential Savings: </span>
                          <span className="font-medium text-green-600">
                            {formatCurrency(rec.potential_savings)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No budget recommendations available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Summary Tab */}
        <TabsContent value="summary">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Total Income</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(analyticsData?.total_income || 0)}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {analyticsData?.period}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Total Expenses</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {formatCurrency(analyticsData?.total_expenses || 0)}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {analyticsData?.period}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Net Balance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${
                  (analyticsData?.net_balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(analyticsData?.net_balance || 0)}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {analyticsData?.period}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalyticsDashboard;