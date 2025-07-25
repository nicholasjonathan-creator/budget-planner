import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Edit2, Save, X } from 'lucide-react';
import { mockCategories } from './mock/mockData';

const BudgetLimitsManager = ({ budgetLimits, onUpdateLimits, currentTransactions }) => {
  const [editingCategory, setEditingCategory] = useState(null);
  const [editValue, setEditValue] = useState('');

  const handleStartEdit = (categoryId, currentLimit) => {
    setEditingCategory(categoryId);
    setEditValue(currentLimit.toString());
  };

  const handleSaveEdit = (categoryId) => {
    const newLimit = parseFloat(editValue);
    if (newLimit >= 0) {
      onUpdateLimits({
        ...budgetLimits,
        [categoryId]: {
          ...budgetLimits[categoryId],
          limit: newLimit
        }
      });
    }
    setEditingCategory(null);
    setEditValue('');
  };

  const handleCancelEdit = () => {
    setEditingCategory(null);
    setEditValue('');
  };

  const calculateSpent = (categoryId) => {
    return currentTransactions
      .filter(t => t.categoryId === categoryId && t.type === 'expense')
      .reduce((sum, t) => sum + t.amount, 0);
  };

  const getBudgetStatus = (spent, limit) => {
    const percentage = (spent / limit) * 100;
    if (percentage >= 100) return { status: 'over', color: 'bg-red-500' };
    if (percentage >= 80) return { status: 'warning', color: 'bg-amber-500' };
    return { status: 'good', color: 'bg-green-500' };
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Budget Limits</h2>
        <p className="text-gray-600">Set and manage your spending limits by category</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {mockCategories.expense.map(category => {
          const budget = budgetLimits[category.id] || { limit: 0, spent: 0 };
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
                        <span className="font-bold">${budget.limit.toFixed(2)}</span>
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
                    <span>Spent: ${spent.toFixed(2)}</span>
                    <span>Remaining: ${Math.max(0, budget.limit - spent).toFixed(2)}</span>
                  </div>
                  <Progress 
                    value={Math.min(percentage, 100)} 
                    className="h-2"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>0%</span>
                    <span>{percentage.toFixed(1)}%</span>
                    <span>100%</span>
                  </div>
                </div>

                {spent > budget.limit && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-700">
                      <strong>Over budget by ${(spent - budget.limit).toFixed(2)}</strong>
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