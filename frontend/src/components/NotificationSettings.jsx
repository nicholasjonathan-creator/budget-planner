import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Settings, Bell, Info } from 'lucide-react';

const NotificationSettings = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <Bell className="h-8 w-8 text-blue-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-900">Notification Settings</h2>
        </div>
        <p className="text-gray-600">
          Budget Planner uses dashboard-based notifications for a cleaner experience
        </p>
      </div>

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-900 flex items-center">
            <Info className="h-5 w-5 mr-2" />
            Dashboard-Only Mode
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-blue-800">
            <p>
              ✅ <strong>Email notifications are disabled</strong> to keep things simple and focused.
            </p>
            <p>
              📊 All insights, alerts, and reports are available directly in your dashboard tabs:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
              <div className="bg-white p-3 rounded-lg">
                <div className="font-semibold">📈 Analytics Tab</div>
                <div className="text-sm text-gray-600">Financial health, spending patterns, insights</div>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <div className="font-semibold">💰 Budget Limits</div> 
                <div className="text-sm text-gray-600">Budget tracking, alerts, progress</div>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <div className="font-semibold">📱 WhatsApp Integration</div>
                <div className="text-sm text-gray-600">SMS processing, transaction automation</div>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <div className="font-semibold">🏠 Overview Dashboard</div>
                <div className="text-sm text-gray-600">Summary cards, recent transactions</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Benefits Card */}
      <Card className="bg-green-50 border-green-200">
        <CardHeader>
          <CardTitle className="text-green-900 flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Benefits of Dashboard-Only Mode
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-green-800">
            <div>
              <h4 className="font-semibold mb-2">🎯 Focused Experience</h4>
              <p className="text-sm">No email distractions - check insights when you need them</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">🔄 Real-time Data</h4>
              <p className="text-sm">Always up-to-date information in your dashboard</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">🎨 Clean Interface</h4>
              <p className="text-sm">Simpler app without email configuration complexity</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">⚡ Better Performance</h4>
              <p className="text-sm">Faster load times without background email processing</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Access */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Badge variant="secondary" className="mr-2">Quick Access</Badge>
            Where to Find Everything
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span>💰 View spending alerts and budget status</span>
              <Badge variant="outline">Budget Limits Tab</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span>📊 Check financial health and analytics</span>
              <Badge variant="outline">Analytics Tab</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span>📱 Process SMS and view transaction history</span>
              <Badge variant="outline">WhatsApp Tab</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span>📋 Manually classify failed SMS messages</span>
              <Badge variant="outline">Manual Tab</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NotificationSettings;