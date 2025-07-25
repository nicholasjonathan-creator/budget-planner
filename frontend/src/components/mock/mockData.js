// Mock data for budget planner app - will be replaced with backend integration later

export const mockCategories = {
  income: [
    { id: 1, name: 'Salary', color: '#a7f3d0' },
    { id: 2, name: 'Freelance', color: '#bfdbfe' },
    { id: 3, name: 'Investment', color: '#ddd6fe' },
    { id: 4, name: 'Other Income', color: '#fce7f3' }
  ],
  expense: [
    { id: 5, name: 'Food & Dining', color: '#fed7d7' },
    { id: 6, name: 'Transportation', color: '#feebc8' },
    { id: 7, name: 'Entertainment', color: '#c6f6d5' },
    { id: 8, name: 'Shopping', color: '#bee3f8' },
    { id: 9, name: 'Bills & Utilities', color: '#e9d8fd' },
    { id: 10, name: 'Healthcare', color: '#fbb6ce' },
    { id: 11, name: 'Education', color: '#fed7e2' },
    { id: 12, name: 'Other Expenses', color: '#fef5e7' }
  ]
};

export const mockTransactions = [
  { id: 1, type: 'income', categoryId: 1, amount: 5000, description: 'Monthly salary', date: '2025-07-01' },
  { id: 2, type: 'income', categoryId: 2, amount: 800, description: 'Freelance project', date: '2025-07-05' },
  { id: 3, type: 'expense', categoryId: 5, amount: 120, description: 'Grocery shopping', date: '2025-07-02' },
  { id: 4, type: 'expense', categoryId: 6, amount: 80, description: 'Gas and parking', date: '2025-07-03' },
  { id: 5, type: 'expense', categoryId: 7, amount: 60, description: 'Movie tickets', date: '2025-07-04' },
  { id: 6, type: 'expense', categoryId: 5, amount: 85, description: 'Restaurant dinner', date: '2025-07-06' },
  { id: 7, type: 'expense', categoryId: 9, amount: 200, description: 'Electricity bill', date: '2025-07-07' },
  { id: 8, type: 'expense', categoryId: 8, amount: 150, description: 'Clothing', date: '2025-07-08' },
  { id: 9, type: 'income', categoryId: 3, amount: 300, description: 'Dividend payment', date: '2025-07-10' },
  { id: 10, type: 'expense', categoryId: 10, amount: 200, description: 'Doctor visit', date: '2025-07-12' }
];

export const mockBudgetLimits = {
  5: { limit: 400, spent: 205 }, // Food & Dining
  6: { limit: 200, spent: 80 },  // Transportation
  7: { limit: 150, spent: 60 },  // Entertainment
  8: { limit: 300, spent: 150 }, // Shopping
  9: { limit: 500, spent: 200 }, // Bills & Utilities
  10: { limit: 250, spent: 200 }, // Healthcare
  11: { limit: 100, spent: 0 },   // Education
  12: { limit: 100, spent: 0 }    // Other Expenses
};

// Helper functions for mock data
export const getCategoryById = (id) => {
  const allCategories = [...mockCategories.income, ...mockCategories.expense];
  return allCategories.find(cat => cat.id === id);
};

export const getTransactionsByMonth = (month, year) => {
  return mockTransactions.filter(transaction => {
    const transactionDate = new Date(transaction.date);
    return transactionDate.getMonth() === month && transactionDate.getFullYear() === year;
  });
};

export const calculateCategoryTotals = (transactions) => {
  const totals = {};
  transactions.forEach(transaction => {
    const categoryId = transaction.categoryId;
    if (!totals[categoryId]) {
      totals[categoryId] = { income: 0, expense: 0 };
    }
    totals[categoryId][transaction.type] += transaction.amount;
  });
  return totals;
};