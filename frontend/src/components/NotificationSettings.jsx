import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Separator } from './ui/separator';
import { Badge } from './ui/badge';
import { toast } from '../hooks/use-toast';
import { 
  Mail, 
  AlertTriangle, 
  Calendar, 
  CreditCard, 
  MessageSquare, 
  User,
  Bell,
  Settings,
  Send,
  BarChart3
} from 'lucide-react';

const NotificationSettings = () => {
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testEmailSending, setTestEmailSending] = useState(false);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/preferences`, {
        headers: {
          'Authorization': `Bearer ${getCookie('auth_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPreferences(data);
      } else {
        toast({
          title: "Error",
          description: "Failed to load notification preferences",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
      toast({
        title: "Error",
        description: "Failed to load notification preferences",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  };

  const updatePreferences = async (updates) => {
    setSaving(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getCookie('auth_token')}`,
        },
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        const updatedPreferences = await response.json();
        setPreferences(updatedPreferences);
        toast({
          title: "Settings Updated",
          description: "Your notification preferences have been saved",
        });
      } else {
        toast({
          title: "Error",
          description: "Failed to update notification preferences",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error updating preferences:', error);
      toast({
        title: "Error",
        description: "Failed to update notification preferences",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const sendTestEmail = async () => {
    setTestEmailSending(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/test-email`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getCookie('auth_token')}`,
        },
      });

      if (response.ok) {
        const result = await response.json();
        toast({
          title: "Test Email Sent",
          description: `Test email sent to ${result.email}`,
        });
      } else {
        toast({
          title: "Error",
          description: "Failed to send test email",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error sending test email:', error);
      toast({
        title: "Error",
        description: "Failed to send test email",
        variant: "destructive",
      });
    } finally {
      setTestEmailSending(false);
    }
  };

  const handleSwitchChange = (key, value) => {
    updatePreferences({ [key]: value });
  };

  const handleInputChange = (key, value) => {
    // Debounce input changes
    clearTimeout(window.notificationInputTimeout);
    window.notificationInputTimeout = setTimeout(() => {
      updatePreferences({ [key]: value });
    }, 1000);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-6 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="text-center py-8">
        <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <p className="text-gray-600">Failed to load notification preferences</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Bell className="h-6 w-6 mr-2" />
            Notification Settings
          </h2>
          <p className="text-gray-600 mt-1">
            Manage your email notifications and preferences
          </p>
        </div>
        <Button
          onClick={sendTestEmail}
          disabled={testEmailSending}
          variant="outline"
          size="sm"
        >
          <Send className="h-4 w-4 mr-2" />
          {testEmailSending ? 'Sending...' : 'Send Test Email'}
        </Button>
      </div>

      {/* Email Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Mail className="h-5 w-5 mr-2" />
            Email Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">Email Notifications</Label>
              <p className="text-sm text-gray-500">
                Enable or disable all email notifications
              </p>
            </div>
            <Switch
              checked={preferences.email_enabled}
              onCheckedChange={(checked) => handleSwitchChange('email_enabled', checked)}
              disabled={saving}
            />
          </div>

          {preferences.email_enabled && (
            <div className="space-y-3 pt-3 border-t">
              <div>
                <Label htmlFor="email_address" className="text-sm font-medium">
                  Alternative Email Address (Optional)
                </Label>
                <Input
                  id="email_address"
                  type="email"
                  placeholder="Leave empty to use account email"
                  defaultValue={preferences.email_address || ''}
                  onChange={(e) => handleInputChange('email_address', e.target.value || null)}
                  className="mt-1"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Notifications will be sent to this address instead of your account email
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Budget Alerts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2" />
            Budget Alerts
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">Budget Limit Alerts</Label>
              <p className="text-sm text-gray-500">
                Get notified when you approach or exceed budget limits
              </p>
            </div>
            <Switch
              checked={preferences.budget_alerts_enabled}
              onCheckedChange={(checked) => handleSwitchChange('budget_alerts_enabled', checked)}
              disabled={saving || !preferences.email_enabled}
            />
          </div>

          {preferences.budget_alerts_enabled && preferences.email_enabled && (
            <div className="space-y-3 pt-3 border-t">
              <div>
                <Label htmlFor="budget_threshold" className="text-sm font-medium">
                  Alert Threshold
                </Label>
                <div className="flex items-center space-x-2 mt-1">
                  <Input
                    id="budget_threshold"
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    defaultValue={preferences.budget_alert_threshold}
                    onChange={(e) => handleInputChange('budget_alert_threshold', parseFloat(e.target.value))}
                    className="w-24"
                  />
                  <span className="text-sm text-gray-500">
                    ({(preferences.budget_alert_threshold * 100).toFixed(0)}% of budget)
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Send alert when spending reaches this percentage of the budget limit
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Summary Reports */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="h-5 w-5 mr-2" />
            Summary Reports
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Weekly Summary */}
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">Weekly Summary</Label>
              <p className="text-sm text-gray-500">
                Get weekly spending and income summaries
              </p>
            </div>
            <Switch
              checked={preferences.weekly_summary_enabled}
              onCheckedChange={(checked) => handleSwitchChange('weekly_summary_enabled', checked)}
              disabled={saving || !preferences.email_enabled}
            />
          </div>

          {preferences.weekly_summary_enabled && preferences.email_enabled && (
            <div className="ml-6 space-y-2">
              <Label htmlFor="weekly_day" className="text-sm font-medium">
                Send on Day
              </Label>
              <select
                id="weekly_day"
                value={preferences.weekly_summary_day}
                onChange={(e) => handleSwitchChange('weekly_summary_day', parseInt(e.target.value))}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value={1}>Monday</option>
                <option value={2}>Tuesday</option>
                <option value={3}>Wednesday</option>
                <option value={4}>Thursday</option>
                <option value={5}>Friday</option>
                <option value={6}>Saturday</option>
                <option value={7}>Sunday</option>
              </select>
            </div>
          )}

          <Separator />

          {/* Monthly Summary */}
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">Monthly Summary</Label>
              <p className="text-sm text-gray-500">
                Get comprehensive monthly financial reports
              </p>
            </div>
            <Switch
              checked={preferences.monthly_summary_enabled}
              onCheckedChange={(checked) => handleSwitchChange('monthly_summary_enabled', checked)}
              disabled={saving || !preferences.email_enabled}
            />
          </div>

          {preferences.monthly_summary_enabled && preferences.email_enabled && (
            <div className="ml-6 space-y-2">
              <Label htmlFor="monthly_day" className="text-sm font-medium">
                Send on Day of Month
              </Label>
              <Input
                id="monthly_day"
                type="number"
                min="1"
                max="28"
                defaultValue={preferences.monthly_summary_day}
                onChange={(e) => handleInputChange('monthly_summary_day', parseInt(e.target.value))}
                className="w-20"
              />
              <p className="text-xs text-gray-500">
                Day of the month to send summary (1-28)
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Transaction Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <CreditCard className="h-5 w-5 mr-2" />
            Transaction Notifications
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">Transaction Confirmations</Label>
              <p className="text-sm text-gray-500">
                Get notified when transactions are added to your account
              </p>
            </div>
            <Switch
              checked={preferences.transaction_confirmation_enabled}
              onCheckedChange={(checked) => handleSwitchChange('transaction_confirmation_enabled', checked)}
              disabled={saving || !preferences.email_enabled}
            />
          </div>

          {preferences.transaction_confirmation_enabled && preferences.email_enabled && (
            <div className="space-y-3 pt-3 border-t">
              <div>
                <Label htmlFor="transaction_threshold" className="text-sm font-medium">
                  Minimum Amount for Notifications
                </Label>
                <div className="flex items-center space-x-2 mt-1">
                  <span className="text-sm">₹</span>
                  <Input
                    id="transaction_threshold"
                    type="number"
                    min="0"
                    step="100"
                    defaultValue={preferences.transaction_confirmation_threshold}
                    onChange={(e) => handleInputChange('transaction_confirmation_threshold', parseFloat(e.target.value))}
                    className="w-32"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Only send notifications for transactions above this amount
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* SMS Processing */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageSquare className="h-5 w-5 mr-2" />
            SMS Processing
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">SMS Processing Reports</Label>
              <p className="text-sm text-gray-500">
                Get summaries of SMS transaction processing
              </p>
            </div>
            <Switch
              checked={preferences.sms_processing_enabled}
              onCheckedChange={(checked) => handleSwitchChange('sms_processing_enabled', checked)}
              disabled={saving || !preferences.email_enabled}
            />
          </div>

          {preferences.sms_processing_enabled && preferences.email_enabled && (
            <div className="space-y-3 pt-3 border-t">
              <div>
                <Label htmlFor="sms_frequency" className="text-sm font-medium">
                  Report Frequency
                </Label>
                <select
                  id="sms_frequency"
                  value={preferences.sms_processing_frequency}
                  onChange={(e) => handleSwitchChange('sms_processing_frequency', e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm mt-1"
                >
                  <option value="instant">Instant</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analytics Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            Analytics & Insights
          </CardTitle>
          <CardDescription>
            Get intelligent insights about your spending patterns and financial health
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Spending Alerts */}
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">Spending Alerts</Label>
              <p className="text-sm text-gray-500">
                Get notified about unusual spending patterns and anomalies
              </p>
            </div>
            <Switch
              checked={preferences.spending_alerts_enabled}
              onCheckedChange={(checked) => handleSwitchChange('spending_alerts_enabled', checked)}
              disabled={saving || !preferences.email_enabled}
            />
          </div>

          {preferences.spending_alerts_enabled && preferences.email_enabled && (
            <div className="space-y-3 pt-3 border-t">
              <div>
                <Label htmlFor="alert_severity" className="text-sm font-medium">
                  Alert Sensitivity
                </Label>
                <select
                  id="alert_severity"
                  value={preferences.spending_alert_severity_threshold}
                  onChange={(e) => handleSwitchChange('spending_alert_severity_threshold', e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm mt-1"
                >
                  <option value="low">Low - All alerts</option>
                  <option value="medium">Medium - Important alerts</option>
                  <option value="high">High - Critical alerts only</option>
                  <option value="critical">Critical - Emergency alerts only</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Choose how sensitive you want the spending anomaly detection to be
                </p>
              </div>
            </div>
          )}

          {/* Financial Health Reports */}
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">Financial Health Reports</Label>
              <p className="text-sm text-gray-500">
                Monthly reports with your financial health score and recommendations
              </p>
            </div>
            <Switch
              checked={preferences.financial_health_reports_enabled}
              onCheckedChange={(checked) => handleSwitchChange('financial_health_reports_enabled', checked)}
              disabled={saving || !preferences.email_enabled}
            />
          </div>

          {/* Budget Recommendations */}
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">AI Budget Recommendations</Label>
              <p className="text-sm text-gray-500">
                Smart suggestions to optimize your budget based on spending patterns
              </p>
            </div>
            <Switch
              checked={preferences.budget_recommendations_enabled}
              onCheckedChange={(checked) => handleSwitchChange('budget_recommendations_enabled', checked)}
              disabled={saving || !preferences.email_enabled}
            />
          </div>

          {/* Weekly Analytics Digest */}
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">Weekly Analytics Digest</Label>
              <p className="text-sm text-gray-500">
                Weekly summary of your spending trends and financial insights
              </p>
            </div>
            <Switch
              checked={preferences.weekly_analytics_digest_enabled}
              onCheckedChange={(checked) => handleSwitchChange('weekly_analytics_digest_enabled', checked)}
              disabled={saving || !preferences.email_enabled}
            />
          </div>
        </CardContent>
      </Card>

      {/* Account Updates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="h-5 w-5 mr-2" />
            Account Updates
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base font-medium">Account & Security Updates</Label>
              <p className="text-sm text-gray-500">
                Important notifications about your account and security
              </p>
            </div>
            <Switch
              checked={preferences.account_updates_enabled}
              onCheckedChange={(checked) => handleSwitchChange('account_updates_enabled', checked)}
              disabled={saving || !preferences.email_enabled}
            />
          </div>
        </CardContent>
      </Card>

      {/* Status */}
      {saving && (
        <div className="flex items-center justify-center py-4">
          <div className="flex items-center space-x-2 text-blue-600">
            <Settings className="h-4 w-4 animate-spin" />
            <span className="text-sm">Saving preferences...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationSettings;