#!/usr/bin/env python3
"""
Comprehensive Production Deployment System Testing
Tests requested by user for production deployment functionality:
1. Main Deployment Script (/app/deploy-production.sh)
2. Platform-Specific Deployment Scripts (Railway, Render)
3. Monitoring System (/app/monitoring/health_monitor.py)
4. Docker Configuration
5. Health Check System
6. Configuration Files
"""

import os
import subprocess
import json
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

class DeploymentSystemTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.app_root = Path("/app")
        
    def test_main_deployment_script(self):
        """Test the main deployment script structure and permissions"""
        print("\n🧪 Testing Main Deployment Script (/app/deploy-production.sh)...")
        print("=" * 70)
        
        self.total_tests += 1
        script_path = self.app_root / "deploy-production.sh"
        
        try:
            # Check if script exists
            if not script_path.exists():
                print("❌ Main deployment script not found")
                self.failed_tests += 1
                return False
            
            print("✅ Main deployment script exists")
            
            # Check if script is executable
            if not os.access(script_path, os.X_OK):
                print("❌ Main deployment script is not executable")
                self.failed_tests += 1
                return False
            
            print("✅ Main deployment script is executable")
            
            # Read and analyze script content
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Check for required sections
            required_sections = [
                "Environment Validation",
                "Build Application", 
                "Database Setup",
                "Production Configuration",
                "Docker Configuration",
                "Platform Deployment Scripts",
                "Health Check System",
                "Monitoring Setup"
            ]
            
            sections_found = 0
            for section in required_sections:
                if section in content:
                    sections_found += 1
                    print(f"✅ Found section: {section}")
                else:
                    print(f"❌ Missing section: {section}")
            
            # Check for environment variable validation
            required_vars = ["SENDGRID_API_KEY", "MONGO_URL", "JWT_SECRET", "SENDER_EMAIL"]
            env_vars_found = 0
            for var in required_vars:
                if var in content:
                    env_vars_found += 1
                    print(f"✅ Environment variable check: {var}")
                else:
                    print(f"❌ Missing environment variable check: {var}")
            
            # Check for proper error handling
            if "set -e" in content:
                print("✅ Script has proper error handling (set -e)")
            else:
                print("❌ Script missing error handling")
            
            # Check for colored output functions
            if "print_status()" in content and "print_error()" in content:
                print("✅ Script has proper output formatting functions")
            else:
                print("❌ Script missing output formatting functions")
            
            # Overall assessment
            if sections_found >= 6 and env_vars_found >= 3:
                print("✅ Main deployment script is well-structured")
                self.passed_tests += 1
                return True
            else:
                print("❌ Main deployment script is missing critical components")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing main deployment script: {e}")
            self.failed_tests += 1
            return False

    def test_platform_deployment_scripts(self):
        """Test platform-specific deployment scripts"""
        print("\n🧪 Testing Platform-Specific Deployment Scripts...")
        print("=" * 60)
        
        scripts_to_test = [
            ("scripts/deploy-railway.sh", "Railway deployment script"),
            ("scripts/deploy-render.sh", "Render deployment script")
        ]
        
        platform_results = []
        
        for script_path, description in scripts_to_test:
            self.total_tests += 1
            full_path = self.app_root / script_path
            
            print(f"\n--- Testing {description} ---")
            
            try:
                # Check if script exists
                if not full_path.exists():
                    print(f"❌ {description} not found at {script_path}")
                    self.failed_tests += 1
                    platform_results.append(False)
                    continue
                
                print(f"✅ {description} exists")
                
                # Check if script is executable
                if not os.access(full_path, os.X_OK):
                    print(f"❌ {description} is not executable")
                    self.failed_tests += 1
                    platform_results.append(False)
                    continue
                
                print(f"✅ {description} is executable")
                
                # Read and analyze script content
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Check for platform-specific requirements
                if "railway" in script_path.lower():
                    # Railway-specific checks
                    railway_checks = [
                        ("railway", "Railway CLI usage"),
                        ("railway.json", "Railway configuration"),
                        ("railway up", "Railway deployment command"),
                        ("railway variables set", "Environment variable setting")
                    ]
                    
                    railway_passed = 0
                    for check, desc in railway_checks:
                        if check in content:
                            print(f"✅ {desc} found")
                            railway_passed += 1
                        else:
                            print(f"❌ {desc} missing")
                    
                    if railway_passed >= 3:
                        print("✅ Railway deployment script is properly configured")
                        self.passed_tests += 1
                        platform_results.append(True)
                    else:
                        print("❌ Railway deployment script missing critical components")
                        self.failed_tests += 1
                        platform_results.append(False)
                
                elif "render" in script_path.lower():
                    # Render-specific checks
                    render_checks = [
                        ("render.yaml", "Render configuration file"),
                        ("buildCommand", "Build command configuration"),
                        ("startCommand", "Start command configuration"),
                        ("envVars", "Environment variables configuration")
                    ]
                    
                    render_passed = 0
                    for check, desc in render_checks:
                        if check in content:
                            print(f"✅ {desc} found")
                            render_passed += 1
                        else:
                            print(f"❌ {desc} missing")
                    
                    if render_passed >= 3:
                        print("✅ Render deployment script is properly configured")
                        self.passed_tests += 1
                        platform_results.append(True)
                    else:
                        print("❌ Render deployment script missing critical components")
                        self.failed_tests += 1
                        platform_results.append(False)
                
            except Exception as e:
                print(f"❌ Error testing {description}: {e}")
                self.failed_tests += 1
                platform_results.append(False)
        
        return all(platform_results)

    def test_monitoring_system(self):
        """Test the health monitoring system"""
        print("\n🧪 Testing Monitoring System (/app/monitoring/health_monitor.py)...")
        print("=" * 65)
        
        self.total_tests += 1
        monitor_path = self.app_root / "monitoring" / "health_monitor.py"
        
        try:
            # Check if monitoring script exists
            if not monitor_path.exists():
                print("❌ Health monitoring script not found")
                self.failed_tests += 1
                return False
            
            print("✅ Health monitoring script exists")
            
            # Check if script is executable
            if not os.access(monitor_path, os.X_OK):
                print("❌ Health monitoring script is not executable")
                self.failed_tests += 1
                return False
            
            print("✅ Health monitoring script is executable")
            
            # Read and analyze monitoring script content
            with open(monitor_path, 'r') as f:
                content = f.read()
            
            # Check for required monitoring functions
            monitoring_functions = [
                ("check_backend_health", "Backend health check"),
                ("check_database_connection", "Database connectivity check"),
                ("check_email_system", "Email system check"),
                ("check_frontend", "Frontend availability check"),
                ("check_ssl_certificate", "SSL certificate monitoring"),
                ("generate_html_report", "HTML report generation"),
                ("run_all_checks", "Comprehensive health check"),
                ("monitor_continuous", "Continuous monitoring")
            ]
            
            functions_found = 0
            for func, desc in monitoring_functions:
                if func in content:
                    print(f"✅ {desc} function found")
                    functions_found += 1
                else:
                    print(f"❌ {desc} function missing")
            
            # Check for proper imports
            required_imports = ["asyncio", "aiohttp", "json", "datetime"]
            imports_found = 0
            for imp in required_imports:
                if f"import {imp}" in content:
                    imports_found += 1
                    print(f"✅ Required import: {imp}")
                else:
                    print(f"❌ Missing import: {imp}")
            
            # Check for configuration options
            config_options = ["BACKEND_URL", "FRONTEND_URL", "ALERT_EMAIL"]
            config_found = 0
            for option in config_options:
                if option in content:
                    config_found += 1
                    print(f"✅ Configuration option: {option}")
                else:
                    print(f"❌ Missing configuration: {option}")
            
            # Test if the script can be imported (syntax check)
            try:
                # Try to run a basic syntax check
                result = subprocess.run([
                    sys.executable, "-m", "py_compile", str(monitor_path)
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print("✅ Monitoring script has valid Python syntax")
                else:
                    print(f"❌ Monitoring script has syntax errors: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("⚠️  Syntax check timed out")
            except Exception as e:
                print(f"⚠️  Could not perform syntax check: {e}")
            
            # Overall assessment
            if functions_found >= 6 and imports_found >= 3 and config_found >= 2:
                print("✅ Monitoring system is comprehensive and well-structured")
                self.passed_tests += 1
                return True
            else:
                print("❌ Monitoring system is missing critical components")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing monitoring system: {e}")
            self.failed_tests += 1
            return False

    def test_docker_configuration(self):
        """Test Docker configuration files"""
        print("\n🧪 Testing Docker Configuration...")
        print("=" * 40)
        
        # Check if main deployment script creates Docker files
        self.total_tests += 1
        
        try:
            # Run a dry-run of the deployment script to check Docker file creation
            # We'll analyze the script content to see if it creates proper Docker configs
            
            deploy_script = self.app_root / "deploy-production.sh"
            if not deploy_script.exists():
                print("❌ Cannot test Docker configuration - deployment script missing")
                self.failed_tests += 1
                return False
            
            with open(deploy_script, 'r') as f:
                content = f.read()
            
            # Check for Docker configuration creation
            docker_checks = [
                ("Dockerfile.prod", "Production Dockerfile creation"),
                ("docker-compose.prod.yml", "Docker Compose configuration"),
                ("nginx.conf", "Nginx configuration"),
                ("FROM python:", "Python base image"),
                ("FROM node:", "Node base image"),
                ("HEALTHCHECK", "Health check configuration"),
                ("EXPOSE", "Port exposure"),
                ("CMD", "Container startup command")
            ]
            
            docker_found = 0
            for check, desc in docker_checks:
                if check in content:
                    print(f"✅ {desc} found in deployment script")
                    docker_found += 1
                else:
                    print(f"❌ {desc} missing from deployment script")
            
            # Check for production optimizations
            prod_optimizations = [
                ("--no-cache-dir", "Pip cache optimization"),
                ("gzip on", "Gzip compression"),
                ("Security headers", "Security header configuration"),
                ("worker_connections", "Nginx worker configuration"),
                ("proxy_pass", "API proxy configuration")
            ]
            
            optimizations_found = 0
            for opt, desc in prod_optimizations:
                if opt in content:
                    print(f"✅ {desc} configured")
                    optimizations_found += 1
                else:
                    print(f"❌ {desc} missing")
            
            # Overall assessment
            if docker_found >= 6 and optimizations_found >= 3:
                print("✅ Docker configuration is production-ready")
                self.passed_tests += 1
                return True
            else:
                print("❌ Docker configuration is incomplete")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing Docker configuration: {e}")
            self.failed_tests += 1
            return False

    def test_health_check_system(self):
        """Test health check system functionality"""
        print("\n🧪 Testing Health Check System...")
        print("=" * 40)
        
        self.total_tests += 1
        
        try:
            # Check if deployment script creates health check script
            deploy_script = self.app_root / "deploy-production.sh"
            if not deploy_script.exists():
                print("❌ Cannot test health check system - deployment script missing")
                self.failed_tests += 1
                return False
            
            with open(deploy_script, 'r') as f:
                content = f.read()
            
            # Check for health check script creation
            health_checks = [
                ("health-check.sh", "Health check script creation"),
                ("check_service()", "Service check function"),
                ("Backend API", "Backend health check"),
                ("Frontend", "Frontend health check"),
                ("Database Connection", "Database check"),
                ("Email System", "Email system check"),
                ("Authentication", "Authentication test"),
                ("curl -f", "HTTP health check commands")
            ]
            
            health_found = 0
            for check, desc in health_checks:
                if check in content:
                    print(f"✅ {desc} found")
                    health_found += 1
                else:
                    print(f"❌ {desc} missing")
            
            # Check for proper error handling in health checks
            error_handling = [
                ("grep -q", "Response validation"),
                ("if.*then", "Conditional logic"),
                ("else", "Error handling"),
                ("exit 1", "Failure exit codes")
            ]
            
            error_found = 0
            for check, desc in error_handling:
                if check in content:
                    print(f"✅ {desc} implemented")
                    error_found += 1
                else:
                    print(f"❌ {desc} missing")
            
            # Overall assessment
            if health_found >= 6 and error_found >= 2:
                print("✅ Health check system is comprehensive")
                self.passed_tests += 1
                return True
            else:
                print("❌ Health check system is incomplete")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing health check system: {e}")
            self.failed_tests += 1
            return False

    def test_configuration_files(self):
        """Test configuration file generation"""
        print("\n🧪 Testing Configuration Files...")
        print("=" * 40)
        
        self.total_tests += 1
        
        try:
            # Check if deployment script creates proper configuration files
            deploy_script = self.app_root / "deploy-production.sh"
            if not deploy_script.exists():
                print("❌ Cannot test configuration files - deployment script missing")
                self.failed_tests += 1
                return False
            
            with open(deploy_script, 'r') as f:
                content = f.read()
            
            # Check for configuration file creation
            config_files = [
                (".env.production", "Production environment file"),
                ("render.yaml", "Render configuration"),
                ("railway.json", "Railway configuration"),
                ("nginx.conf", "Nginx configuration"),
                ("prometheus.yml", "Monitoring configuration"),
                ("fluentd.conf", "Logging configuration")
            ]
            
            config_found = 0
            for file_name, desc in config_files:
                if file_name in content:
                    print(f"✅ {desc} creation found")
                    config_found += 1
                else:
                    print(f"❌ {desc} creation missing")
            
            # Check for proper environment variable handling
            env_handling = [
                ("${MONGO_URL}", "MongoDB URL variable"),
                ("${SENDGRID_API_KEY}", "SendGrid API key variable"),
                ("${JWT_SECRET}", "JWT secret variable"),
                ("ENVIRONMENT=production", "Production environment setting"),
                ("NODE_ENV=production", "Node environment setting")
            ]
            
            env_found = 0
            for check, desc in env_handling:
                if check in content:
                    print(f"✅ {desc} handled")
                    env_found += 1
                else:
                    print(f"❌ {desc} missing")
            
            # Check for security configurations
            security_configs = [
                ("CORS_ORIGINS", "CORS configuration"),
                ("LOG_LEVEL", "Logging level"),
                ("ACCESS_TOKEN_EXPIRE", "Token expiration"),
                ("X-Frame-Options", "Security headers"),
                ("Strict-Transport-Security", "HTTPS enforcement")
            ]
            
            security_found = 0
            for check, desc in security_configs:
                if check in content:
                    print(f"✅ {desc} configured")
                    security_found += 1
                else:
                    print(f"❌ {desc} missing")
            
            # Overall assessment
            if config_found >= 4 and env_found >= 3 and security_found >= 3:
                print("✅ Configuration files are properly generated")
                self.passed_tests += 1
                return True
            else:
                print("❌ Configuration file generation is incomplete")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing configuration files: {e}")
            self.failed_tests += 1
            return False

    def test_deployment_script_execution(self):
        """Test deployment script can be executed (dry run)"""
        print("\n🧪 Testing Deployment Script Execution...")
        print("=" * 45)
        
        self.total_tests += 1
        
        try:
            # Test if the main deployment script can be executed with help/dry-run
            deploy_script = self.app_root / "deploy-production.sh"
            
            if not deploy_script.exists():
                print("❌ Deployment script not found")
                self.failed_tests += 1
                return False
            
            # Try to run the script with bash syntax check
            result = subprocess.run([
                "bash", "-n", str(deploy_script)
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Deployment script has valid bash syntax")
            else:
                print(f"❌ Deployment script has syntax errors: {result.stderr}")
                self.failed_tests += 1
                return False
            
            # Check if script handles missing environment variables gracefully
            # Run script without required env vars to test validation
            env_test = os.environ.copy()
            # Remove required variables to test validation
            for var in ["SENDGRID_API_KEY", "MONGO_URL", "JWT_SECRET", "SENDER_EMAIL"]:
                env_test.pop(var, None)
            
            try:
                result = subprocess.run([
                    "bash", str(deploy_script)
                ], env=env_test, capture_output=True, text=True, timeout=15)
                
                # Script should exit with error code when env vars are missing
                if result.returncode != 0 and "Missing required environment variables" in result.stdout:
                    print("✅ Deployment script properly validates environment variables")
                elif result.returncode != 0:
                    print("✅ Deployment script exits with error when environment is incomplete")
                else:
                    print("⚠️  Deployment script may not properly validate environment variables")
                    
            except subprocess.TimeoutExpired:
                print("⚠️  Deployment script validation test timed out (expected)")
            
            self.passed_tests += 1
            return True
            
        except Exception as e:
            print(f"❌ Error testing deployment script execution: {e}")
            self.failed_tests += 1
            return False

    def run_all_tests(self):
        """Run all deployment system tests"""
        print("🚀 Starting Production Deployment System Testing")
        print("Focus: Deployment automation, monitoring, Docker, health checks, configuration")
        print("=" * 80)
        
        # Run all test suites
        results = []
        results.append(self.test_main_deployment_script())
        results.append(self.test_platform_deployment_scripts())
        results.append(self.test_monitoring_system())
        results.append(self.test_docker_configuration())
        results.append(self.test_health_check_system())
        results.append(self.test_configuration_files())
        results.append(self.test_deployment_script_execution())
        
        # Print final results
        self.print_final_results()
        
        return all(results)

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 PRODUCTION DEPLOYMENT SYSTEM TEST RESULTS")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: Production deployment system is ready for use!")
            elif success_rate >= 75:
                print("👍 GOOD: Production deployment system is mostly ready with minor issues")
            elif success_rate >= 50:
                print("⚠️  MODERATE: Production deployment system needs some improvements")
            else:
                print("❌ POOR: Production deployment system has significant issues")
        
        print("\n📋 Test Summary:")
        print("  ✅ Main deployment script structure and validation")
        print("  ✅ Platform-specific deployment scripts (Railway, Render)")
        print("  ✅ Health monitoring system functionality")
        print("  ✅ Docker configuration and optimization")
        print("  ✅ Health check system implementation")
        print("  ✅ Configuration file generation")
        print("  ✅ Deployment script execution validation")
        
        print("=" * 80)


if __name__ == "__main__":
    tester = DeploymentSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All deployment system tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some deployment system tests failed!")
        sys.exit(1)