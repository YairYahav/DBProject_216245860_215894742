"""
Streaming Service Management System - Main Application
מערכת ניהול שירותי סטרימינג - אפליקציה ראשית

Author: DB5785 Team
Description: ממשק גרפי מקיף לניהול מערכת סטרימינג עם PostgreSQL
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import psycopg2
from psycopg2 import sql
import os
import sys
from datetime import datetime, date
import traceback

# Import custom modules
from database_connection import DatabaseManager
from login_screen import LoginScreen
from dashboard import Dashboard
from customer_management import CustomerManagement
from profile_management import ProfileManagement
from watchhistory_management import WatchHistoryManagement
from queries_reports import QueriesReports
from functions_procedures import FunctionsProcedures

class StreamingServiceApp:
    """
    Main application class for Streaming Service Management System
    """
    
    def __init__(self):
        """Initialize the main application"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window initially
        
        # Application settings
        self.app_title = "Streaming Service Management System"
        self.version = "1.0.0"
        self.current_user = None
        self.db_manager = None
        
        # Color scheme
        self.colors = {
            'primary': '#2C3E50',      # Dark blue-gray
            'secondary': '#3498DB',    # Blue
            'accent': '#E74C3C',       # Red
            'success': '#27AE60',      # Green
            'warning': '#F39C12',      # Orange
            'light': '#ECF0F1',        # Light gray
            'dark': '#34495E',         # Dark gray
            'white': '#FFFFFF',
            'text': '#2C3E50'
        }
        
        self.setup_application()
        
    def setup_application(self):
        """Setup application configuration and styling"""
        # Configure main window
        self.root.title(self.app_title)
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        self.root.configure(bg=self.colors['light'])
        
        # Set application icon (if available)
        try:
            self.root.iconbitmap('assets/app_icon.ico')
        except:
            pass  # Icon file not found, continue without it
        
        # Configure styles
        self.setup_styles()
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Show login screen
        self.show_login()
        
    def setup_styles(self):
        """Setup custom styles for ttk widgets"""
        style = ttk.Style()
        
        # Configure custom styles
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'),
                       background=self.colors['light'],
                       foreground=self.colors['primary'])
        
        style.configure('Heading.TLabel',
                       font=('Arial', 12, 'bold'),
                       background=self.colors['light'],
                       foreground=self.colors['dark'])
        
        style.configure('Primary.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=(20, 10))
        
        style.configure('Secondary.TButton',
                       font=('Arial', 9),
                       padding=(15, 5))
        
        style.configure('Accent.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=(15, 8))
        
        # Configure Treeview
        style.configure('Custom.Treeview',
                       background=self.colors['white'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['white'],
                       font=('Arial', 9))
        
        style.configure('Custom.Treeview.Heading',
                       font=('Arial', 10, 'bold'),
                       background=self.colors['primary'],
                       foreground=self.colors['white'])
        
    def show_login(self):
        """Display login screen"""
        try:
            self.login_window = LoginScreen(self, self.db_manager, self.colors)
            self.login_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show login screen: {str(e)}")
            self.root.quit()
    
    def on_login_success(self, user_info):
        """Handle successful login"""
        self.current_user = user_info
        self.login_window.destroy()
        self.show_main_application()
    
    def show_main_application(self):
        """Show main application window"""
        try:
            # Show main window
            self.root.deiconify()
            
            # Create main application interface
            self.create_main_interface()
            
            # Show dashboard by default
            self.show_dashboard()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize main application: {str(e)}")
            self.root.quit()
    
    def create_main_interface(self):
        """Create the main application interface"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        self.create_header()
        
        # Create navigation
        self.create_navigation()
        
        # Create content area
        self.create_content_area()
        
        # Create status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create application header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text=self.app_title,
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # User info
        if self.current_user:
            user_frame = ttk.Frame(header_frame)
            user_frame.pack(side=tk.RIGHT)
            
            user_label = ttk.Label(user_frame,
                                  text=f"Welcome, {self.current_user.get('username', 'User')}",
                                  font=('Arial', 10))
            user_label.pack(side=tk.RIGHT, padx=(0, 10))
            
            logout_btn = ttk.Button(user_frame,
                                   text="Logout",
                                   command=self.logout,
                                   style='Secondary.TButton')
            logout_btn.pack(side=tk.RIGHT)
        
        # Separator
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 10))
    
    def create_navigation(self):
        """Create navigation menu"""
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons
        self.nav_buttons = {}
        
        buttons_config = [
            ("Dashboard", "🏠", self.show_dashboard),
            ("Customers", "👥", self.show_customers),
            ("Profiles", "👤", self.show_profiles),
            ("Watch History", "📺", self.show_watch_history),
            ("Queries & Reports", "📊", self.show_queries),
            ("Functions & Procedures", "⚙️", self.show_functions)
        ]
        
        for text, icon, command in buttons_config:
            btn = ttk.Button(nav_frame,
                           text=f"{icon} {text}",
                           command=command,
                           style='Primary.TButton')
            btn.pack(side=tk.LEFT, padx=(0, 5))
            self.nav_buttons[text] = btn
    
    def create_content_area(self):
        """Create main content area"""
        self.content_frame = ttk.Frame(self.main_frame, relief=tk.RAISED, borderwidth=1)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure content frame
        self.content_frame.configure(padding=(10, 10, 10, 10))
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_bar.pack(fill=tk.X)
        
        # Status label
        self.status_label = ttk.Label(self.status_bar,
                                     text="Ready",
                                     font=('Arial', 9),
                                     relief=tk.SUNKEN,
                                     anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Connection status
        self.connection_label = ttk.Label(self.status_bar,
                                         text="Connected to Database",
                                         font=('Arial', 9),
                                         relief=tk.SUNKEN,
                                         background=self.colors['success'],
                                         foreground=self.colors['white'])
        self.connection_label.pack(side=tk.RIGHT)
    
    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        self.root.update_idletasks()
    
    def show_dashboard(self):
        """Show dashboard screen"""
        self.clear_content()
        self.update_status("Loading Dashboard...")
        
        try:
            dashboard = Dashboard(self.content_frame, self.db_manager, self.colors)
            dashboard.create_dashboard()
            self.update_status("Dashboard loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard: {str(e)}")
            self.update_status("Error loading dashboard")
    
    def show_customers(self):
        """Show customer management screen"""
        self.clear_content()
        self.update_status("Loading Customer Management...")
        
        try:
            customer_mgmt = CustomerManagement(self.content_frame, self.db_manager, self.colors)
            customer_mgmt.create_interface()
            self.update_status("Customer Management loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer management: {str(e)}")
            self.update_status("Error loading customer management")
    
    def show_profiles(self):
        """Show profile management screen"""
        self.clear_content()
        self.update_status("Loading Profile Management...")
        
        try:
            profile_mgmt = ProfileManagement(self.content_frame, self.db_manager, self.colors)
            profile_mgmt.create_interface()
            self.update_status("Profile Management loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profile management: {str(e)}")
            self.update_status("Error loading profile management")
    
    def show_watch_history(self):
        """Show watch history management screen"""
        self.clear_content()
        self.update_status("Loading Watch History Management...")
        
        try:
            watch_mgmt = WatchHistoryManagement(self.content_frame, self.db_manager, self.colors)
            watch_mgmt.create_interface()
            self.update_status("Watch History Management loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load watch history management: {str(e)}")
            self.update_status("Error loading watch history management")
    
    def show_queries(self):
        """Show queries and reports screen"""
        self.clear_content()
        self.update_status("Loading Queries & Reports...")
        
        try:
            queries_reports = QueriesReports(self.content_frame, self.db_manager, self.colors)
            queries_reports.create_interface()
            self.update_status("Queries & Reports loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load queries & reports: {str(e)}")
            self.update_status("Error loading queries & reports")
    
    def show_functions(self):
        """Show functions and procedures screen"""
        self.clear_content()
        self.update_status("Loading Functions & Procedures...")
        
        try:
            functions_procs = FunctionsProcedures(self.content_frame, self.db_manager, self.colors)
            functions_procs.create_interface()
            self.update_status("Functions & Procedures loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load functions & procedures: {str(e)}")
            self.update_status("Error loading functions & procedures")
    
    def logout(self):
        """Handle user logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            try:
                # Close database connection
                if self.db_manager:
                    self.db_manager.close_connection()
                
                # Reset user info
                self.current_user = None
                
                # Hide main window
                self.root.withdraw()
                
                # Show login screen again
                self.show_login()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error during logout: {str(e)}")
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            try:
                # Close database connection
                if self.db_manager:
                    self.db_manager.close_connection()
                
                # Destroy application
                self.root.destroy()
                
            except Exception as e:
                print(f"Error during application shutdown: {str(e)}")
                self.root.destroy()
    
    def run(self):
        """Run the application"""
        try:
            # Set up closing protocol
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Start main loop
            self.root.mainloop()
            
        except Exception as e:
            print(f"Critical error in application: {str(e)}")
            traceback.print_exc()

def main():
    """Main function to start the application"""
    try:
        # Create and run application
        app = StreamingServiceApp()
        app.run()
        
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
        traceback.print_exc()
        
        # Show error message if possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Critical Error", 
                               f"Failed to start application:\n{str(e)}\n\nPlease check the console for details.")
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    main()
  
