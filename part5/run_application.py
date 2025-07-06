#!/usr/bin/env python3
"""
Streaming Service Management System - Application Launcher
מערכת ניהול שירותי סטרימינג - מפעיל האפליקציה

This script launches the streaming service management application.
Run this file to start the system.

Usage:
    python run_application.py

Requirements:
    - Python 3.8 or higher
    - PostgreSQL database
    - Required packages (see requirements.txt)

Author: DB5785 Team
"""

import sys
import os
import subprocess
import importlib.util

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_required_packages():
    """Check if required packages are installed"""
    required_packages = [
        ('psycopg2', 'PostgreSQL adapter'),
        ('tkinter', 'GUI framework'),
        ('tkcalendar', 'Date picker widget'),
        ('pandas', 'Data manipulation'),
        ('matplotlib', 'Charts and visualization'),
        ('numpy', 'Numerical operations')
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                importlib.import_module(package)
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"❌ {package}: {description} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("   Please install missing packages using:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def create_config_directories():
    """Create necessary configuration directories"""
    directories = [
        'config',
        'logs',
        'assets',
        'assets/profile_pictures',
        'exports'
    ]
    
    for directory in directories:
        dir_path = os.path.join(current_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"📁 Created directory: {directory}")
    
    print("✅ Configuration directories ready")

def check_database_files():
    """Check if database configuration files exist"""
    required_files = [
        'database_connection.py',
        'main_app.py',
        'login_screen.py'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(current_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required application files found")
    return True

def install_requirements():
    """Install requirements if missing packages are detected"""
    requirements_file = os.path.join(current_dir, 'requirements.txt')
    
    if os.path.exists(requirements_file):
        print("📦 Installing required packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
            print("✅ Packages installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            return False
    else:
        print("⚠️  requirements.txt not found")
        return False

def display_system_info():
    """Display system information and requirements"""
    print("="*60)
    print("🎬 STREAMING SERVICE MANAGEMENT SYSTEM 🎬")
    print("מערכת ניהול שירותי סטרימינג")
    print("="*60)
    print("Version: 1.0.0")
    print("Author: DB5785 Team")
    print("Database: PostgreSQL")
    print("Framework: Python + Tkinter")
    print("="*60)

def display_database_setup_info():
    """Display database setup information"""
    print("\n📋 DATABASE SETUP REQUIREMENTS:")
    print("-" * 40)
    print("1. PostgreSQL server must be running")
    print("2. Database 'streaming_service' should exist")
    print("3. User should have appropriate permissions")
    print("4. Tables should be created using the provided SQL files")
    print("\nDefault connection settings:")
    print("  Host: localhost")
    print("  Port: 5432")
    print("  Database: streaming_service")
    print("  User: postgres")
    print("  Password: (will be prompted)")
    print("-" * 40)

def launch_application():
    """Launch the main application"""
    try:
        print("\n🚀 Launching Streaming Service Management System...")
        
        # Import and run the main application
        from main_app import main
        main()
        
    except ImportError as e:
        print(f"❌ Failed to import main application: {e}")
        print("   Please ensure all application files are present")
        return False
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

def main():
    """Main function to run all checks and launch application"""
    display_system_info()
    
    print("\n🔍 SYSTEM CHECK:")
    print("-" * 20)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create necessary directories
    create_config_directories()
    
    # Check required files
    if not check_database_files():
        print("\n❌ Missing required files. Please ensure all application files are present.")
        sys.exit(1)
    
    # Check required packages
    if not check_required_packages():
        print("\n📦 Attempting to install missing packages...")
        if not install_requirements():
            print("\n❌ Failed to install required packages.")
            print("   Please manually install packages using: pip install -r requirements.txt")
            sys.exit(1)
        
        # Re-check packages after installation
        if not check_required_packages():
            print("\n❌ Package installation failed. Please install manually.")
            sys.exit(1)
    
    # Display database setup info
    display_database_setup_info()
    
    # Launch application
    print("\n" + "="*60)
    if launch_application():
        print("✅ Application started successfully")
    else:
        print("❌ Failed to start application")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Application startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        sys.exit(1)
      
