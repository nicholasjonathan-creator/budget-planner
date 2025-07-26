import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Separator } from './ui/separator';
import { toast } from '../hooks/use-toast';
import { 
  Shield, 
  Server, 
  Mail, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Settings,
  Play,
  Square,
  RefreshCw,
  AlertTriangle,
  Activity
} from 'lucide-react';

const ProductionEmailManagement = () => {
  const [productionStatus, setProductionStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState({});

  useEffect(() => {
    loadProductionStatus();
  }, []);

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  };

  const loadProductionStatus = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/production/status`, {
        headers: {
          'Authorization': `Bearer ${getCookie('auth_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProductionStatus(data);
      } else {
        toast({
          title: "Error",
          description: "Failed to load production status",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error loading production status:', error);
      toast({
        title: "Error",
        description: "Failed to load production status",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSchedulerAction = async (action) => {
    setActionLoading(prev => ({ ...prev, [action]: true }));
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/production/${action}-scheduler`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getCookie('auth_token')}`,
        },
      });

      if (response.ok) {
        const result = await response.json();
        toast({
          title: "Success",
          description: result.message,
        });
        await loadProductionStatus(); // Refresh status
      } else {
        toast({
          title: "Error",
          description: `Failed to ${action} scheduler`,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error(`Error ${action} scheduler:`, error);
      toast({
        title: "Error",
        description: `Failed to ${action} scheduler`,
        variant: "destructive",
      });
    } finally {
      setActionLoading(prev => ({ ...prev, [action]: false }));
    }
  };

  const triggerManualEmail = async (emailType) => {
    setActionLoading(prev => ({ ...prev, [emailType]: true }));
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/production/trigger-${emailType}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getCookie('auth_token')}`,
        },
      });

      if (response.ok) {
        const result = await response.json();
        toast({
          title: "Success",
          description: result.message,
        });
      } else {
        toast({
          title: "Error",
          description: `Failed to trigger ${emailType}`,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error(`Error triggering ${emailType}:`, error);
      toast({
        title: "Error",
        description: `Failed to trigger ${emailType}`,
        variant: "destructive",
      });
    } finally {
      setActionLoading(prev => ({ ...prev, [emailType]: false }));
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'complete':
        return <Badge variant="success" className="bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" />Complete</Badge>;
      case 'pending':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800"><Clock className="h-3 w-3 mr-1" />Pending</Badge>;
      case 'error':
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" />Error</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <Shield className="h-6 w-6 mr-2" />
              Production Email Management
            </h2>
            <p className="text-gray-600 mt-1">
              Configure and monitor production email system
            </p>
          </div>
          <Button onClick={loadProductionStatus} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-32 bg-gray-200 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!productionStatus) {
    return (
      <div className="text-center py-8">
        <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <p className="text-gray-600">Failed to load production status</p>
        <Button onClick={loadProductionStatus} className="mt-4">
          <RefreshCw className="h-4 w-4 mr-2" />
          Try Again
        </Button>
      </div>
    );
  }

  const checklist = productionStatus.production_checklist?.checklist || {};
  const completionPercentage = productionStatus.production_checklist?.completion_percentage || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Shield className="h-6 w-6 mr-2" />
            Production Email Management
          </h2>
          <p className="text-gray-600 mt-1">
            Configure and monitor production email system
          </p>
        </div>
        <Button onClick={loadProductionStatus} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* System Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <Server className="h-4 w-4 mr-2" />
              Environment
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {productionStatus.environment || 'development'}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Current environment setting
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <Activity className="h-4 w-4 mr-2" />
              Email Scheduler
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${productionStatus.scheduler?.running ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-lg font-semibold">
                {productionStatus.scheduler?.running ? 'Running' : 'Stopped'}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {productionStatus.scheduler?.jobs || 0} scheduled jobs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <Mail className="h-4 w-4 mr-2" />
              Configuration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {completionPercentage.toFixed(0)}%
            </div>
            <Progress value={completionPercentage} className="mt-2" />
            <p className="text-xs text-gray-500 mt-1">
              Production readiness
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Production Checklist */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <CheckCircle className="h-5 w-5 mr-2" />
            Production Readiness Checklist
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(checklist).map(([key, item]) => (
            <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  {getStatusBadge(item.status)}
                  <div>
                    <p className="font-medium">{item.description}</p>
                    {item.action && (
                      <p className="text-sm text-gray-600 mt-1">{item.action}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Scheduler Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Scheduler Controls
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Email Scheduler Status</p>
              <p className="text-sm text-gray-600">
                {productionStatus.scheduler?.running ? 
                  'Automated emails are being sent according to user preferences' : 
                  'Automated emails are currently disabled'
                }
              </p>
            </div>
            <div className="flex space-x-2">
              <Button
                onClick={() => handleSchedulerAction('start')}
                disabled={productionStatus.scheduler?.running || actionLoading.start}
                size="sm"
                variant={productionStatus.scheduler?.running ? "secondary" : "default"}
              >
                <Play className="h-4 w-4 mr-2" />
                {actionLoading.start ? 'Starting...' : 'Start'}
              </Button>
              <Button
                onClick={() => handleSchedulerAction('stop')}
                disabled={!productionStatus.scheduler?.running || actionLoading.stop}
                size="sm"
                variant="outline"
              >
                <Square className="h-4 w-4 mr-2" />
                {actionLoading.stop ? 'Stopping...' : 'Stop'}
              </Button>
            </div>
          </div>
          
          <Separator />
          
          <div>
            <p className="font-medium mb-3">Manual Email Triggers (Testing)</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Button
                onClick={() => triggerManualEmail('budget-alerts')}
                disabled={actionLoading['budget-alerts']}
                variant="outline"
                size="sm"
              >
                <Mail className="h-4 w-4 mr-2" />
                {actionLoading['budget-alerts'] ? 'Sending...' : 'Trigger Budget Alerts'}
              </Button>
              <Button
                onClick={() => triggerManualEmail('monthly-summaries')}
                disabled={actionLoading['monthly-summaries']}
                variant="outline"
                size="sm"
              >
                <Mail className="h-4 w-4 mr-2" />
                {actionLoading['monthly-summaries'] ? 'Sending...' : 'Trigger Monthly Summaries'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Configuration Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Mail className="h-5 w-5 mr-2" />
            Email Configuration Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-700">SendGrid API Status</p>
              <p className="text-lg">
                {productionStatus.configuration?.api_key_valid ? (
                  <span className="text-green-600 flex items-center">
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Connected
                  </span>
                ) : (
                  <span className="text-red-600 flex items-center">
                    <XCircle className="h-4 w-4 mr-1" />
                    Not Connected
                  </span>
                )}
              </p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-700">Sender Email</p>
              <p className="text-lg">{productionStatus.configuration?.sender_email || 'Not configured'}</p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-700">Sender Verification</p>
              <p className="text-lg">
                {productionStatus.configuration?.sender_verification?.verified ? (
                  <span className="text-green-600 flex items-center">
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Verified
                  </span>
                ) : (
                  <span className="text-yellow-600 flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    Pending Verification
                  </span>
                )}
              </p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-700">Domain Authentication</p>
              <p className="text-lg">
                {productionStatus.configuration?.domain_authentication?.authenticated ? (
                  <span className="text-green-600 flex items-center">
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Authenticated
                  </span>
                ) : (
                  <span className="text-yellow-600 flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    Setup Required
                  </span>
                )}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProductionEmailManagement;