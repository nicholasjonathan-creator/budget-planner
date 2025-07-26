import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { ChevronDown, ChevronRight, Sunrise, Sun, Sunset, Moon, Clock, TrendingUp, TrendingDown } from 'lucide-react';

const TimeBasedTransactionGroups = ({ transactions }) => {
  const [expandedGroups, setExpandedGroups] = useState({
    morning: false,
    afternoon: false,
    evening: false,
    night: false
  });

  // Define time periods with icons and colors
  const timePeriods = {
    morning: {
      label: 'Morning',
      timeRange: '6:00 AM - 11:59 AM',
      icon: Sunrise,
      color: 'from-orange-100 to-yellow-100',
      borderColor: 'border-orange-200',
      textColor: 'text-orange-800',
      iconColor: 'text-orange-600'
    },
    afternoon: {
      label: 'Afternoon',
      timeRange: '12:00 PM - 2:59 PM',
      icon: Sun,
      color: 'from-yellow-100 to-amber-100',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-800',
      iconColor: 'text-yellow-600'
    },
    evening: {
      label: 'Evening',
      timeRange: '3:00 PM - 8:59 PM',
      icon: Sunset,
      color: 'from-orange-100 to-red-100',
      borderColor: 'border-orange-200',
      textColor: 'text-orange-800',
      iconColor: 'text-orange-600'
    },
    night: {
      label: 'Night',
      timeRange: '9:00 PM - 5:59 AM',
      icon: Moon,
      color: 'from-indigo-100 to-purple-100',
      borderColor: 'border-indigo-200',
      textColor: 'text-indigo-800',
      iconColor: 'text-indigo-600'
    }
  };

  // Function to determine which time period a transaction belongs to
  const getTimePeriod = (date) => {
    const hour = new Date(date).getHours();
    
    if (hour >= 6 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 15) return 'afternoon';
    if (hour >= 15 && hour < 21) return 'evening';
    return 'night'; // 21-23 and 0-5
  };

  // Group transactions by time period
  const groupedTransactions = React.useMemo(() => {
    const groups = {
      morning: [],
      afternoon: [],
      evening: [],
      night: []
    };

    transactions.forEach(transaction => {
      const period = getTimePeriod(transaction.date);
      groups[period].push(transaction);
    });

    return groups;
  }, [transactions]);

  // Calculate totals for each period
  const periodTotals = React.useMemo(() => {
    const totals = {};
    Object.keys(groupedTransactions).forEach(period => {
      const income = groupedTransactions[period]
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
      const expense = groupedTransactions[period]
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);
      
      totals[period] = {
        income,
        expense,
        balance: income - expense,
        count: groupedTransactions[period].length
      };
    });
    return totals;
  }, [groupedTransactions]);

  const toggleGroup = (period) => {
    setExpandedGroups(prev => ({
      ...prev,
      [period]: !prev[period]
    }));
  };

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatCurrency = (amount) => {
    return `₹${amount.toLocaleString('en-IN')}`;
  };

  // Calculate the maximum expense for progress bars
  const maxExpense = Math.max(...Object.values(periodTotals).map(p => p.expense));

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-6">
        <Clock className="h-5 w-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-800">Daily Time-based Spending</h3>
      </div>

      {Object.entries(timePeriods).map(([periodKey, period]) => {
        const total = periodTotals[periodKey];
        const Icon = period.icon;
        const hasTransactions = total.count > 0;
        const expensePercentage = maxExpense > 0 ? (total.expense / maxExpense) * 100 : 0;

        return (
          <Card key={periodKey} className={`bg-gradient-to-br ${period.color} ${period.borderColor} transition-all duration-200 hover:shadow-md`}>
            <Collapsible 
              open={expandedGroups[periodKey]} 
              onOpenChange={() => toggleGroup(periodKey)}
            >
              <CollapsibleTrigger asChild>
                <CardHeader className="cursor-pointer hover:bg-white/20 transition-colors duration-150 rounded-t-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Icon className={`h-5 w-5 ${period.iconColor}`} />
                      <div>
                        <CardTitle className={`text-base font-medium ${period.textColor}`}>
                          {period.label}
                        </CardTitle>
                        <p className={`text-xs ${period.textColor} opacity-70`}>
                          {period.timeRange}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      {hasTransactions && (
                        <>
                          <div className="text-right">
                            <div className={`text-sm font-medium ${period.textColor}`}>
                              {formatCurrency(total.expense)}
                            </div>
                            <div className={`text-xs ${period.textColor} opacity-70`}>
                              {total.count} transaction{total.count !== 1 ? 's' : ''}
                            </div>
                          </div>
                          <div className="w-16">
                            <Progress 
                              value={expensePercentage} 
                              className="h-2 bg-white/30"
                            />
                          </div>
                        </>
                      )}
                      
                      {!hasTransactions && (
                        <Badge variant="outline" className={`${period.textColor} border-current`}>
                          No transactions
                        </Badge>
                      )}
                      
                      {hasTransactions ? (
                        expandedGroups[periodKey] ? 
                          <ChevronDown className={`h-4 w-4 ${period.textColor}`} /> : 
                          <ChevronRight className={`h-4 w-4 ${period.textColor}`} />
                      ) : null}
                    </div>
                  </div>
                </CardHeader>
              </CollapsibleTrigger>

              {hasTransactions && (
                <CollapsibleContent>
                  <CardContent className="pt-0">
                    {/* Summary Row */}
                    <div className="flex justify-between items-center mb-4 p-3 bg-white/40 rounded-lg">
                      <div className="flex gap-6">
                        {total.income > 0 && (
                          <div className="flex items-center gap-1">
                            <TrendingUp className="h-4 w-4 text-green-600" />
                            <span className="text-sm font-medium text-green-800">
                              {formatCurrency(total.income)}
                            </span>
                          </div>
                        )}
                        <div className="flex items-center gap-1">
                          <TrendingDown className="h-4 w-4 text-red-600" />
                          <span className="text-sm font-medium text-red-800">
                            {formatCurrency(total.expense)}
                          </span>
                        </div>
                      </div>
                      <div className={`text-sm font-medium ${total.balance >= 0 ? 'text-green-800' : 'text-red-800'}`}>
                        Net: {formatCurrency(Math.abs(total.balance))} {total.balance < 0 ? 'deficit' : 'surplus'}
                      </div>
                    </div>

                    {/* Transactions List */}
                    <div className="space-y-2">
                      {groupedTransactions[periodKey]
                        .sort((a, b) => new Date(b.date) - new Date(a.date))
                        .map((transaction, index) => (
                          <div 
                            key={transaction.id || index} 
                            className="flex items-center justify-between p-3 bg-white/60 rounded-lg hover:bg-white/80 transition-colors duration-150"
                          >
                            <div className="flex items-center gap-3">
                              <div className="flex flex-col">
                                <span className="text-sm font-medium text-gray-800">
                                  {transaction.merchant || transaction.description}
                                </span>
                                <span className="text-xs text-gray-600">
                                  {formatTime(transaction.date)}
                                </span>
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <span className={`text-sm font-medium ${
                                transaction.type === 'income' ? 'text-green-700' : 'text-red-700'
                              }`}>
                                {transaction.type === 'income' ? '+' : '-'}{formatCurrency(transaction.amount)}
                              </span>
                              {transaction.currency && transaction.currency !== 'INR' && (
                                <Badge variant="outline" className="text-xs">
                                  {transaction.currency}
                                </Badge>
                              )}
                            </div>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </CollapsibleContent>
              )}
            </Collapsible>
          </Card>
        );
      })}

      {/* Daily Summary */}
      {transactions.length > 0 && (
        <Card className="bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200 mt-6">
          <CardHeader>
            <CardTitle className="text-base font-medium text-gray-800 flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Daily Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(periodTotals).map(([periodKey, total]) => (
                <div key={periodKey} className="text-center">
                  <div className="text-xs text-gray-600 mb-1">
                    {timePeriods[periodKey].label}
                  </div>
                  <div className={`text-sm font-medium ${
                    total.expense > 0 ? 'text-red-700' : 'text-gray-500'
                  }`}>
                    {formatCurrency(total.expense)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {total.count} txns
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TimeBasedTransactionGroups;