import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Loader2, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import apiService from '../services/api';

const MonitoringPanel = () => {
  const [isChecking, setIsChecking] = useState(false);
  const [lastCheckTime, setLastCheckTime] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [autoCheckEnabled, setAutoCheckEnabled] = useState(false);
  const { toast } = useToast();

  // Auto-check on component mount and when user navigates back to app
  useEffect(() => {
    checkSystemHealth();
    
    // Set up auto-check when user becomes active (potential force refresh scenario)
    const handleVisibilityChange = () => {
      if (!document.hidden && autoCheckEnabled) {
        checkUserSyncStatus();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [autoCheckEnabled]);

  const checkSystemHealth = async () => {
    try {
      const health = await apiService.getSystemHealth();
      setSystemHealth(health);
      
      if (health.status === 'unhealthy') {
        toast({
          title: "System Health Alert",
          description: "System is unhealthy. Some features may not work properly.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error checking system health:', error);
      setSystemHealth({ status: 'error', issues: ['Failed to check system health'] });
    }
  };

  const checkUserSyncStatus = async () => {
    setIsChecking(true);
    try {
      const response = await apiService.checkUserSyncStatus();
      setAlerts(response.sync_alerts || []);
      setLastCheckTime(new Date());
      
      if (response.total_alerts > 0) {
        toast({
          title: "Sync Issues Detected",
          description: `Found ${response.total_alerts} potential sync issues. Check the monitoring panel for details.`,
          variant: "destructive",
        });
      } else {
        toast({
          title: "Sync Status OK",
          description: "No sync issues detected. All transactions are properly synchronized.",
          variant: "default",
        });
      }
    } catch (error) {
      console.error('Error checking user sync status:', error);
      toast({
        title: "Sync Check Failed",
        description: "Failed to check sync status. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsChecking(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'unhealthy':
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-50';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-50';
      case 'unhealthy':
      case 'error':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getAlertLevelBadge = (level) => {
    const variants = {
      critical: 'destructive',
      error: 'destructive',
      warning: 'secondary',
      info: 'outline'
    };
    return <Badge variant={variants[level] || 'outline'}>{level.toUpperCase()}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* System Health Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            System Health
            {systemHealth && getStatusIcon(systemHealth.status)}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {systemHealth ? (
            <div className="space-y-4">
              <div className={`p-3 rounded-lg ${getStatusColor(systemHealth.status)}`}>
                <div className="flex items-center gap-2">
                  {getStatusIcon(systemHealth.status)}
                  <span className="font-medium">Status: {systemHealth.status}</span>
                </div>
              </div>
              
              {systemHealth.metrics && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-sm text-gray-700">Database</h4>
                    <p className="text-sm">{systemHealth.metrics.database}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-sm text-gray-700">WhatsApp Service</h4>
                    <p className="text-sm">{systemHealth.metrics.whatsapp_service}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-sm text-gray-700">Recent Transactions</h4>
                    <p className="text-sm">{systemHealth.metrics.recent_transactions}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-sm text-gray-700">Recent Failures</h4>
                    <p className="text-sm">{systemHealth.metrics.recent_failures}</p>
                  </div>
                </div>
              )}
              
              {systemHealth.issues && systemHealth.issues.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm text-gray-700 mb-2">Issues:</h4>
                  <ul className="text-sm space-y-1">
                    {systemHealth.issues.map((issue, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <AlertTriangle className="h-3 w-3 text-red-500 mt-0.5 flex-shrink-0" />
                        {issue}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-4">
              <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
              <p className="text-sm text-gray-500">Loading system health...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Sync Check Card */}
      <Card>
        <CardHeader>
          <CardTitle>Transaction Sync Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">
                  Check if all your WhatsApp transactions are properly synchronized
                </p>
                {lastCheckTime && (
                  <p className="text-xs text-gray-500 mt-1">
                    Last checked: {lastCheckTime.toLocaleTimeString()}
                  </p>
                )}
              </div>
              <Button
                onClick={checkUserSyncStatus}
                disabled={isChecking}
                variant="outline"
              >
                {isChecking ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Checking...
                  </>
                ) : (
                  'Check Sync Status'
                )}
              </Button>
            </div>
            
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="autoCheck"
                checked={autoCheckEnabled}
                onChange={(e) => setAutoCheckEnabled(e.target.checked)}
                className="rounded"
              />
              <label htmlFor="autoCheck" className="text-sm text-gray-600">
                Auto-check when returning to app (detects potential force refresh)
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Sync Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {alerts.map((alert, index) => (
                <Alert key={index} className={`${
                  alert.level === 'critical' || alert.level === 'error' 
                    ? 'border-red-200 bg-red-50' 
                    : 'border-yellow-200 bg-yellow-50'
                }`}>
                  <div className="flex items-start gap-2">
                    {getAlertLevelBadge(alert.level)}
                    <AlertDescription className="flex-1">
                      <div className="space-y-2">
                        <p className="font-medium">{alert.message}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(alert.timestamp).toLocaleString()}
                        </p>
                        {alert.details && (
                          <details className="text-xs">
                            <summary className="cursor-pointer font-medium">Details</summary>
                            <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-x-auto">
                              {JSON.stringify(alert.details, null, 2)}
                            </pre>
                          </details>
                        )}
                      </div>
                    </AlertDescription>
                  </div>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MonitoringPanel;