import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Edit2, Save, X } from 'lucide-react';

const BudgetLimitsManager = ({ budgetLimits, categories, onUpdateLimits, currentTransactions }) => {
  const [editingCategory, setEditingCategory] = useState(null);
  const [editValue, setEditValue] = useState('');

  const handleStartEdit = (categoryId, currentLimit) => {
    setEditingCategory(categoryId);
    setEditValue(currentLimit.toString());
  };

  const handleSaveEdit = (categoryId) => {
    const newLimit = parseFloat(editValue);
    if (newLimit >= 0) {
      // Create new limits object
      const newLimits = { ...budgetLimits };
      const existingBudget = budgetLimits.find(b => b.category_id === categoryId);
      
      if (existingBudget) {
        // Update existing budget
        newLimits[categoryId] = {
          ...existingBudget,
          limit: newLimit
        };
      } else {
        // Create new budget
        newLimits[categoryId] = {
          category_id: categoryId,
          limit: newLimit,
          spent: 0
        };
      }
      
      onUpdateLimits(newLimits);
    }
    setEditingCategory(null);
    setEditValue('');
  };

  const handleCancelEdit = () => {
    setEditingCategory(null);
    setEditValue('');
  };

  const calculateSpent = (categoryId) => {
    // Calculate real-time spent amount from current transactions
    const spent = currentTransactions
      .filter(t => t.category_id === categoryId && t.type === 'expense')
      .reduce((sum, t) => sum + t.amount, 0);
    
    // Return the calculated amount, which updates dynamically as transactions change
    return spent;
  };

  const getBudgetForCategory = (categoryId) => {
    const budget = budgetLimits.find(b => b.category_id === categoryId);
    return budget || { limit: 0, spent: 0 };
  };

  const getBudgetStatus = (spent, limit) => {
    const percentage = limit > 0 ? (spent / limit) * 100 : 0;
    if (percentage >= 100) return { status: 'over', color: 'bg-red-500' };
    if (percentage >= 80) return { status: 'warning', color: 'bg-amber-500' };
    return { status: 'good', color: 'bg-green-500' };
  };

  // Filter to only show expense categories
  const expenseCategories = categories.filter(cat => cat.type === 'expense');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Budget Limits</h2>
        <p className="text-gray-600">Set and manage your spending limits by category</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {expenseCategories.map(category => {
          const budget = getBudgetForCategory(category.id);
          const spent = calculateSpent(category.id);
          const percentage = budget.limit > 0 ? (spent / budget.limit) * 100 : 0;
          const budgetStatus = getBudgetStatus(spent, budget.limit);
          const isEditing = editingCategory === category.id;

          return (
            <Card key={category.id} className="border-l-4" style={{ borderLeftColor: category.color }}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <div 
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: category.color }}
                    ></div>
                    {category.name}
                  </CardTitle>
                  {budgetStatus.status === 'over' && (
                    <Badge variant="destructive">Over Budget</Badge>
                  )}
                  {budgetStatus.status === 'warning' && (
                    <Badge variant="outline" className="border-amber-500 text-amber-700">
                      Near Limit
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Budget Limit</span>
                  <div className="flex items-center gap-2">
                    {isEditing ? (
                      <div className="flex items-center gap-2">
                        <Input
                          type="number"
                          step="0.01"
                          min="0"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="w-20 h-8"
                        />
                        <Button
                          size="sm"
                          onClick={() => handleSaveEdit(category.id)}
                          className="h-8 w-8 p-0"
                        >
                          <Save className="h-3 w-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={handleCancelEdit}
                          className="h-8 w-8 p-0"
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <span className="font-bold">₹{budget.limit.toLocaleString('en-IN')}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleStartEdit(category.id, budget.limit)}
                          className="h-8 w-8 p-0"
                        >
                          <Edit2 className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="flex items-center gap-1">
                      <span className="text-red-600">Spent:</span>
                      <span className="font-semibold text-red-700">₹{spent.toLocaleString('en-IN')}</span>
                      {budget.limit > 0 && (
                        <span className="text-xs text-gray-500">
                          ({((spent / budget.limit) * 100).toFixed(1)}%)
                        </span>
                      )}
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="text-green-600">Remaining:</span>
                      <span className="font-semibold text-green-700">₹{Math.max(0, budget.limit - spent).toLocaleString('en-IN')}</span>
                    </span>
                  </div>
                  <div className="relative">
                    <Progress 
                      value={Math.min(percentage, 100)} 
                      className="h-3"
                    />
                    {/* Dynamic counter that moves with progress */}
                    <div 
                      className="absolute top-0 h-3 bg-gradient-to-r from-transparent to-white/50 pointer-events-none"
                      style={{ 
                        width: `${Math.min(percentage, 100)}%`,
                        transition: 'width 0.3s ease-in-out'
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>₹0</span>
                    <span className={`font-semibold ${percentage > 100 ? 'text-red-600' : percentage > 80 ? 'text-amber-600' : 'text-green-600'}`}>
                      {percentage.toFixed(1)}% used
                    </span>
                    <span>₹{budget.limit.toLocaleString('en-IN')}</span>
                  </div>
                </div>

                {spent > budget.limit && budget.limit > 0 && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-700">
                      <strong>Over budget by ₹{(spent - budget.limit).toLocaleString('en-IN')}</strong>
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default BudgetLimitsManager;