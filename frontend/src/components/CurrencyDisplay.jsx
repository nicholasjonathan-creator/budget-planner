import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { DollarSign, IndianRupee, Euro, PoundSterling, AlertCircle } from 'lucide-react';

const CurrencyDisplay = ({ currencies = [] }) => {
  const [exchangeRates, setExchangeRates] = useState({});
  const [loading, setLoading] = useState(false);

  const getCurrencyIcon = (currency) => {
    switch (currency.toUpperCase()) {
      case 'INR':
        return <IndianRupee className="h-4 w-4" />;
      case 'USD':
        return <DollarSign className="h-4 w-4" />;
      case 'EUR':
        return <Euro className="h-4 w-4" />;
      case 'GBP':
        return <PoundSterling className="h-4 w-4" />;
      default:
        return <DollarSign className="h-4 w-4" />;
    }
  };

  const getCurrencySymbol = (currency) => {
    switch (currency.toUpperCase()) {
      case 'INR':
        return '₹';
      case 'USD':
        return '$';
      case 'EUR':
        return '€';
      case 'GBP':
        return '£';
      case 'JPY':
        return '¥';
      case 'AUD':
        return 'A$';
      case 'CAD':
        return 'C$';
      case 'CHF':
        return 'CHF';
      case 'CNY':
        return '¥';
      case 'SGD':
        return 'S$';
      default:
        return currency.toUpperCase();
    }
  };

  const fetchExchangeRates = async () => {
    setLoading(true);
    try {
      // For demo purposes, using mock exchange rates
      // In production, you'd use a real exchange rate API
      const mockRates = {
        USD: 82.5,
        EUR: 89.2,
        GBP: 103.7,
        JPY: 0.6,
        AUD: 55.8,
        CAD: 61.2,
        CHF: 91.4,
        CNY: 11.4,
        SGD: 61.8
      };
      setExchangeRates(mockRates);
    } catch (error) {
      console.error('Failed to fetch exchange rates:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currencies.length > 0) {
      fetchExchangeRates();
    }
  }, [currencies]);

  if (!currencies.length) {
    return null;
  }

  // Group transactions by currency
  const currencyGroups = currencies.reduce((groups, item) => {
    const currency = item.currency || 'INR';
    if (!groups[currency]) {
      groups[currency] = [];
    }
    groups[currency].push(item);
    return groups;
  }, {});

  return (
    <Card className="mb-6 border-l-4 border-l-blue-500 bg-blue-50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-blue-800">
          <AlertCircle className="h-5 w-5" />
          Multi-Currency Transactions Detected
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <p className="text-blue-700 text-sm">
            Transactions in multiple currencies detected. Here's a breakdown with current exchange rates:
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(currencyGroups).map(([currency, items]) => {
              const totalAmount = items.reduce((sum, item) => sum + (item.amount || 0), 0);
              const exchangeRate = exchangeRates[currency];
              const inrValue = currency === 'INR' ? totalAmount : (totalAmount * (exchangeRate || 1));

              return (
                <Card key={currency} className="bg-white border border-blue-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getCurrencyIcon(currency)}
                        <span className="font-semibold text-gray-900">{currency}</span>
                        <Badge variant="outline" className="text-xs">
                          {items.length} transaction{items.length !== 1 ? 's' : ''}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="text-lg font-bold text-gray-900">
                        {getCurrencySymbol(currency)}{totalAmount.toLocaleString()}
                      </div>
                      
                      {currency !== 'INR' && (
                        <div className="text-sm text-gray-600">
                          {loading ? (
                            <span>Loading rate...</span>
                          ) : exchangeRate ? (
                            <div>
                              <div>Rate: ₹{exchangeRate}/1 {currency}</div>
                              <div className="font-semibold text-green-700">
                                ≈ ₹{inrValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                              </div>
                            </div>
                          ) : (
                            <span className="text-red-600">Rate unavailable</span>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
          
          <div className="flex items-center justify-between pt-2 border-t border-blue-200">
            <p className="text-xs text-blue-600">
              💡 Exchange rates are approximate and for display purposes only
            </p>
            <Button 
              size="sm" 
              variant="outline" 
              onClick={fetchExchangeRates}
              disabled={loading}
              className="text-blue-700 border-blue-300 hover:bg-blue-100"
            >
              {loading ? 'Updating...' : 'Update Rates'}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CurrencyDisplay;