"""
Login Screen for Streaming Service Management System
מסך כניסה למערכת ניהול שירותי סטרימינג

Handles user authentication and database connection setup
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class LoginScreen:
    """
    Login screen class for database authentication
    """
    
    def __init__(self, main_app, db_manager, colors):
        """
        Initialize login screen
        
        Args:
            main_app: Main application instance
            db_manager: Database manager instance
            colors: Color scheme dictionary
        """
        self.main_app = main_app
        self.db_manager = db_manager
        self.colors = colors
        
        self.login_window = None
        self.connection_saved = False
        
        # Default connection parameters
        self.default_connections = {
            "Local PostgreSQL": {
                "host": "localhost",
                "port": "5432",
                "database": "streaming_service",
                "user": "postgres"
            },
            "Custom Connection": {
                "host": "",
                "port": "5432",
                "database": "",
                "user": ""
            }
        }
        
        self.load_saved_connections()
    
    def load_saved_connections(self):
        """Load saved connection parameters from file"""
        try:
            if os.path.exists('config/connections.json'):
                with open('config/connections.json', 'r') as f:
                    saved_connections = json.load(f)
                    self.default_connections.update(saved_connections)
        except Exception as e:
            print(f"Could not load saved connections: {str(e)}")
    
    def save_connection(self, name, params):
        """Save connection parameters to file"""
        try:
            # Create config directory if not exists
            os.makedirs('config', exist_ok=True)
            
            # Load existing connections
            connections = {}
            if os.path.exists('config/connections.json'):
                with open('config/connections.json', 'r') as f:
                    connections = json.load(f)
            
            # Add new connection
            connections[name] = {
                "host": params['host'],
                "port": params['port'],
                "database": params['database'],
                "user": params['user']
            }
            
            # Save to file
            with open('config/connections.json', 'w') as f:
                json.dump(connections, f, indent=2)
                
            self.connection_saved = True
            
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not save connection: {str(e)}")
    
    def show(self):
        """Display login window"""
        self.create_login_window()
        self.create_login_interface()
        
        # Center window on screen
        self.center_window()
        
        # Focus on window
        self.login_window.focus_set()
        self.login_window.grab_set()
    
    def create_login_window(self):
        """Create login window"""
        self.login_window = tk.Toplevel()
        self.login_window.title("Login - Streaming Service Management")
        self.login_window.geometry("500x600")
        self.login_window.resizable(False, False)
        self.login_window.configure(bg=self.colors['light'])
        
        # Set window icon
        try:
            self.login_window.iconbitmap('assets/app_icon.ico')
        except:
            pass
        
        # Handle window close
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def center_window(self):
        """Center login window on screen"""
        self.login_window.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        
        # Get window dimensions
        window_width = self.login_window.winfo_width()
        window_height = self.login_window.winfo_height()
        
        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.login_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def create_login_interface(self):
        """Create login interface elements"""
        # Main container
        main_frame = ttk.Frame(self.login_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Connection selection
        self.create_connection_selection(main_frame)
        
        # Connection parameters
        self.create_connection_params(main_frame)
        
        # Test connection button
        self.create_test_section(main_frame)
        
        # Login buttons
        self.create_button_section(main_frame)
        
        # Status section
        self.create_status_section(main_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo/Icon placeholder
        logo_frame = ttk.Frame(header_frame)
        logo_frame.pack(pady=(0, 10))
        
        # App icon (placeholder)
        icon_label = ttk.Label(logo_frame, text="🎬", font=('Arial', 48))
        icon_label.pack()
        
        # Title
        title_label = ttk.Label(header_frame,
                               text="Streaming Service Management",
                               font=('Arial', 16, 'bold'),
                               foreground=self.colors['primary'])
        title_label.pack()
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame,
                                  text="Database Connection Setup",
                                  font=('Arial', 10),
                                  foreground=self.colors['dark'])
        subtitle_label.pack()
        
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 20))
    
    def create_connection_selection(self, parent):
        """Create connection selection section"""
        selection_frame = ttk.LabelFrame(parent, text="Connection Profile", padding="10")
        selection_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Connection selection
        self.connection_var = tk.StringVar(value="Local PostgreSQL")
        
        for name in self.default_connections.keys():
            radio = ttk.Radiobutton(selection_frame,
                                   text=name,
                                   variable=self.connection_var,
                                   value=name,
                                   command=self.on_connection_change)
            radio.pack(anchor=tk.W, pady=2)
    
    def create_connection_params(self, parent):
        """Create connection parameters section"""
        params_frame = ttk.LabelFrame(parent, text="Connection Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create entry fields
        self.entries = {}
        
        fields = [
            ("Host:", "host"),
            ("Port:", "port"),
            ("Database:", "database"),
            ("Username:", "user"),
            ("Password:", "password")
        ]
        
        for i, (label_text, field_name) in enumerate(fields):
            # Label
            label = ttk.Label(params_frame, text=label_text)
            label.grid(row=i, column=0, sticky=tk.W, padx=(0, 10), pady=5)
            
            # Entry
            if field_name == "password":
                entry = ttk.Entry(params_frame, show="*", width=30)
            else:
                entry = ttk.Entry(params_frame, width=30)
            
            entry.grid(row=i, column=1, sticky=tk.W, pady=5)
            self.entries[field_name] = entry
        
        # Configure grid weights
        params_frame.columnconfigure(1, weight=1)
        
        # Load default values
        self.on_connection_change()
    
    def create_test_section(self, parent):
        """Create test connection section"""
        test_frame = ttk.Frame(parent)
        test_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Test button
        self.test_btn = ttk.Button(test_frame,
                                  text="🔍 Test Connection",
                                  command=self.test_connection,
                                  style='Secondary.TButton')
        self.test_btn.pack(side=tk.LEFT)
        
        # Save connection checkbox
        self.save_connection_var = tk.BooleanVar()
        save_check = ttk.Checkbutton(test_frame,
                                    text="Save this connection",
                                    variable=self.save_connection_var)
        save_check.pack(side=tk.RIGHT)
    
    def create_button_section(self, parent):
        """Create login buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Login button
        self.login_btn = ttk.Button(button_frame,
                                   text="🔐 Connect & Login",
                                   command=self.on_login,
                                   style='Primary.TButton')
        self.login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_btn = ttk.Button(button_frame,
                               text="❌ Cancel",
                               command=self.on_cancel,
                               style='Secondary.TButton')
        cancel_btn.pack(side=tk.LEFT)
        
        # About button
        about_btn = ttk.Button(button_frame,
                              text="ℹ️ About",
                              command=self.show_about,
                              style='Secondary.TButton')
        about_btn.pack(side=tk.RIGHT)
    
    def create_status_section(self, parent):
        """Create status section"""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status text
        self.status_text = tk.Text(status_frame,
                                  height=8,
                                  width=60,
                                  state=tk.DISABLED,
                                  wrap=tk.WORD,
                                  font=('Consolas', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Add initial message
        self.add_status_message("Ready to connect. Please configure your database settings above.")
    
    def on_connection_change(self):
        """Handle connection profile change"""
        selected_connection = self.connection_var.get()
        
        if selected_connection in self.default_connections:
            params = self.default_connections[selected_connection]
            
            # Update entry fields
            for field_name, entry in self.entries.items():
                if field_name in params:
                    entry.delete(0, tk.END)
                    entry.insert(0, params[field_name])
                elif field_name == "password":
                    entry.delete(0, tk.END)
    
    def get_connection_params(self):
        """Get connection parameters from form"""
        return {
            'host': self.entries['host'].get().strip(),
            'port': self.entries['port'].get().strip(),
            'database': self.entries['database'].get().strip(),
            'user': self.entries['user'].get().strip(),
            'password': self.entries['password'].get()
        }
    
    def add_status_message(self, message, message_type="info"):
        """Add message to status text"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format message based on type
        if message_type == "error":
            prefix = "❌ ERROR"
        elif message_type == "success":
            prefix = "✅ SUCCESS"
        elif message_type == "warning":
            prefix = "⚠️ WARNING"
        else:
            prefix = "ℹ️ INFO"
        
        formatted_message = f"[{timestamp}] {prefix}: {message}\n"
        
        # Add to text widget
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def test_connection(self):
        """Test database connection"""
        self.add_status_message("Testing database connection...")
        
        # Disable test button during test
        self.test_btn.config(state=tk.DISABLED)
        
        try:
            # Get connection parameters
            params = self.get_connection_params()
            
            # Validate parameters
            if not all([params['host'], params['port'], params['database'], params['user']]):
                self.add_status_message("Please fill in all required fields", "error")
                return
            
            # Test connection
            if self.db_manager.connect(**params):
                # Test with simple query
                test_result = self.db_manager.test_connection()
                
                if test_result['status'] == 'success':
                    self.add_status_message(
                        f"Connection successful! Connected to database '{test_result['database']}' "
                        f"as user '{test_result['user']}'", 
                        "success"
                    )
                    
                    # Enable login button
                    self.login_btn.config(state=tk.NORMAL)
                else:
                    self.add_status_message(f"Connection test failed: {test_result['error']}", "error")
            else:
                self.add_status_message("Failed to establish database connection", "error")
                
        except Exception as e:
            self.add_status_message(f"Connection error: {str(e)}", "error")
            
        finally:
            # Re-enable test button
            self.test_btn.config(state=tk.NORMAL)
    
    def on_login(self):
        """Handle login button click"""
        try:
            # Get connection parameters
            params = self.get_connection_params()
            
            # Validate parameters
            if not all([params['host'], params['port'], params['database'], params['user']]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            self.add_status_message("Connecting to database...")
            
            # Connect to database
            if self.db_manager.connect(**params):
                # Test connection
                test_result = self.db_manager.test_connection()
                
                if test_result['status'] == 'success':
                    self.add_status_message("Login successful! Loading application...", "success")
                    
                    # Save connection if requested
                    if self.save_connection_var.get():
                        connection_name = f"Connection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        self.save_connection(connection_name, params)
                    
                    # Create user info
                    user_info = {
                        'username': params['user'],
                        'database': params['database'],
                        'host': params['host'],
                        'login_time': datetime.now()
                    }
                    
                    # Notify main app of successful login
                    self.main_app.on_login_success(user_info)
                    
                else:
                    messagebox.showerror("Login Failed", f"Database test failed: {test_result['error']}")
            else:
                messagebox.showerror("Login Failed", "Could not connect to database")
                
        except Exception as e:
            messagebox.showerror("Login Error", f"Login failed: {str(e)}")
            self.add_status_message(f"Login failed: {str(e)}", "error")
    
    def on_cancel(self):
        """Handle cancel button click"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.login_window.destroy()
            self.main_app.root.quit()
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Streaming Service Management System
Version 1.0.0

A comprehensive database management application for streaming services.

Features:
• Customer Management
• Profile Management  
• Watch History Tracking
• Advanced Queries & Reports
• Stored Functions & Procedures

Developed by: DB5785 Team
Database: PostgreSQL
Framework: Python + Tkinter

© 2024 All rights reserved
        """
        
        messagebox.showinfo("About", about_text.strip())
    
    def destroy(self):
        """Destroy login window"""
        if self.login_window:
            self.login_window.destroy()
          
