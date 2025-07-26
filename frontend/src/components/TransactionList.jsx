import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { TrendingUp, TrendingDown, MessageSquare, Edit } from 'lucide-react';

const TransactionList = ({ transactions, categories }) => {
  const getCategoryById = (categoryId) => {
    return categories.find(cat => cat.id === categoryId);
  };

  const getSourceIcon = (source) => {
    switch(source) {
      case 'sms':
        return <MessageSquare className="h-4 w-4 text-blue-600" />;
      case 'email':
        return <Edit className="h-4 w-4 text-purple-600" />;
      default:
        return <Edit className="h-4 w-4 text-gray-600" />;
    }
  };

  const getSourceColor = (source) => {
    switch(source) {
      case 'sms':
        return 'bg-blue-100 text-blue-800';
      case 'email':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (transactions.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-gray-500">No transactions found for this period.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Transactions
          <Badge variant="secondary">{transactions.length}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {transactions.map(transaction => {
            const category = getCategoryById(transaction.category_id);
            const date = new Date(transaction.date).toLocaleDateString();
            
            return (
              <div 
                key={transaction.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    {transaction.type === 'income' ? (
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-600" />
                    )}
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: category?.color || '#gray' }}
                    ></div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{transaction.description}</p>
                      <div className="flex items-center gap-1">
                        {getSourceIcon(transaction.source)}
                        <Badge variant="outline" className={`text-xs ${getSourceColor(transaction.source)}`}>
                          {transaction.source.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <span>{category?.name || 'Unknown'}</span>
                      <span>•</span>
                      <span>{date}</span>
                      {transaction.merchant && (
                        <>
                          <span>•</span>
                          <span>{transaction.merchant}</span>
                        </>
                      )}
                      {transaction.balance && (
                        <>
                          <span>•</span>
                          <span>Balance: ${transaction.balance.toFixed(2)}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-bold ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                    {transaction.type === 'income' ? '+' : '-'}${transaction.amount.toFixed(2)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default TransactionList;