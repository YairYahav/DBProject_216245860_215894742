import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, date
import random

class StreamingServiceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Streaming Service Management System")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Database connection
        self.connection = None
        self.cursor = None
        
        # Start with login screen
        self.show_login_screen()
    
    def clear_screen(self):
        """Clear all widgets from the screen"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """מסך כניסה למערכת עם חיבור PostgreSQL"""
        self.clear_screen()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=50, pady=50)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Streaming Service Management System", 
                              font=('Arial', 24, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=(0, 40))
        
        # Login form frame
        login_frame = tk.Frame(main_frame, bg='white', padx=40, pady=40, relief='raised', bd=3)
        login_frame.pack()
        
        tk.Label(login_frame, text="PostgreSQL Database Connection", font=('Arial', 18, 'bold')).pack(pady=(0, 30))
        
        # Create fields frame for organized layout
        fields_frame = tk.Frame(login_frame, bg='white')
        fields_frame.pack()
        
        # Host
        tk.Label(fields_frame, text="Host:", font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=10, pady=8, sticky='e')
        self.host_entry = tk.Entry(fields_frame, font=('Arial', 12), width=25)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, padx=10, pady=8)
        
        # Port
        tk.Label(fields_frame, text="Port:", font=('Arial', 12, 'bold')).grid(row=1, column=0, padx=10, pady=8, sticky='e')
        self.port_entry = tk.Entry(fields_frame, font=('Arial', 12), width=25)
        self.port_entry.insert(0, "5432")
        self.port_entry.grid(row=1, column=1, padx=10, pady=8)
        
        # Database Name
        tk.Label(fields_frame, text="Database Name:", font=('Arial', 12, 'bold')).grid(row=2, column=0, padx=10, pady=8, sticky='e')
        self.database_entry = tk.Entry(fields_frame, font=('Arial', 12), width=25)
        self.database_entry.insert(0, "streaming_service")
        self.database_entry.grid(row=2, column=1, padx=10, pady=8)
        
        # Username
        tk.Label(fields_frame, text="Username:", font=('Arial', 12, 'bold')).grid(row=3, column=0, padx=10, pady=8, sticky='e')
        self.username_entry = tk.Entry(fields_frame, font=('Arial', 12), width=25)
        self.username_entry.insert(0, "postgres")
        self.username_entry.grid(row=3, column=1, padx=10, pady=8)
        
        # Password
        tk.Label(fields_frame, text="Password:", font=('Arial', 12, 'bold')).grid(row=4, column=0, padx=10, pady=8, sticky='e')
        self.password_entry = tk.Entry(fields_frame, font=('Arial', 12), width=25, show='*')
        self.password_entry.grid(row=4, column=1, padx=10, pady=8)
        
        # Connect button
        connect_btn = tk.Button(login_frame, text="Connect to PostgreSQL Database", 
                               command=self.connect_database,
                               bg='#3498db', fg='white', font=('Arial', 14, 'bold'),
                               padx=30, pady=15, cursor='hand2')
        connect_btn.pack(pady=30)
        
        # Status label
        self.status_label = tk.Label(login_frame, text="Enter PostgreSQL credentials and click Connect", 
                                    fg='#7f8c8d', bg='white', font=('Arial', 10))
        self.status_label.pack()
    
    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=self.host_entry.get(),
                port=self.port_entry.get(),
                database=self.database_entry.get(),
                user=self.username_entry.get(),
                password=self.password_entry.get()
            )
            self.cursor = self.connection.cursor(cursor_factory=DictCursor)
            
            # Test connection
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()[0]
            
            messagebox.showinfo("Success", f"Connected successfully to PostgreSQL!\n\nVersion: {version[:60]}...")
            self.show_main_menu()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to PostgreSQL database:\n\n{str(e)}")
            self.status_label.config(text="Connection failed. Please check credentials.", fg='red')
    
    def show_main_menu(self):
        """תפריט ראשי"""
        self.clear_screen()
        
        # Header
        header_frame = tk.Frame(self.root, bg='#34495e', height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Streaming Service Management System", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#34495e')
        title_label.pack(expand=True)
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#ecf0f1', padx=50, pady=50)
        content_frame.pack(fill='both', expand=True)
        
        # Menu buttons
        menu_options = [
            ("👥 Customer Management", self.show_customer_management, '#3498db'),
            ("📱 Profile Management", self.show_profile_management, '#e67e22'),
            ("⭐ Favorites Management", self.show_favorites_management, '#9b59b6'),
            ("📊 Reports & Queries", self.show_reports_screen, '#27ae60'),
            ("🔧 Functions & Procedures", self.show_functions_screen, '#e74c3c'),
            ("🚪 Disconnect", self.show_login_screen, '#95a5a6')
        ]
        
        # Create buttons in grid
        for i, (text, command, color) in enumerate(menu_options):
            row = i // 2
            col = i % 2
            
            btn = tk.Button(content_frame, text=text, command=command,
                           bg=color, fg='white', font=('Arial', 14, 'bold'),
                           width=30, height=3, cursor='hand2')
            btn.grid(row=row, column=col, padx=30, pady=20)
    
    def create_header(self, title):
        """Create header for screens"""
        header_frame = tk.Frame(self.root, bg='#34495e', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text=title, 
                              font=('Arial', 18, 'bold'), fg='white', bg='#34495e')
        title_label.pack(expand=True)
    
    def show_customer_management(self):
        """ניהול לקוחות - CRUD"""
        self.clear_screen()
        self.create_header("Customer Management")
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#ecf0f1', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Buttons frame
        buttons_frame = tk.Frame(content_frame, bg='#ecf0f1')
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        # CRUD buttons
        tk.Button(buttons_frame, text="➕ Add Customer", command=self.add_customer,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="✏ Edit Customer", command=self.edit_customer,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="🗑 Delete Customer", command=self.delete_customer,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="🔄 Refresh", command=self.refresh_customers,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="⬅ Back", command=self.show_main_menu,
                 bg='#95a5a6', fg='white', font=('Arial', 10, 'bold')).pack(side='right', padx=5)
        
        # Treeview for customers
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical')
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        
        # Treeview
        self.customer_tree = ttk.Treeview(tree_frame, 
                                         columns=('CustomerID', 'FirstName', 'LastName', 'DateOfBirth', 'CustomerSince'),
                                         show='headings',
                                         yscrollcommand=v_scrollbar.set,
                                         xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.customer_tree.yview)
        h_scrollbar.config(command=self.customer_tree.xview)
        
        # Define headings
        headings = ['Customer ID', 'First Name', 'Last Name', 'Date of Birth', 'Customer Since']
        for i, heading in enumerate(headings):
            self.customer_tree.heading(f'#{i+1}', text=heading)
            self.customer_tree.column(f'#{i+1}', width=150)
        
        # Pack components
        self.customer_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Load data
        self.refresh_customers()
        
        # Bind selection event
        self.customer_tree.bind('<<TreeviewSelect>>', self.on_customer_select)
    
    def refresh_customers(self):
        """Load customers"""
        try:
            # Clear existing data
            for item in self.customer_tree.get_children():
                self.customer_tree.delete(item)
            
            # Show loading message
            self.root.config(cursor="wait")
            self.root.update()
            
            # Fetch customers
            self.cursor.execute("SELECT customerID, firstName, lastName, dateOfBirth, customerSince FROM Customer ORDER BY customerID")
            customers = self.cursor.fetchall()
            
            # Insert into treeview
            for customer in customers:
                self.customer_tree.insert('', 'end', values=customer)
            
            # Reset cursor
            self.root.config(cursor="")
            
            # Clear any previous selection
            if hasattr(self, 'selected_customer'):
                delattr(self, 'selected_customer')
                
            # Show success message with count
            if customers:
                status_msg = f"✅ Successfully loaded {len(customers)} customer{'s' if len(customers) != 1 else ''}"
                messagebox.showinfo("Data Loaded", status_msg)
            else:
                messagebox.showinfo("No Data", "No customers found in the database.\n\nClick 'Add Customer' to create the first customer.")
            
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Database Error", f"Failed to load customers:\n\n{str(e)}\n\nPlease check your database connection.")
    
    def on_customer_select(self, event):
        """Handle customer selection"""
        selection = self.customer_tree.selection()
        if selection:
            item = self.customer_tree.item(selection[0])
            self.selected_customer = item['values']
    
    def add_customer(self):
        """Add new customer"""
        dialog = CustomerDialog(self.root, "Add Customer")
        if dialog.result:
            try:
                self.cursor.execute("""
                    INSERT INTO Customer (customerID, firstName, lastName, dateOfBirth, customerSince)
                    VALUES (%s, %s, %s, %s, %s)
                """, dialog.result)
                
                self.connection.commit()
                messagebox.showinfo("Success", "Customer added successfully!")
                self.refresh_customers()
                
            except Exception as e:
                self.connection.rollback()
                messagebox.showerror("Error", f"Failed to add customer: {str(e)}")
    
    def edit_customer(self):
        """Edit selected customer"""
        if not hasattr(self, 'selected_customer') or not self.selected_customer:
            messagebox.showwarning("Selection Required", 
                                 "Please select a customer from the table first.\n\nClick on a row in the table to select it, then click Edit.")
            return
        
        dialog = CustomerDialog(self.root, "Edit Customer", self.selected_customer)
        if dialog.result:
            try:
                self.cursor.execute("""
                    UPDATE Customer 
                    SET firstName = %s, lastName = %s, dateOfBirth = %s, customerSince = %s
                    WHERE customerID = %s
                """, dialog.result[1:] + [self.selected_customer[0]])
                
                self.connection.commit()
                messagebox.showinfo("Success", 
                                  f"Customer '{dialog.result[1]} {dialog.result[2]}' updated successfully!")
                self.refresh_customers()
                
            except Exception as e:
                self.connection.rollback()
                messagebox.showerror("Database Error", 
                                   f"Failed to update customer:\n\n{str(e)}\n\nThe operation has been cancelled.")
    
    def delete_customer(self):
        """Delete selected customer"""
        if not hasattr(self, 'selected_customer') or not self.selected_customer:
            messagebox.showwarning("Selection Required", 
                                 "Please select a customer from the table first.\n\nClick on a row in the table to select it, then click Delete.")
            return
        
        # Show detailed warning
        customer_name = f"{self.selected_customer[1]} {self.selected_customer[2]}"
        warning_msg = f"⚠️ WARNING: DELETE CUSTOMER ⚠️\n\n"
        warning_msg += f"You are about to permanently delete:\n\n"
        warning_msg += f"Customer ID: {self.selected_customer[0]}\n"
        warning_msg += f"Name: {customer_name}\n"
        warning_msg += f"Date of Birth: {self.selected_customer[3]}\n"
        warning_msg += f"Customer Since: {self.selected_customer[4]}\n\n"
        warning_msg += "⚠️ THIS WILL ALSO DELETE:\n"
        warning_msg += "• All profiles associated with this customer\n"
        warning_msg += "• All related data\n\n"
        warning_msg += "❌ THIS CANNOT BE UNDONE!\n\n"
        warning_msg += "Are you sure you want to delete this customer?"
        
        if messagebox.askyesno("Confirm Deletion", warning_msg):
            try:
                self.cursor.execute("DELETE FROM Customer WHERE customerID = %s", (self.selected_customer[0],))
                self.connection.commit()
                messagebox.showinfo("Deleted", f"Customer '{customer_name}' and all related data deleted successfully.")
                self.refresh_customers()
                # Clear selection
                if hasattr(self, 'selected_customer'):
                    delattr(self, 'selected_customer')
                
            except Exception as e:
                self.connection.rollback()
                messagebox.showerror("Database Error", 
                                   f"Failed to delete customer:\n\n{str(e)}\n\nThe customer may have related records that prevent deletion.")
    
    def show_profile_management(self):
        """ניהול פרופילים - CRUD"""
        self.clear_screen()
        self.create_header("Profile Management")
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#ecf0f1', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Buttons frame
        buttons_frame = tk.Frame(content_frame, bg='#ecf0f1')
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        # CRUD buttons
        tk.Button(buttons_frame, text="➕ Add Profile", command=self.add_profile,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="✏ Edit Profile", command=self.edit_profile,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="🗑 Delete Profile", command=self.delete_profile,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="🔄 Refresh", command=self.refresh_profiles,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="⬅ Back", command=self.show_main_menu,
                 bg='#95a5a6', fg='white', font=('Arial', 10, 'bold')).pack(side='right', padx=5)
        
        # Treeview for profiles
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill='both', expand=True)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical')
        self.profile_tree = ttk.Treeview(tree_frame, 
                                        columns=('ProfileID', 'ProfileName', 'ProfilePicture', 'IsOnline', 'CustomerID', 'CustomerName'),
                                        show='headings',
                                        yscrollcommand=v_scrollbar.set)
        
        v_scrollbar.config(command=self.profile_tree.yview)
        
        # Define headings
        headings = ['Profile ID', 'Profile Name', 'Profile Picture', 'Is Online', 'Customer ID', 'Customer Name']
        for i, heading in enumerate(headings):
            self.profile_tree.heading(f'#{i+1}', text=heading)
            self.profile_tree.column(f'#{i+1}', width=120)
        
        self.profile_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        self.refresh_profiles()
        self.profile_tree.bind('<<TreeviewSelect>>', self.on_profile_select)
    
    def refresh_profiles(self):
        """Load profiles"""
        try:
            for item in self.profile_tree.get_children():
                self.profile_tree.delete(item)
            
            self.cursor.execute("""
                SELECT p.profileID, p.profileName, p.profilePicture, p.isOnline, 
                       p.customerID, c.firstName || ' ' || c.lastName
                FROM Profile p
                JOIN Customer c ON p.customerID = c.customerID
                ORDER BY p.profileID
            """)
            profiles = self.cursor.fetchall()
            
            for profile in profiles:
                values = list(profile)
                values[3] = "Yes" if values[3] else "No"  # Convert boolean
                self.profile_tree.insert('', 'end', values=values)
                
            messagebox.showinfo("Success", f"Loaded {len(profiles)} profiles")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profiles: {str(e)}")
    
    def on_profile_select(self, event):
        """Handle profile selection"""
        selection = self.profile_tree.selection()
        if selection:
            item = self.profile_tree.item(selection[0])
            self.selected_profile = item['values']
    
    def add_profile(self):
        """Add new profile"""
        dialog = ProfileDialog(self.root, "Add Profile", self.cursor)
        if dialog.result:
            try:
                self.cursor.execute("""
                    INSERT INTO Profile (profileID, profileName, profilePicture, isOnline, WatchHistoryID, customerID)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, dialog.result)
                
                self.connection.commit()
                messagebox.showinfo("Success", "Profile added successfully!")
                self.refresh_profiles()
                
            except Exception as e:
                self.connection.rollback()
                messagebox.showerror("Error", f"Failed to add profile: {str(e)}")
    
    def edit_profile(self):
        """Edit selected profile"""
        if not hasattr(self, 'selected_profile') or not self.selected_profile:
            messagebox.showwarning("Selection Required", 
                                 "Please select a profile from the table first.\n\nClick on a row in the table to select it, then click Edit.")
            return
        
        dialog = ProfileDialog(self.root, "Edit Profile", self.cursor, self.selected_profile)
        if dialog.result:
            try:
                self.cursor.execute("""
                    UPDATE Profile 
                    SET profileName = %s, profilePicture = %s, isOnline = %s, WatchHistoryID = %s, customerID = %s
                    WHERE profileID = %s
                """, dialog.result[1:] + [self.selected_profile[0]])
                
                self.connection.commit()
                messagebox.showinfo("Success", 
                                  f"Profile '{dialog.result[1]}' updated successfully!")
                self.refresh_profiles()
                
            except Exception as e:
                self.connection.rollback()
                messagebox.showerror("Database Error", 
                                   f"Failed to update profile:\n\n{str(e)}\n\nThe operation has been cancelled.")
    
    def delete_profile(self):
        """Delete selected profile"""
        if not hasattr(self, 'selected_profile') or not self.selected_profile:
            messagebox.showwarning("Selection Required", 
                                 "Please select a profile from the table first.\n\nClick on a row in the table to select it, then click Delete.")
            return
        
        profile_name = self.selected_profile[1]
        warning_msg = f"⚠️ WARNING: DELETE PROFILE ⚠️\n\n"
        warning_msg += f"You are about to permanently delete:\n\n"
        warning_msg += f"Profile ID: {self.selected_profile[0]}\n"
        warning_msg += f"Profile Name: {profile_name}\n"
        warning_msg += f"Customer: {self.selected_profile[5]}\n\n"
        warning_msg += "❌ THIS CANNOT BE UNDONE!\n\n"
        warning_msg += "Are you sure you want to delete this profile?"
        
        if messagebox.askyesno("Confirm Deletion", warning_msg):
            try:
                self.cursor.execute("DELETE FROM Profile WHERE profileID = %s", (self.selected_profile[0],))
                self.connection.commit()
                messagebox.showinfo("Deleted", f"Profile '{profile_name}' deleted successfully.")
                self.refresh_profiles()
                if hasattr(self, 'selected_profile'):
                    delattr(self, 'selected_profile')
                
            except Exception as e:
                self.connection.rollback()
                messagebox.showerror("Database Error", 
                                   f"Failed to delete profile:\n\n{str(e)}")
    
    def show_favorites_management(self):
        """ניהול מועדפים - CRUD"""
        self.clear_screen()
        self.create_header("Favorites Management")
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#ecf0f1', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Buttons frame
        buttons_frame = tk.Frame(content_frame, bg='#ecf0f1')
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        tk.Button(buttons_frame, text="➕ Add Favorite", command=self.add_favorite,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="🗑 Remove Favorite", command=self.delete_favorite,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="🔄 Refresh", command=self.refresh_favorites,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="⬅ Back", command=self.show_main_menu,
                 bg='#95a5a6', fg='white', font=('Arial', 10, 'bold')).pack(side='right', padx=5)
        
        # Treeview for favorites
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill='both', expand=True)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical')
        self.favorites_tree = ttk.Treeview(tree_frame, 
                                          columns=('ProfileID', 'ProfileName', 'MovieID'),
                                          show='headings',
                                          yscrollcommand=v_scrollbar.set)
        
        v_scrollbar.config(command=self.favorites_tree.yview)
        
        headings = ['Profile ID', 'Profile Name', 'Movie ID']
        for i, heading in enumerate(headings):
            self.favorites_tree.heading(f'#{i+1}', text=heading)
            self.favorites_tree.column(f'#{i+1}', width=150)
        
        self.favorites_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        self.refresh_favorites()
        self.favorites_tree.bind('<<TreeviewSelect>>', self.on_favorite_select)
    
    def refresh_favorites(self):
        """Load favorites"""
        try:
            for item in self.favorites_tree.get_children():
                self.favorites_tree.delete(item)
            
            self.cursor.execute("""
                SELECT maf.profileID, p.profileName, maf.movieID
                FROM MarksAsFavorite maf
                JOIN Profile p ON maf.profileID = p.profileID
                ORDER BY maf.profileID, maf.movieID
            """)
            favorites = self.cursor.fetchall()
            
            for favorite in favorites:
                self.favorites_tree.insert('', 'end', values=favorite)
                
            messagebox.showinfo("Success", f"Loaded {len(favorites)} favorites")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load favorites: {str(e)}")
    
    def on_favorite_select(self, event):
        """Handle favorite selection"""
        selection = self.favorites_tree.selection()
        if selection:
            item = self.favorites_tree.item(selection[0])
            self.selected_favorite = item['values']
    
    def add_favorite(self):
        """Add new favorite"""
        dialog = FavoriteDialog(self.root, "Add Favorite", self.cursor)
        if dialog.result:
            try:
                self.cursor.execute("""
                    INSERT INTO MarksAsFavorite (profileID, movieID)
                    VALUES (%s, %s)
                """, dialog.result)
                
                self.connection.commit()
                messagebox.showinfo("Success", "Favorite added successfully!")
                self.refresh_favorites()
                
            except Exception as e:
                self.connection.rollback()
                messagebox.showerror("Error", f"Failed to add favorite: {str(e)}")
    
    def delete_favorite(self):
        """Delete selected favorite"""
        if not hasattr(self, 'selected_favorite') or not self.selected_favorite:
            messagebox.showwarning("Selection Required", 
                                 "Please select a favorite from the table first.")
            return
        
        profile_name = self.selected_favorite[1]
        movie_id = self.selected_favorite[2]
        
        confirm_msg = f"Remove from favorites?\n\n"
        confirm_msg += f"Profile: {profile_name}\n"
        confirm_msg += f"Movie ID: {movie_id}\n\n"
        confirm_msg += "Are you sure you want to continue?"
        
        if messagebox.askyesno("Confirm Remove Favorite", confirm_msg):
            try:
                self.cursor.execute("""
                    DELETE FROM MarksAsFavorite 
                    WHERE profileID = %s AND movieID = %s
                """, (self.selected_favorite[0], self.selected_favorite[2]))
                
                self.connection.commit()
                messagebox.showinfo("Success", 
                                  f"Movie {movie_id} removed from {profile_name}'s favorites successfully!")
                self.refresh_favorites()
                if hasattr(self, 'selected_favorite'):
                    delattr(self, 'selected_favorite')
                
            except Exception as e:
                self.connection.rollback()
                messagebox.showerror("Database Error", 
                                   f"Failed to remove favorite:\n\n{str(e)}")
    
    def show_reports_screen(self):
        """מסך דוחות ושאילתות"""
        self.clear_screen()
        self.create_header("Reports & Queries")
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#ecf0f1', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Left panel for queries
        left_panel = tk.Frame(content_frame, bg='#ecf0f1', width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="Available Reports", font=('Arial', 14, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').pack(pady=(0, 20))
        
        # Query buttons
        queries = [
            ("📊 Customer Statistics", self.query_customer_stats),
            ("⭐ Popular Movies", self.query_popular_movies),
            ("📱 Profile Activity", self.query_profile_activity),
            ("💰 Payment Summary", self.query_payment_summary),
            ("🎬 Watch History Analysis", self.query_watch_history),
        ]
        
        for text, command in queries:
            btn = tk.Button(left_panel, text=text, command=command,
                           bg='#3498db', fg='white', font=('Arial', 10),
                           width=35, pady=5, cursor='hand2')
            btn.pack(pady=2, fill='x')
        
        # Back button
        tk.Button(left_panel, text="⬅ Back to Main Menu", command=self.show_main_menu,
                 bg='#95a5a6', fg='white', font=('Arial', 10, 'bold'),
                 width=35, pady=5).pack(side='bottom', pady=10, fill='x')
        
        # Right panel for results
        right_panel = tk.Frame(content_frame, bg='white', relief='sunken', bd=2)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Results area
        results_frame = tk.Frame(right_panel)
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for results
        self.results_tree = ttk.Treeview(results_frame, show='headings', height=20)
        results_scrollbar = ttk.Scrollbar(results_frame, command=self.results_tree.yview)
        self.results_tree.config(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True)
        results_scrollbar.pack(side='right', fill='y')
        
        # Initial message
        tk.Label(results_frame, text="Select a report from the left panel to view results...", 
                font=('Arial', 12)).pack(pady=50)
    
    def query_customer_stats(self):
        """שאילתה 1: סטטיסטיקות לקוחות"""
        try:
            self.cursor.execute("""
                SELECT 
                    c.customerID,
                    c.firstName || ' ' || c.lastName AS customer_name,
                    COUNT(p.profileID) AS num_profiles,
                    COUNT(DISTINCT maf.movieID) AS num_favorites,
                    EXTRACT(YEAR FROM c.customerSince) AS join_year
                FROM Customer c
                LEFT JOIN Profile p ON c.customerID = p.customerID
                LEFT JOIN MarksAsFavorite maf ON p.profileID = maf.profileID
                GROUP BY c.customerID, c.firstName, c.lastName, c.customerSince
                ORDER BY num_favorites DESC
            """)
            
            results = self.cursor.fetchall()
            self.display_query_results(results, 
                ['Customer ID', 'Customer Name', 'Profiles', 'Favorites', 'Join Year'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {str(e)}")
    
    def query_popular_movies(self):
        """שאילתה 2: סרטים פופולריים"""
        try:
            self.cursor.execute("""
                SELECT 
                    maf.movieID,
                    COUNT(maf.profileID) AS favorite_count
                FROM MarksAsFavorite maf
                GROUP BY maf.movieID
                HAVING COUNT(maf.profileID) > 0
                ORDER BY favorite_count DESC
                LIMIT 10
            """)
            
            results = self.cursor.fetchall()
            self.display_query_results(results, 
                ['Movie ID', 'Favorite Count'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {str(e)}")
    
    def query_profile_activity(self):
        """שאילתה 3: פעילות פרופילים"""
        try:
            self.cursor.execute("""
                SELECT 
                    p.profileID,
                    p.profileName,
                    p.isOnline,
                    COUNT(maf.movieID) AS favorites_count
                FROM Profile p
                LEFT JOIN MarksAsFavorite maf ON p.profileID = maf.profileID
                GROUP BY p.profileID, p.profileName, p.isOnline
                ORDER BY favorites_count DESC
            """)
            
            results = self.cursor.fetchall()
            formatted_results = []
            for row in results:
                formatted_row = list(row)
                formatted_row[2] = "Online" if formatted_row[2] else "Offline"
                formatted_results.append(formatted_row)
            
            self.display_query_results(formatted_results, 
                ['Profile ID', 'Profile Name', 'Status', 'Favorites'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {str(e)}")
    
    def query_payment_summary(self):
        """שאילתה 4: סיכום תשלומים"""
        try:
            # This is a simplified query since Payment table structure may vary
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_customers,
                    AVG(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM customerSince)) as avg_years_as_customer
                FROM Customer
            """)
            
            results = self.cursor.fetchall()
            self.display_query_results(results, 
                ['Total Customers', 'Avg Years as Customer'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {str(e)}")
    
    def query_watch_history(self):
        """שאילתה 5: ניתוח לקוחות ופרופילים"""
        try:
            self.cursor.execute("""
                SELECT 
                    c.customerID,
                    c.firstName || ' ' || c.lastName as customer_name,
                    COUNT(p.profileID) as profile_count,
                    CASE 
                        WHEN COUNT(p.profileID) >= 3 THEN 'Family'
                        WHEN COUNT(p.profileID) = 2 THEN 'Couple'
                        ELSE 'Individual'
                    END as customer_type
                FROM Customer c
                LEFT JOIN Profile p ON c.customerID = p.customerID
                GROUP BY c.customerID, c.firstName, c.lastName
                ORDER BY profile_count DESC
            """)
            
            results = self.cursor.fetchall()
            self.display_query_results(results, 
                ['Customer ID', 'Customer Name', 'Profile Count', 'Customer Type'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {str(e)}")
    
    def display_query_results(self, results, columns):
        """Display query results in treeview"""
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Configure columns
        self.results_tree['columns'] = columns
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120)
        
        # Insert results
        for row in results:
            self.results_tree.insert('', 'end', values=row)
        
        messagebox.showinfo("Success", f"Query completed! Found {len(results)} results")
    
    def show_functions_screen(self):
        """מסך פונקציות ופרוצדורות"""
        self.clear_screen()
        self.create_header("Functions & Procedures")
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#ecf0f1', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Functions frame
        functions_frame = tk.LabelFrame(content_frame, text="Database Functions", 
                                       font=('Arial', 12, 'bold'))
        functions_frame.pack(fill='x', padx=10, pady=10)
        
        # Function buttons
        tk.Button(functions_frame, text="🔧 Clean Test Data", 
                 command=self.clean_test_data,
                 bg='#e67e22', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=10)
        
        tk.Button(functions_frame, text="📊 Generate Sample Data", 
                 command=self.generate_sample_data,
                 bg='#9b59b6', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=10)
        
        tk.Button(functions_frame, text="⭐ Count Total Favorites", 
                 command=self.count_total_favorites,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=10)
        
        # Results area
        results_frame = tk.LabelFrame(content_frame, text="Function Results", 
                                     font=('Arial', 12, 'bold'))
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.function_results_text = tk.Text(results_frame, font=('Courier', 10), height=15)
        function_scrollbar = ttk.Scrollbar(results_frame, command=self.function_results_text.yview)
        self.function_results_text.config(yscrollcommand=function_scrollbar.set)
        
        self.function_results_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        function_scrollbar.pack(side='right', fill='y')
        
        # Back button
        tk.Button(content_frame, text="⬅ Back to Main Menu", command=self.show_main_menu,
                 bg='#95a5a6', fg='white', font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Initial message
        self.function_results_text.insert('1.0', "Select a function above to execute...\n\n")
    
    def clean_test_data(self):
        """Function 1: Clean test data"""
        try:
            # Count records before deletion
            self.cursor.execute("SELECT COUNT(*) FROM MarksAsFavorite")
            favorites_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM Profile")
            profiles_count = self.cursor.fetchone()[0]
            
            result_text = f"Clean Test Data Function Executed:\n"
            result_text += f"- Found {favorites_count} favorite records\n"
            result_text += f"- Found {profiles_count} profile records\n"
            result_text += f"- Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += "-" * 50 + "\n\n"
            
            self.function_results_text.insert('end', result_text)
            messagebox.showinfo("Success", f"Data analysis completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Function failed: {str(e)}")
    
    def generate_sample_data(self):
        """Function 2: Generate sample data info"""
        try:
            # Get next available IDs
            self.cursor.execute("SELECT COALESCE(MAX(customerID), 0) + 1 FROM Customer")
            next_customer_id = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COALESCE(MAX(profileID), 0) + 1 FROM Profile")
            next_profile_id = self.cursor.fetchone()[0]
            
            result_text = f"Sample Data Generation Info:\n"
            result_text += f"- Next available Customer ID: {next_customer_id}\n"
            result_text += f"- Next available Profile ID: {next_profile_id}\n"
            result_text += f"- Suggestion: Create customers with IDs starting from {next_customer_id}\n"
            result_text += f"- Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += "-" * 50 + "\n\n"
            
            self.function_results_text.insert('end', result_text)
            messagebox.showinfo("Success", "Sample data analysis completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Function failed: {str(e)}")
    
    def count_total_favorites(self):
        """Function 3: Count total favorites"""
        try:
            # Count total favorites by profile
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_favorites,
                    COUNT(DISTINCT profileID) as profiles_with_favorites,
                    COUNT(DISTINCT movieID) as unique_movies_favorited
                FROM MarksAsFavorite
            """)
            
            stats = self.cursor.fetchone()
            
            result_text = f"Favorites Statistics:\n"
            result_text += f"- Total Favorites: {stats[0]}\n"
            result_text += f"- Profiles with Favorites: {stats[1]}\n"
            result_text += f"- Unique Movies Favorited: {stats[2]}\n"
            result_text += f"- Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += "-" * 50 + "\n\n"
            
            self.function_results_text.insert('end', result_text)
            messagebox.showinfo("Success", "Favorites analysis completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Function failed: {str(e)}")


class CustomerDialog:
    """Dialog for adding/editing customers"""
    def __init__(self, parent, title, customer_data=None):
        self.result = None
        
        # Create dialog window - INCREASED SIZE
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x650")  # Made larger
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        self.dialog.transient(parent)
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (650 // 2)
        self.dialog.geometry(f"600x650+{x}+{y}")
        
        # Main frame with scrollbar support
        canvas = tk.Canvas(self.dialog, bg='white')
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main content in scrollable frame
        main_frame = tk.Frame(scrollable_frame, padx=40, pady=40, bg='white')
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text=title, font=('Arial', 18, 'bold'), 
                              bg='white', fg='#2c3e50')
        title_label.pack(pady=(0, 30))
        
        # Form fields with better spacing
        fields = [
            ('Customer ID:', 'customer_id'),
            ('First Name:', 'first_name'),
            ('Last Name:', 'last_name'),
            ('Date of Birth (YYYY-MM-DD):', 'dob'),
            ('Customer Since (YYYY-MM-DD):', 'customer_since')
        ]
        
        self.entries = {}
        
        for i, (label, field) in enumerate(fields):
            # Label
            label_widget = tk.Label(main_frame, text=label, font=('Arial', 13, 'bold'), 
                                  bg='white', fg='#34495e')
            label_widget.pack(anchor='w', pady=(20, 8))
            
            # Entry with better styling
            entry = tk.Entry(main_frame, font=('Arial', 13), width=40, 
                           relief='solid', bd=2, highlightthickness=2,
                           highlightcolor='#3498db')
            entry.pack(fill='x', pady=(0, 15), ipady=12)
            self.entries[field] = entry
            
            # Fill with existing data if editing
            if customer_data and i < len(customer_data):
                entry.insert(0, str(customer_data[i]))
                if title == "Edit Customer" and field == 'customer_id':
                    entry.config(state='readonly')  # Don't allow editing ID
        
        # Validation info
        info_frame = tk.Frame(main_frame, bg='#e8f4fd', relief='solid', bd=2)
        info_frame.pack(fill='x', pady=(30, 30))
        
        info_label = tk.Label(info_frame, 
                             text="💡 Important Notes:\n" +
                                  "• Customer ID must be a unique number\n" +
                                  "• Dates must be in YYYY-MM-DD format (e.g., 1990-12-25)\n" +
                                  "• All fields are required\n" +
                                  "• Names should contain only letters and spaces", 
                             font=('Arial', 11), bg='#e8f4fd', fg='#2c3e50', justify='left')
        info_label.pack(padx=20, pady=15)
        
        # Buttons frame with better layout
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=(30, 20))
        
        # Confirm button
        confirm_btn = tk.Button(button_frame, text="✅ Save Customer", command=self.save,
                               bg='#27ae60', fg='white', font=('Arial', 14, 'bold'),
                               width=18, height=2, cursor='hand2',
                               relief='flat', bd=0)
        confirm_btn.pack(side='left', padx=15)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="❌ Cancel", command=self.cancel,
                              bg='#e74c3c', fg='white', font=('Arial', 14, 'bold'),
                              width=18, height=2, cursor='hand2',
                              relief='flat', bd=0)
        cancel_btn.pack(side='left', padx=15)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Focus on first field
        if not customer_data:
            self.entries['customer_id'].focus()
        else:
            self.entries['first_name'].focus()
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Wait for dialog
        parent.wait_window(self.dialog)
    
    def save(self):
        """Save customer data with validation"""
        try:
            # Validate all fields are filled
            for field_name, entry in self.entries.items():
                if not entry.get().strip():
                    field_display = field_name.replace('_', ' ').title()
                    messagebox.showerror("Validation Error", f"Please fill in {field_display}")
                    entry.focus()
                    return
            
            # Validate Customer ID is numeric
            try:
                customer_id = int(self.entries['customer_id'].get().strip())
                if customer_id <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Validation Error", "Customer ID must be a positive number")
                self.entries['customer_id'].focus()
                return
            
            # Validate date formats
            try:
                dob = self.entries['dob'].get().strip()
                customer_since = self.entries['customer_since'].get().strip()
                
                # Check date format YYYY-MM-DD
                datetime.strptime(dob, '%Y-%m-%d')
                datetime.strptime(customer_since, '%Y-%m-%d')
                    
            except ValueError:
                messagebox.showerror("Validation Error", 
                                   "Dates must be in YYYY-MM-DD format\nExample: 1990-12-25")
                return
            
            # Validate names contain only letters and spaces
            first_name = self.entries['first_name'].get().strip()
            last_name = self.entries['last_name'].get().strip()
            
            if not all(c.isalpha() or c.isspace() for c in first_name):
                messagebox.showerror("Validation Error", "First name should contain only letters and spaces")
                self.entries['first_name'].focus()
                return
                
            if not all(c.isalpha() or c.isspace() for c in last_name):
                messagebox.showerror("Validation Error", "Last name should contain only letters and spaces")
                self.entries['last_name'].focus()
                return
            
            # Show confirmation dialog
            confirm_msg = f"Save customer information?\n\n"
            confirm_msg += f"Customer ID: {customer_id}\n"
            confirm_msg += f"Name: {first_name} {last_name}\n"
            confirm_msg += f"Date of Birth: {dob}\n"
            confirm_msg += f"Customer Since: {customer_since}"
            
            if messagebox.askyesno("Confirm Save", confirm_msg):
                # Collect validated data
                self.result = [
                    customer_id,
                    first_name,
                    last_name,
                    dob,
                    customer_since
                ]
                self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")
    
    def cancel(self):
        """Cancel dialog with confirmation"""
        if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel?\nAny changes will be lost."):
            self.dialog.destroy()


class ProfileDialog:
    """Dialog for adding/editing profiles"""
    def __init__(self, parent, title, cursor, profile_data=None):
        self.result = None
        self.cursor = cursor
        
        # Create dialog window - INCREASED SIZE
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("700x750")  # Made larger
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        self.dialog.transient(parent)
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (750 // 2)
        self.dialog.geometry(f"700x750+{x}+{y}")
        
        # Main frame with scrollbar support
        canvas = tk.Canvas(self.dialog, bg='white')
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main content
        main_frame = tk.Frame(scrollable_frame, padx=40, pady=40, bg='white')
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text=title, font=('Arial', 18, 'bold'), 
                              bg='white', fg='#2c3e50')
        title_label.pack(pady=(0, 30))
        
        # Profile ID
        tk.Label(main_frame, text="Profile ID:", font=('Arial', 13, 'bold'), 
                bg='white', fg='#34495e').pack(anchor='w', pady=(20, 8))
        self.profile_id_entry = tk.Entry(main_frame, font=('Arial', 13), width=45, 
                                        relief='solid', bd=2, highlightthickness=2,
                                        highlightcolor='#3498db')
        self.profile_id_entry.pack(fill='x', pady=(0, 15), ipady=12)
        
        # Profile Name
        tk.Label(main_frame, text="Profile Name:", font=('Arial', 13, 'bold'), 
                bg='white', fg='#34495e').pack(anchor='w', pady=(20, 8))
        self.profile_name_entry = tk.Entry(main_frame, font=('Arial', 13), width=45, 
                                          relief='solid', bd=2, highlightthickness=2,
                                          highlightcolor='#3498db')
        self.profile_name_entry.pack(fill='x', pady=(0, 15), ipady=12)
        
        # Profile Picture
        tk.Label(main_frame, text="Profile Picture URL:", font=('Arial', 13, 'bold'), 
                bg='white', fg='#34495e').pack(anchor='w', pady=(20, 8))
        self.profile_picture_entry = tk.Entry(main_frame, font=('Arial', 13), width=45, 
                                             relief='solid', bd=2, highlightthickness=2,
                                             highlightcolor='#3498db')
        self.profile_picture_entry.pack(fill='x', pady=(0, 15), ipady=12)
        
        # Customer selection
        tk.Label(main_frame, text="Select Customer:", font=('Arial', 13, 'bold'), 
                bg='white', fg='#34495e').pack(anchor='w', pady=(20, 8))
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(main_frame, textvariable=self.customer_var, 
                                          font=('Arial', 13), width=42, state='readonly', height=10)
        self.customer_combo.pack(fill='x', pady=(0, 15), ipady=12)
        
        # Watch History ID
        tk.Label(main_frame, text="Watch History ID:", font=('Arial', 13, 'bold'), 
                bg='white', fg='#34495e').pack(anchor='w', pady=(20, 8))
        self.watch_history_entry = tk.Entry(main_frame, font=('Arial', 13), width=45, 
                                           relief='solid', bd=2, highlightthickness=2,
                                           highlightcolor='#3498db')
        self.watch_history_entry.pack(fill='x', pady=(0, 15), ipady=12)
        
        # Online status checkbox with better styling
        checkbox_frame = tk.Frame(main_frame, bg='white')
        checkbox_frame.pack(fill='x', pady=(25, 25))
        
        self.is_online_var = tk.BooleanVar()
        online_checkbox = tk.Checkbutton(checkbox_frame, text="Profile is currently online", 
                                        variable=self.is_online_var,
                                        font=('Arial', 13), bg='white', fg='#34495e',
                                        activebackground='white')
        online_checkbox.pack(anchor='w')
        
        # Load customers
        self.load_customers()
        
        # Fill with existing data if editing
        if profile_data:
            self.fill_existing_data(profile_data)
        
        # Validation info
        info_frame = tk.Frame(main_frame, bg='#e8f4fd', relief='solid', bd=2)
        info_frame.pack(fill='x', pady=(30, 30))
        
        info_label = tk.Label(info_frame, 
                             text="💡 Important Notes:\n" +
                                  "• Profile ID must be a unique number\n" +
                                  "• Watch History ID should be a number (can be same as Profile ID)\n" +
                                  "• Select a customer from the dropdown\n" +
                                  "• Profile picture URL is optional", 
                             font=('Arial', 11), bg='#e8f4fd', fg='#2c3e50', justify='left')
        info_label.pack(padx=20, pady=15)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=(30, 20))
        
        # Confirm button
        confirm_btn = tk.Button(button_frame, text="✅ Save Profile", command=self.save,
                               bg='#27ae60', fg='white', font=('Arial', 14, 'bold'),
                               width=18, height=2, cursor='hand2',
                               relief='flat', bd=0)
        confirm_btn.pack(side='left', padx=15)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="❌ Cancel", command=self.cancel,
                              bg='#e74c3c', fg='white', font=('Arial', 14, 'bold'),
                              width=18, height=2, cursor='hand2',
                              relief='flat', bd=0)
        cancel_btn.pack(side='left', padx=15)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Focus on first field
        if not profile_data:
            self.profile_id_entry.focus()
        else:
            self.profile_name_entry.focus()
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Wait for dialog
        parent.wait_window(self.dialog)
    
    def load_customers(self):
        """Load customer list for selection"""
        try:
            self.cursor.execute("SELECT customerID, firstName || ' ' || lastName FROM Customer ORDER BY firstName")
            customers = self.cursor.fetchall()
            customer_list = [f"{row[0]} - {row[1]}" for row in customers]
            self.customer_combo['values'] = customer_list
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
    
    def fill_existing_data(self, profile_data):
        """Fill form with existing profile data"""
        try:
            self.profile_id_entry.insert(0, str(profile_data[0]))
            self.profile_id_entry.config(state='readonly')  # Don't allow editing ID
            self.profile_name_entry.insert(0, profile_data[1])
            self.profile_picture_entry.insert(0, profile_data[2])
            self.is_online_var.set(profile_data[3] == "Yes")
            
            # Set customer
            customer_id = profile_data[4]
            for i, value in enumerate(self.customer_combo['values']):
                if value.startswith(str(customer_id)):
                    self.customer_combo.current(i)
                    break
            
            # Generate a default watch history ID
            self.watch_history_entry.insert(0, str(profile_data[0]))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error filling form: {str(e)}")
    
    def save(self):
        """Save profile data with validation"""
        try:
            # Validate required fields
            if not self.profile_id_entry.get().strip():
                messagebox.showerror("Validation Error", "Please enter Profile ID")
                self.profile_id_entry.focus()
                return
                
            if not self.profile_name_entry.get().strip():
                messagebox.showerror("Validation Error", "Please enter Profile Name")
                self.profile_name_entry.focus()
                return
                
            if not self.customer_var.get():
                messagebox.showerror("Validation Error", "Please select a customer")
                self.customer_combo.focus()
                return
                
            if not self.watch_history_entry.get().strip():
                messagebox.showerror("Validation Error", "Please enter Watch History ID")
                self.watch_history_entry.focus()
                return
            
            # Validate numeric fields
            try:
                profile_id = int(self.profile_id_entry.get().strip())
                watch_history_id = int(self.watch_history_entry.get().strip())
                if profile_id <= 0 or watch_history_id <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Validation Error", "Profile ID and Watch History ID must be positive numbers")
                return
            
            # Get customer ID
            customer_id = int(self.customer_var.get().split(' - ')[0])
            
            # Validate profile name
            profile_name = self.profile_name_entry.get().strip()
            if len(profile_name) < 2:
                messagebox.showerror("Validation Error", "Profile name must be at least 2 characters long")
                self.profile_name_entry.focus()
                return
            
            # Get other fields
            profile_picture = self.profile_picture_entry.get().strip() or "default_avatar.png"
            is_online = self.is_online_var.get()
            
            # Show confirmation dialog
            customer_name = self.customer_var.get().split(' - ')[1]
            confirm_msg = f"Save profile information?\n\n"
            confirm_msg += f"Profile ID: {profile_id}\n"
            confirm_msg += f"Profile Name: {profile_name}\n"
            confirm_msg += f"Customer: {customer_name}\n"
            confirm_msg += f"Online Status: {'Online' if is_online else 'Offline'}\n"
            confirm_msg += f"Watch History ID: {watch_history_id}"
            
            if messagebox.askyesno("Confirm Save", confirm_msg):
                # Collect validated data
                self.result = [
                    profile_id,
                    profile_name,
                    profile_picture,
                    is_online,
                    watch_history_id,
                    customer_id
                ]
                self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")
    
    def cancel(self):
        """Cancel dialog with confirmation"""
        if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel?\nAny changes will be lost."):
            self.dialog.destroy()


class FavoriteDialog:
    """Dialog for adding favorites"""
    def __init__(self, parent, title, cursor):
        self.result = None
        self.cursor = cursor
        
        # Create dialog window - INCREASED SIZE
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x550")  # Made larger
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        self.dialog.transient(parent)
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f"600x550+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=40, pady=40, bg='white')
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text=title, font=('Arial', 18, 'bold'), 
                              bg='white', fg='#2c3e50')
        title_label.pack(pady=(0, 40))
        
        # Profile selection
        tk.Label(main_frame, text="Select Profile:", font=('Arial', 13, 'bold'), 
                bg='white', fg='#34495e').pack(anchor='w', pady=(20, 8))
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(main_frame, textvariable=self.profile_var, 
                                         font=('Arial', 13), width=40, state='readonly', height=10)
        self.profile_combo.pack(fill='x', pady=(0, 25), ipady=12)
        
        # Movie ID
        tk.Label(main_frame, text="Movie ID:", font=('Arial', 13, 'bold'), 
                bg='white', fg='#34495e').pack(anchor='w', pady=(20, 8))
        self.movie_id_entry = tk.Entry(main_frame, font=('Arial', 13), width=40, 
                                      relief='solid', bd=2, highlightthickness=2,
                                      highlightcolor='#3498db')
        self.movie_id_entry.pack(fill='x', pady=(0, 25), ipady=12)
        
        # Load profiles
        self.load_profiles()
        
        # Validation info
        info_frame = tk.Frame(main_frame, bg='#e8f4fd', relief='solid', bd=2)
        info_frame.pack(fill='x', pady=(30, 30))
        
        info_label = tk.Label(info_frame, 
                             text="💡 Important Notes:\n" +
                                  "• Select a profile from the dropdown\n" +
                                  "• Movie ID must be a positive number\n" +
                                  "• This will add the movie to the profile's favorites\n" +
                                  "• Duplicate favorites will be rejected", 
                             font=('Arial', 11), bg='#e8f4fd', fg='#2c3e50', justify='left')
        info_label.pack(padx=20, pady=15)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=(30, 0))
        
        # Confirm button
        confirm_btn = tk.Button(button_frame, text="✅ Add to Favorites", command=self.save,
                               bg='#27ae60', fg='white', font=('Arial', 14, 'bold'),
                               width=18, height=2, cursor='hand2',
                               relief='flat', bd=0)
        confirm_btn.pack(side='left', padx=15)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="❌ Cancel", command=self.cancel,
                              bg='#e74c3c', fg='white', font=('Arial', 14, 'bold'),
                              width=15, height=2, cursor='hand2',
                              relief='flat', bd=0)
        cancel_btn.pack(side='left', padx=15)
        
        # Focus on profile selection
        self.profile_combo.focus()
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Wait for dialog
        parent.wait_window(self.dialog)
    
    def load_profiles(self):
        """Load profile list for selection"""
        try:
            self.cursor.execute("SELECT profileID, profileName FROM Profile ORDER BY profileName")
            profiles = self.cursor.fetchall()
            profile_list = [f"{row[0]} - {row[1]}" for row in profiles]
            self.profile_combo['values'] = profile_list
            
            if not profiles:
                messagebox.showwarning("No Profiles", "No profiles found. Please add profiles first.")
                self.dialog.destroy()
                return
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profiles: {str(e)}")
            self.dialog.destroy()
    
    def save(self):
        """Save favorite data with validation"""
        try:
            # Validate profile selection
            if not self.profile_var.get():
                messagebox.showerror("Validation Error", "Please select a profile")
                self.profile_combo.focus()
                return
            
            # Validate movie ID
            if not self.movie_id_entry.get().strip():
                messagebox.showerror("Validation Error", "Please enter Movie ID")
                self.movie_id_entry.focus()
                return
            
            # Validate movie ID is numeric
            try:
                movie_id = int(self.movie_id_entry.get().strip())
                if movie_id <= 0:
                    messagebox.showerror("Validation Error", "Movie ID must be a positive number")
                    self.movie_id_entry.focus()
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Movie ID must be a valid number")
                self.movie_id_entry.focus()
                return
            
            # Get profile ID
            profile_id = int(self.profile_var.get().split(' - ')[0])
            profile_name = self.profile_var.get().split(' - ')[1]
            
            # Check if this favorite already exists
            try:
                self.cursor.execute("""
                    SELECT COUNT(*) FROM MarksAsFavorite 
                    WHERE profileID = %s AND movieID = %s
                """, (profile_id, movie_id))
                
                if self.cursor.fetchone()[0] > 0:
                    messagebox.showwarning("Duplicate Entry", 
                                         f"Movie {movie_id} is already in {profile_name}'s favorites!")
                    return
                    
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not check for duplicates: {str(e)}")
            
            # Show confirmation dialog
            confirm_msg = f"Add to favorites?\n\n"
            confirm_msg += f"Profile: {profile_name}\n"
            confirm_msg += f"Movie ID: {movie_id}\n\n"
            confirm_msg += "This movie will be added to the profile's favorite list."
            
            if messagebox.askyesno("Confirm Add Favorite", confirm_msg):
                # Collect validated data
                self.result = [profile_id, movie_id]
                self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")
    
    def cancel(self):
        """Cancel dialog with confirmation"""
        if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel?"):
            self.dialog.destroy()


def main():
    root = tk.Tk()
    app = StreamingServiceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()