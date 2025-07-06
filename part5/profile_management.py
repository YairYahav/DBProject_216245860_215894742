"""
Profile Management Screen for Streaming Service Management System
מסך ניהול פרופילים למערכת ניהול שירותי סטרימינג

Provides CRUD operations for Profile table (linked to Customer table)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import os

class ProfileManagement:
    """
    Profile management class for CRUD operations on Profile table
    """
    
    def __init__(self, parent_frame, db_manager, colors):
        """
        Initialize profile management
        
        Args:
            parent_frame: Parent frame for profile management
            db_manager: Database manager instance
            colors: Color scheme dictionary
        """
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.colors = colors
        
        # Current data
        self.profiles_data = []
        self.customers_data = []
        self.selected_profile = None
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        # Form variables
        self.form_vars = {}
        
        # Profile pictures directory
        self.profile_pics_dir = "assets/profile_pictures"
        os.makedirs(self.profile_pics_dir, exist_ok=True)
    
    def create_interface(self):
        """Create profile management interface"""
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Search and filters
        self.create_search_section(main_container)
        
        # Main content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Profile list (left side)
        self.create_profile_list(content_frame)
        
        # Profile form (right side)
        self.create_profile_form(content_frame)
        
        # Load initial data
        self.load_customers_data()
        self.refresh_profile_list()
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame,
                               text="👤 Profile Management",
                               font=('Arial', 16, 'bold'),
                               foreground=self.colors['primary'])
        title_label.pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame,
                  text="➕ New Profile",
                  command=self.new_profile,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="🔄 Refresh",
                  command=self.refresh_profile_list,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="📊 Profile Stats",
                  command=self.show_profile_statistics,
                  style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, pady=(5, 0))
    
    def create_search_section(self, parent):
        """Create search and filter section"""
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Search box
        ttk.Label(search_frame, text="🔍 Search:").pack(side=tk.LEFT)
        
        search_entry = ttk.Entry(search_frame,
                                textvariable=self.search_var,
                                width=25)
        search_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        # Filter by customer
        ttk.Label(search_frame, text="Customer:").pack(side=tk.LEFT)
        
        self.customer_filter = ttk.Combobox(search_frame,
                                           values=['All Customers'],
                                           state='readonly',
                                           width=20)
        self.customer_filter.set('All Customers')
        self.customer_filter.pack(side=tk.LEFT, padx=(5, 20))
        self.customer_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_profile_list())
        
        # Filter by status
        ttk.Label(search_frame, text="Status:").pack(side=tk.LEFT)
        
        self.status_filter = ttk.Combobox(search_frame,
                                         values=['All', 'Active', 'Inactive', 'Suspended', 'Trial'],
                                         state='readonly',
                                         width=12)
        self.status_filter.set('All')
        self.status_filter.pack(side=tk.LEFT, padx=(5, 20))
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_profile_list())
        
        # Filter by online status
        ttk.Label(search_frame, text="Online:").pack(side=tk.LEFT)
        
        self.online_filter = ttk.Combobox(search_frame,
                                         values=['All', 'Online', 'Offline'],
                                         state='readonly',
                                         width=10)
        self.online_filter.set('All')
        self.online_filter.pack(side=tk.LEFT, padx=(5, 0))
        self.online_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_profile_list())
    
    def create_profile_list(self, parent):
        """Create profile list section"""
        # Left frame for profile list
        list_frame = ttk.LabelFrame(parent, text="Profile List", padding="10")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Treeview for profiles
        columns = ('ID', 'Profile Name', 'Customer', 'Status', 'Online', 'Watch History')
        self.profile_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.profile_tree.heading('ID', text='Profile ID')
        self.profile_tree.heading('Profile Name', text='Profile Name')
        self.profile_tree.heading('Customer', text='Customer Name')
        self.profile_tree.heading('Status', text='Account Status')
        self.profile_tree.heading('Online', text='Online Status')
        self.profile_tree.heading('Watch History', text='Watch History ID')
        
        self.profile_tree.column('ID', width=80, anchor=tk.CENTER)
        self.profile_tree.column('Profile Name', width=120, anchor=tk.W)
        self.profile_tree.column('Customer', width=150, anchor=tk.W)
        self.profile_tree.column('Status', width=100, anchor=tk.CENTER)
        self.profile_tree.column('Online', width=80, anchor=tk.CENTER)
        self.profile_tree.column('Watch History', width=100, anchor=tk.CENTER)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.profile_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.profile_tree.xview)
        self.profile_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.profile_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.profile_tree.bind('<<TreeviewSelect>>', self.on_profile_select)
        
        # Context menu
        self.create_context_menu()
        self.profile_tree.bind('<Button-3>', self.show_context_menu)
    
    def create_context_menu(self):
        """Create context menu for profile list"""
        self.context_menu = tk.Menu(self.profile_tree, tearoff=0)
        self.context_menu.add_command(label="Edit Profile", command=self.edit_selected_profile)
        self.context_menu.add_command(label="View Watch History", command=self.view_watch_history)
        self.context_menu.add_command(label="View Reviews", command=self.view_profile_reviews)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Toggle Online Status", command=self.toggle_online_status)
        self.context_menu.add_command(label="Delete Profile", command=self.delete_selected_profile)
    
    def show_context_menu(self, event):
        """Show context menu"""
        if self.profile_tree.selection():
            self.context_menu.post(event.x_root, event.y_root)
    
    def create_profile_form(self, parent):
        """Create profile form section"""
        # Right frame for profile form
        form_frame = ttk.LabelFrame(parent, text="Profile Details", padding="15")
        form_frame.pack(side=tk.RIGHT, fill=tk.Y, ipadx=20)
        
        # Form fields
        self.create_form_fields(form_frame)
        
        # Profile picture section
        self.create_picture_section(form_frame)
        
        # Form buttons
        self.create_form_buttons(form_frame)
        
        # Set initial state
        self.set_form_state('view')
    
    def create_form_fields(self, parent):
        """Create form input fields"""
        # Initialize form variables
        self.form_vars = {
            'profileID': tk.StringVar(),
            'profileName': tk.StringVar(),
            'customerID': tk.StringVar(),
            'WatchHistoryID': tk.StringVar(),
            'account_status': tk.StringVar(),
            'isOnline': tk.BooleanVar(),
            'profilePicture': tk.StringVar()
        }
        
        # Profile ID (readonly)
        row = 0
        ttk.Label(parent, text="Profile ID:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.id_entry = ttk.Entry(parent, textvariable=self.form_vars['profileID'], state='readonly', width=30)
        self.id_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Profile Name
        row += 1
        ttk.Label(parent, text="*Profile Name:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(parent, textvariable=self.form_vars['profileName'], width=30)
        self.name_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Customer Selection
        row += 1
        ttk.Label(parent, text="*Customer:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.customer_combo = ttk.Combobox(parent,
                                          state='readonly',
                                          width=27)
        self.customer_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Watch History ID
        row += 1
        ttk.Label(parent, text="*Watch History ID:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.watch_entry = ttk.Entry(parent, textvariable=self.form_vars['WatchHistoryID'], width=30)
        self.watch_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Account Status
        row += 1
        ttk.Label(parent, text="Account Status:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.status_combo = ttk.Combobox(parent,
                                        textvariable=self.form_vars['account_status'],
                                        values=['Active', 'Inactive', 'Suspended', 'Trial'],
                                        state='readonly',
                                        width=27)
        self.status_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Online Status
        row += 1
        ttk.Label(parent, text="Online Status:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.online_check = ttk.Checkbutton(parent,
                                           text="Currently Online",
                                           variable=self.form_vars['isOnline'])
        self.online_check.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Profile Picture Path
        row += 1
        ttk.Label(parent, text="Profile Picture:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.picture_entry = ttk.Entry(parent, textvariable=self.form_vars['profilePicture'], width=30)
        self.picture_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Required fields note
        row += 1
        note_label = ttk.Label(parent, text="* Required fields", font=('Arial', 8), foreground='red')
        note_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def create_picture_section(self, parent):
        """Create profile picture section"""
        picture_frame = ttk.LabelFrame(parent, text="Profile Picture", padding="10")
        picture_frame.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        
        # Picture preview
        self.picture_label = ttk.Label(picture_frame, text="📷\nNo Picture", 
                                      font=('Arial', 12), 
                                      anchor=tk.CENTER,
                                      relief=tk.RAISED,
                                      padding=(20, 20))
        self.picture_label.pack(pady=(0, 10))
        
        # Picture buttons
        pic_button_frame = ttk.Frame(picture_frame)
        pic_button_frame.pack()
        
        ttk.Button(pic_button_frame,
                  text="📁 Browse",
                  command=self.browse_picture,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(pic_button_frame,
                  text="🗑️ Remove",
                  command=self.remove_picture,
                  style='Secondary.TButton').pack(side=tk.LEFT)
    
    def create_form_buttons(self, parent):
        """Create form action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=20, column=0, columnspan=2, pady=(20, 0), sticky=tk.W)
        
        # Save button
        self.save_btn = ttk.Button(button_frame,
                                  text="💾 Save",
                                  command=self.save_profile,
                                  style='Primary.TButton')
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Cancel button
        self.cancel_btn = ttk.Button(button_frame,
                                    text="❌ Cancel",
                                    command=self.cancel_edit,
                                    style='Secondary.TButton')
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Edit button
        self.edit_btn = ttk.Button(button_frame,
                                  text="✏️ Edit",
                                  command=self.edit_profile,
                                  style='Secondary.TButton')
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete button
        self.delete_btn = ttk.Button(button_frame,
                                    text="🗑️ Delete",
                                    command=self.delete_profile,
                                    style='Accent.TButton')
        self.delete_btn.pack(side=tk.LEFT)
    
    def set_form_state(self, state):
        """Set form state (view, edit, new)"""
        self.form_state = state
        
        if state == 'view':
            # Disable all form fields
            self.name_entry.config(state='readonly')
            self.customer_combo.config(state='disabled')
            self.watch_entry.config(state='readonly')
            self.status_combo.config(state='disabled')
            self.online_check.config(state='disabled')
            self.picture_entry.config(state='readonly')
            
            # Show/hide buttons
            self.save_btn.pack_forget()
            self.cancel_btn.pack_forget()
            self.edit_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.delete_btn.pack(side=tk.LEFT)
            
        elif state in ['edit', 'new']:
            # Enable form fields
            self.name_entry.config(state='normal')
            self.customer_combo.config(state='readonly')
            self.watch_entry.config(state='normal')
            self.status_combo.config(state='readonly')
            self.online_check.config(state='normal')
            self.picture_entry.config(state='normal')
            
            # Show/hide buttons
            self.edit_btn.pack_forget()
            self.delete_btn.pack_forget()
            self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.cancel_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    def load_customers_data(self):
        """Load customers data for dropdown"""
        try:
            self.customers_data = self.db_manager.get_customers()
            
            # Update customer filter
            customer_names = ['All Customers']
            customer_combo_values = ['Select Customer']
            
            for customer in self.customers_data:
                full_name = f"{customer['firstname']} {customer['lastname']} (ID: {customer['customerid']})"
                customer_names.append(full_name)
                customer_combo_values.append(full_name)
            
            self.customer_filter.config(values=customer_names)
            self.customer_combo.config(values=customer_combo_values)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        for var in self.form_vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set('')
        
        # Set default values for new profile
        self.form_vars['account_status'].set('Active')
        self.form_vars['isOnline'].set(True)
        self.picture_label.config(text="📷\nNo Picture")
    
    def load_profile_to_form(self, profile):
        """Load profile data to form"""
        self.form_vars['profileID'].set(str(profile['profileid']))
        self.form_vars['profileName'].set(profile['profilename'] or '')
        self.form_vars['WatchHistoryID'].set(str(profile['watchhistoryid']) if profile['watchhistoryid'] else '')
        self.form_vars['account_status'].set(profile['account_status'] or 'Active')
        self.form_vars['isOnline'].set(bool(profile['isonline']))
        self.form_vars['profilePicture'].set(profile['profilepicture'] or '')
        
        # Set customer selection
        customer_text = f"{profile['firstname']} {profile['lastname']} (ID: {profile['customerid']})"
        self.customer_combo.set(customer_text)
        
        # Update picture preview
        self.update_picture_preview()
    
    def update_picture_preview(self):
        """Update picture preview"""
        picture_path = self.form_vars['profilePicture'].get()
        if picture_path and os.path.exists(picture_path):
            self.picture_label.config(text=f"📷\n{os.path.basename(picture_path)}")
        else:
            self.picture_label.config(text="📷\nNo Picture")
    
    def validate_form(self):
        """Validate form data"""
        errors = []
        
        # Required fields
        if not self.form_vars['profileName'].get().strip():
            errors.append("Profile name is required")
        
        if self.customer_combo.get() == 'Select Customer':
            errors.append("Please select a customer")
        
        if not self.form_vars['WatchHistoryID'].get().strip():
            errors.append("Watch History ID is required")
        
        # Validate Watch History ID is numeric
        try:
            int(self.form_vars['WatchHistoryID'].get())
        except ValueError:
            errors.append("Watch History ID must be a number")
        
        return errors
    
    def refresh_profile_list(self):
        """Refresh profile list from database"""
        try:
            # Build filters
            search_term = self.search_var.get().strip()
            customer_filter = self.customer_filter.get()
            status_filter = self.status_filter.get()
            online_filter = self.online_filter.get()
            
            # Get profiles with filters
            self.profiles_data = self.get_filtered_profiles(
                search_term, customer_filter, status_filter, online_filter
            )
            
            # Update treeview
            self.update_profile_tree()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profiles: {str(e)}")
    
    def get_filtered_profiles(self, search_term, customer_filter, status_filter, online_filter):
        """Get filtered profiles from database"""
        query = """
            SELECT p.profileID, p.profileName, p.profilePicture, p.isOnline,
                   p.customerID, p.WatchHistoryID, p.account_status,
                   c.firstName, c.lastName
            FROM Profile p
            JOIN Customer c ON p.customerID = c.customerID
            WHERE 1=1
        """
        
        params = []
        
        # Add search filter
        if search_term:
            query += " AND (p.profileName ILIKE %s OR c.firstName ILIKE %s OR c.lastName ILIKE %s)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        # Add customer filter
        if customer_filter and customer_filter != 'All Customers':
            # Extract customer ID from filter text
            try:
                customer_id = int(customer_filter.split('ID: ')[1].split(')')[0])
                query += " AND p.customerID = %s"
                params.append(customer_id)
            except:
                pass
        
        # Add status filter
        if status_filter and status_filter != 'All':
            query += " AND p.account_status = %s"
            params.append(status_filter)
        
        # Add online filter
        if online_filter and online_filter != 'All':
            is_online = online_filter == 'Online'
            query += " AND p.isOnline = %s"
            params.append(is_online)
        
        query += " ORDER BY p.profileID"
        
        return self.db_manager.execute_query(query, params) or []
    
    def update_profile_tree(self):
        """Update profile treeview with current data"""
        # Clear existing items
        for item in self.profile_tree.get_children():
            self.profile_tree.delete(item)
        
        # Add profiles to tree
        for profile in self.profiles_data:
            customer_name = f"{profile['firstname']} {profile['lastname']}"
            online_status = "🟢 Online" if profile['isonline'] else "🔴 Offline"
            
            values = (
                profile['profileid'],
                profile['profilename'],
                customer_name,
                profile['account_status'] or 'Active',
                online_status,
                profile['watchhistoryid'] or 'N/A'
            )
            
            self.profile_tree.insert('', 'end', values=values)
    
    # Event handlers
    def on_search_change(self, *args):
        """Handle search text change"""
        self.refresh_profile_list()
    
    def on_profile_select(self, event):
        """Handle profile selection in tree"""
        selection = self.profile_tree.selection()
        if selection:
            item = self.profile_tree.item(selection[0])
            profile_id = item['values'][0]
            
            # Find profile in current data
            self.selected_profile = None
            for profile in self.profiles_data:
                if profile['profileid'] == profile_id:
                    self.selected_profile = profile
                    break
            
            if self.selected_profile:
                self.load_profile_to_form(self.selected_profile)
                self.set_form_state('view')
    
    def browse_picture(self):
        """Browse for profile picture"""
        file_types = [
            ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp'),
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=file_types,
            initialdir=self.profile_pics_dir
        )
        
        if filename:
            self.form_vars['profilePicture'].set(filename)
            self.update_picture_preview()
    
    def remove_picture(self):
        """Remove profile picture"""
        self.form_vars['profilePicture'].set('')
        self.update_picture_preview()
    
    # CRUD operations
    def new_profile(self):
        """Start creating new profile"""
        self.selected_profile = None
        self.clear_form()
        
        # Set new profile ID
        next_id = self.db_manager.get_next_id('Profile', 'profileID')
        self.form_vars['profileID'].set(str(next_id))
        
        # Set new watch history ID
        next_watch_id = self.db_manager.get_next_id('WatchHistory', 'WatchHistoryID')
        self.form_vars['WatchHistoryID'].set(str(next_watch_id))
        
        self.set_form_state('new')
        self.name_entry.focus()
    
    def edit_profile(self):
        """Start editing selected profile"""
        if not self.selected_profile:
            messagebox.showwarning("Warning", "Please select a profile to edit")
            return
        
        self.set_form_state('edit')
        self.name_entry.focus()
    
    def save_profile(self):
        """Save profile (create or update)"""
        # Validate form
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        try:
            # Get customer ID from selection
            customer_text = self.customer_combo.get()
            customer_id = int(customer_text.split('ID: ')[1].split(')')[0])
            
            # Prepare profile data
            profile_data = {
                'profileName': self.form_vars['profileName'].get().strip(),
                'profilePicture': self.form_vars['profilePicture'].get() or 'default_avatar.png',
                'isOnline': self.form_vars['isOnline'].get(),
                'customerID': customer_id,
                'WatchHistoryID': int(self.form_vars['WatchHistoryID'].get()),
                'account_status': self.form_vars['account_status'].get()
            }
            
            if self.form_state == 'new':
                # Create new profile
                profile_data['profileID'] = int(self.form_vars['profileID'].get())
                
                # First create watch history record if it doesn't exist
                self.create_watch_history_if_needed(profile_data['WatchHistoryID'])
                
                result = self.db_manager.create_profile(profile_data)
                
                if result:
                    messagebox.showinfo("Success", "Profile created successfully!")
                    self.refresh_profile_list()
                    self.set_form_state('view')
                else:
                    messagebox.showerror("Error", "Failed to create profile")
                    
            elif self.form_state == 'edit':
                # Update existing profile
                profile_id = int(self.form_vars['profileID'].get())
                result = self.db_manager.update_profile(profile_id, profile_data)
                
                if result:
                    messagebox.showinfo("Success", "Profile updated successfully!")
                    self.refresh_profile_list()
                    self.set_form_state('view')
                else:
                    messagebox.showerror("Error", "Failed to update profile")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")
    
    def create_watch_history_if_needed(self, watch_history_id):
        """Create watch history record if it doesn't exist"""
        try:
            # Check if watch history exists
            check_query = "SELECT COUNT(*) FROM WatchHistory WHERE WatchHistoryID = %s"
            result = self.db_manager.execute_query(check_query, (watch_history_id,))
            
            if result and result[0][0] == 0:
                # Create dummy watch history record
                create_query = """
                    INSERT INTO WatchHistory (WatchHistoryID, movieID, watchDate, durationWatched)
                    VALUES (%s, 1, CURRENT_DATE, 0)
                """
                self.db_manager.execute_query(create_query, (watch_history_id,), fetch=False)
                
        except Exception as e:
            print(f"Error creating watch history: {str(e)}")
    
    def cancel_edit(self):
        """Cancel editing"""
        if self.selected_profile:
            self.load_profile_to_form(self.selected_profile)
            self.set_form_state('view')
        else:
            self.clear_form()
            self.set_form_state('view')
    
    def delete_profile(self):
        """Delete selected profile"""
        if not self.selected_profile:
            messagebox.showwarning("Warning", "Please select a profile to delete")
            return
        
        profile_name = self.selected_profile['profilename']
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete profile '{profile_name}'?\n\n"
                              "This will also delete all associated reviews and favorites."):
            try:
                profile_id = self.selected_profile['profileid']
                result = self.db_manager.delete_profile(profile_id)
                
                if result:
                    messagebox.showinfo("Success", "Profile deleted successfully!")
                    self.clear_form()
                    self.selected_profile = None
                    self.refresh_profile_list()
                    self.set_form_state('view')
                else:
                    messagebox.showerror("Error", "Failed to delete profile")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete profile: {str(e)}")
    
    # Context menu actions
    def edit_selected_profile(self):
        """Edit profile from context menu"""
        self.edit_profile()
    
    def delete_selected_profile(self):
        """Delete profile from context menu"""
        self.delete_profile()
    
    def toggle_online_status(self):
        """Toggle online status of selected profile"""
        if not self.selected_profile:
            messagebox.showwarning("Warning", "Please select a profile")
            return
        
        try:
            profile_id = self.selected_profile['profileid']
            new_status = not self.selected_profile['isonline']
            
            query = "UPDATE Profile SET isOnline = %s WHERE profileID = %s"
            result = self.db_manager.execute_query(query, (new_status, profile_id), fetch=False)
            
            if result:
                status_text = "online" if new_status else "offline"
                messagebox.showinfo("Success", f"Profile is now {status_text}")
                self.refresh_profile_list()
            else:
                messagebox.showerror("Error", "Failed to update online status")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle online status: {str(e)}")
    
    def view_watch_history(self):
        """View watch history for selected profile"""
        if not self.selected_profile:
            messagebox.showwarning("Warning", "Please select a profile")
            return
        
        # This would navigate to watch history management with profile filter
        messagebox.showinfo("Info", "Navigate to Watch History Management to view profile's viewing history")
    
    def view_profile_reviews(self):
        """View reviews made by selected profile"""
        if not self.selected_profile:
            messagebox.showwarning("Warning", "Please select a profile")
            return
        
        try:
            profile_id = self.selected_profile['profileid']
            
            # Get profile reviews
            query = """
                SELECT r.movieID, r.rating, r.comment, r.reviewDate,
                       t.Title_Name
                FROM Reviews r
                LEFT JOIN Title t ON r.movieID = t.Title_ID
                WHERE r.profileID = %s
                ORDER BY r.reviewDate DESC
            """
            
            reviews = self.db_manager.execute_query(query, (profile_id,))
            
            # Create popup window
            popup = tk.Toplevel()
            popup.title(f"Reviews by {self.selected_profile['profilename']}")
            popup.geometry("700x400")
            popup.transient(self.parent_frame)
            
            # Create treeview for reviews
            columns = ('Movie ID', 'Title', 'Rating', 'Comment', 'Date')
            review_tree = ttk.Treeview(popup, columns=columns, show='headings')
            
            # Configure columns
            for col in columns:
                review_tree.heading(col, text=col)
            
            review_tree.column('Movie ID', width=80, anchor=tk.CENTER)
            review_tree.column('Title', width=200, anchor=tk.W)
            review_tree.column('Rating', width=60, anchor=tk.CENTER)
            review_tree.column('Comment', width=250, anchor=tk.W)
            review_tree.column('Date', width=100, anchor=tk.CENTER)
            
            # Add reviews
            for review in reviews or []:
                review_tree.insert('', 'end', values=(
                    review['movieid'],
                    review['title_name'] or 'Unknown',
                    f"{review['rating']}/5" if review['rating'] else 'N/A',
                    review['comment'][:50] + '...' if len(review['comment'] or '') > 50 else review['comment'] or '',
                    review['reviewdate'].strftime('%Y-%m-%d') if review['reviewdate'] else 'N/A'
                ))
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(popup, orient="vertical", command=review_tree.yview)
            review_tree.configure(yscrollcommand=scrollbar.set)
            
            # Pack widgets
            review_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)
            
            # Close button
            ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load reviews: {str(e)}")
    
    def show_profile_statistics(self):
        """Show profile statistics"""
        try:
            # Get statistics
            stats_query = """
                SELECT 
                    COUNT(*) as total_profiles,
                    COUNT(CASE WHEN isOnline = true THEN 1 END) as online_profiles,
                    COUNT(CASE WHEN account_status = 'Active' THEN 1 END) as active_profiles,
                    COUNT(DISTINCT customerID) as unique_customers
                FROM Profile
            """
            
            stats = self.db_manager.execute_query(stats_query)
            
            if stats:
                stat = stats[0]
                stats_text = f"""
Profile Statistics:

Total Profiles: {stat[0]}
Online Profiles: {stat[1]}
Active Profiles: {stat[2]}
Unique Customers: {stat[3]}
                """
                
                messagebox.showinfo("Profile Statistics", stats_text.strip())
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {str(e)}")
          
