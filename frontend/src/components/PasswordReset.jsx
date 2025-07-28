import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import apiService from '../services/api';
import { useToast } from '../hooks/use-toast';

const PasswordReset = ({ onBackToLogin, resetToken = null }) => {
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [token, setToken] = useState(resetToken || '');
  const [step, setStep] = useState(resetToken ? 'reset' : 'request'); // 'request' or 'reset'
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await apiService.forgotPassword(email);
      
      if (response.success) {
        toast({
          title: "Reset Link Sent",
          description: "If this email exists, you will receive a password reset link",
          variant: "default",
        });
        
        // For demo purposes, if token is returned, move to reset step
        if (response.token) {
          setToken(response.token);
          setStep('reset');
          toast({
            title: "Demo Mode",
            description: `Reset token: ${response.token}`,
            variant: "default",
            duration: 10000,
          });
        }
      } else {
        throw new Error(response.error || 'Failed to send reset link');
      }
    } catch (err) {
      toast({
        title: "Error",
        description: err.response?.data?.detail || err.message || 'Failed to send reset link',
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      toast({
        title: "Error",
        description: "Passwords do not match",
        variant: "destructive",
      });
      return;
    }

    if (newPassword.length < 6) {
      toast({
        title: "Error",
        description: "Password must be at least 6 characters long",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await apiService.resetPassword(token, newPassword);
      
      if (response.success) {
        toast({
          title: "Password Reset Successful",
          description: "Your password has been updated. You can now log in with your new password.",
          variant: "default",
        });
        
        // Go back to login after successful reset
        setTimeout(() => {
          onBackToLogin();
        }, 2000);
      } else {
        throw new Error(response.error || 'Failed to reset password');
      }
    } catch (err) {
      toast({
        title: "Error",
        description: err.response?.data?.detail || err.message || 'Failed to reset password',
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (step === 'request') {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">Reset Password</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleRequestReset} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="Enter your email address"
                disabled={isLoading}
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? 'Sending Reset Link...' : 'Send Reset Link'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Remember your password?{' '}
              <button
                onClick={onBackToLogin}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Back to Login
              </button>
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-center">Set New Password</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleResetPassword} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="token">Reset Token</Label>
            <Input
              id="token"
              type="text"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              required
              placeholder="Enter reset token"
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="newPassword">New Password</Label>
            <Input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              placeholder="Enter new password"
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirm New Password</Label>
            <Input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="Confirm new password"
              disabled={isLoading}
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? 'Updating Password...' : 'Update Password'}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            <button
              onClick={onBackToLogin}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              Back to Login
            </button>
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default PasswordReset;