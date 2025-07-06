"""
Watch History Management Screen for Streaming Service Management System
מסך ניהול היסטוריית צפייה למערכת ניהול שירותי סטרימינג

Provides CRUD operations for WatchHistory table (linking table between profiles and content)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class WatchHistoryManagement:
    """
    Watch History management class for CRUD operations on WatchHistory table
    """
    
    def __init__(self, parent_frame, db_manager, colors):
        """
        Initialize watch history management
        
        Args:
            parent_frame: Parent frame for watch history management
            db_manager: Database manager instance
            colors: Color scheme dictionary
        """
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.colors = colors
        
        # Current data
        self.watch_history_data = []
        self.titles_data = []
        self.profiles_data = []
        self.selected_record = None
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        # Form variables
        self.form_vars = {}
        
        # Date filters
        self.date_from = None
        self.date_to = None
        
        # Pagination
        self.current_page = 1
        self.items_per_page = 100
        self.total_pages = 1
    
    def create_interface(self):
        """Create watch history management interface"""
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
        
        # Watch history list (top)
        self.create_watch_history_list(content_frame)
        
        # Bottom section with form and analytics
        bottom_frame = ttk.Frame(content_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Watch history form (left)
        self.create_watch_history_form(bottom_frame)
        
        # Analytics (right)
        self.create_analytics_section(bottom_frame)
        
        # Load initial data
        self.load_reference_data()
        self.refresh_watch_history_list()
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame,
                               text="📺 Watch History Management",
                               font=('Arial', 16, 'bold'),
                               foreground=self.colors['primary'])
        title_label.pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame,
                  text="➕ Record Viewing",
                  command=self.new_watch_record,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="🔄 Refresh",
                  command=self.refresh_watch_history_list,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="📊 Analytics",
                  command=self.show_detailed_analytics,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="📤 Export",
                  command=self.export_watch_history,
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
        
        # Date range filter
        ttk.Label(search_frame, text="From:").pack(side=tk.LEFT)
        
        self.date_from_entry = DateEntry(search_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, 
                                        date_pattern='yyyy-mm-dd')
        self.date_from_entry.set_date(date.today() - timedelta(days=30))
        self.date_from_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.date_from_entry.bind('<<DateEntrySelected>>', lambda e: self.refresh_watch_history_list())
        
        ttk.Label(search_frame, text="To:").pack(side=tk.LEFT)
        
        self.date_to_entry = DateEntry(search_frame, width=12, background='darkblue',
                                      foreground='white', borderwidth=2,
                                      date_pattern='yyyy-mm-dd')
        self.date_to_entry.set_date(date.today())
        self.date_to_entry.pack(side=tk.LEFT, padx=(5, 20))
        self.date_to_entry.bind('<<DateEntrySelected>>', lambda e: self.refresh_watch_history_list())
        
        # Filter by viewing category
        ttk.Label(search_frame, text="Category:").pack(side=tk.LEFT)
        
        self.category_filter = ttk.Combobox(search_frame,
                                           values=['All', 'Regular', 'Binge', 'Sample', 'Rewatch'],
                                           state='readonly',
                                           width=12)
        self.category_filter.set('All')
        self.category_filter.pack(side=tk.LEFT, padx=(5, 20))
        self.category_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_watch_history_list())
        
        # Filter by completion
        ttk.Label(search_frame, text="Completion:").pack(side=tk.LEFT)
        
        self.completion_filter = ttk.Combobox(search_frame,
                                             values=['All', 'Complete (>80%)', 'Partial (20-80%)', 'Sample (<20%)'],
                                             state='readonly',
                                             width=15)
        self.completion_filter.set('All')
        self.completion_filter.pack(side=tk.LEFT, padx=(5, 0))
        self.completion_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_watch_history_list())
    
    def create_watch_history_list(self, parent):
        """Create watch history list section"""
        # Frame for watch history list
        list_frame = ttk.LabelFrame(parent, text="Watch History Records", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 0))
        
        # Treeview for watch history
        columns = ('ID', 'Date', 'Profile', 'Customer', 'Content', 'Duration', 'Completion', 'Category')
        self.watch_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.watch_tree.heading('ID', text='Watch ID')
        self.watch_tree.heading('Date', text='Watch Date')
        self.watch_tree.heading('Profile', text='Profile')
        self.watch_tree.heading('Customer', text='Customer')
        self.watch_tree.heading('Content', text='Content Title')
        self.watch_tree.heading('Duration', text='Duration (min)')
        self.watch_tree.heading('Completion', text='Completion %')
        self.watch_tree.heading('Category', text='Category')
        
        self.watch_tree.column('ID', width=80, anchor=tk.CENTER)
        self.watch_tree.column('Date', width=100, anchor=tk.CENTER)
        self.watch_tree.column('Profile', width=120, anchor=tk.W)
        self.watch_tree.column('Customer', width=120, anchor=tk.W)
        self.watch_tree.column('Content', width=200, anchor=tk.W)
        self.watch_tree.column('Duration', width=100, anchor=tk.CENTER)
        self.watch_tree.column('Completion', width=100, anchor=tk.CENTER)
        self.watch_tree.column('Category', width=100, anchor=tk.CENTER)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.watch_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.watch_tree.xview)
        self.watch_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.watch_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.watch_tree.bind('<<TreeviewSelect>>', self.on_watch_select)
        
        # Context menu
        self.create_context_menu()
        self.watch_tree.bind('<Button-3>', self.show_context_menu)
        
        # Pagination frame
        pagination_frame = ttk.Frame(list_frame)
        pagination_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.create_pagination_controls(pagination_frame)
    
    def create_context_menu(self):
        """Create context menu for watch history list"""
        self.context_menu = tk.Menu(self.watch_tree, tearoff=0)
        self.context_menu.add_command(label="Edit Record", command=self.edit_selected_record)
        self.context_menu.add_command(label="View Content Details", command=self.view_content_details)
        self.context_menu.add_command(label="View Profile Details", command=self.view_profile_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Mark as Rewatch", command=self.mark_as_rewatch)
        self.context_menu.add_command(label="Delete Record", command=self.delete_selected_record)
    
    def show_context_menu(self, event):
        """Show context menu"""
        if self.watch_tree.selection():
            self.context_menu.post(event.x_root, event.y_root)
    
    def create_pagination_controls(self, parent):
        """Create pagination controls"""
        # Previous button
        self.prev_btn = ttk.Button(parent,
                                  text="◀ Previous",
                                  command=self.previous_page,
                                  state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT)
        
        # Page info
        self.page_label = ttk.Label(parent, text="Page 1 of 1")
        self.page_label.pack(side=tk.LEFT, padx=(10, 10))
        
        # Next button
        self.next_btn = ttk.Button(parent,
                                  text="Next ▶",
                                  command=self.next_page,
                                  state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT)
        
        # Items per page
        ttk.Label(parent, text="Items per page:").pack(side=tk.RIGHT, padx=(20, 5))
        
        items_combo = ttk.Combobox(parent,
                                  values=[50, 100, 200, 500],
                                  width=8,
                                  state='readonly')
        items_combo.set(self.items_per_page)
        items_combo.pack(side=tk.RIGHT)
        items_combo.bind('<<ComboboxSelected>>', self.on_items_per_page_change)
    
    def create_watch_history_form(self, parent):
        """Create watch history form section"""
        # Left frame for form
        form_frame = ttk.LabelFrame(parent, text="Watch Record Details", padding="15")
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Form fields
        self.create_form_fields(form_frame)
        
        # Form buttons
        self.create_form_buttons(form_frame)
        
        # Set initial state
        self.set_form_state('view')
    
    def create_form_fields(self, parent):
        """Create form input fields"""
        # Initialize form variables
        self.form_vars = {
            'WatchHistoryID': tk.StringVar(),
            'movieID': tk.StringVar(),
            'watchDate': tk.StringVar(),
            'durationWatched': tk.StringVar(),
            'completion_percentage': tk.StringVar(),
            'viewing_category': tk.StringVar(),
            'profileID': tk.StringVar()
        }
        
        # Watch History ID (readonly)
        row = 0
        ttk.Label(parent, text="Watch ID:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.id_entry = ttk.Entry(parent, textvariable=self.form_vars['WatchHistoryID'], 
                                 state='readonly', width=25)
        self.id_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Profile Selection
        row += 1
        ttk.Label(parent, text="*Profile:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.profile_combo = ttk.Combobox(parent,
                                         state='readonly',
                                         width=22)
        self.profile_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Content Selection
        row += 1
        ttk.Label(parent, text="*Content:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.content_combo = ttk.Combobox(parent,
                                         textvariable=self.form_vars['movieID'],
                                         state='readonly',
                                         width=22)
        self.content_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Watch Date
        row += 1
        ttk.Label(parent, text="*Watch Date:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.date_entry = DateEntry(parent, width=20, background='darkblue',
                                   foreground='white', borderwidth=2, 
                                   date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Duration Watched
        row += 1
        ttk.Label(parent, text="*Duration (min):").grid(row=row, column=0, sticky=tk.W, pady=5)
        duration_frame = ttk.Frame(parent)
        duration_frame.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        self.duration_entry = ttk.Entry(duration_frame, textvariable=self.form_vars['durationWatched'], width=12)
        self.duration_entry.pack(side=tk.LEFT)
        
        # Auto-calculate button
        ttk.Button(duration_frame,
                  text="📊",
                  command=self.auto_calculate_completion,
                  width=3).pack(side=tk.LEFT, padx=(5, 0))
        
        # Completion Percentage
        row += 1
        ttk.Label(parent, text="Completion %:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.completion_entry = ttk.Entry(parent, textvariable=self.form_vars['completion_percentage'], width=25)
        self.completion_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Viewing Category
        row += 1
        ttk.Label(parent, text="Category:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.category_combo = ttk.Combobox(parent,
                                          textvariable=self.form_vars['viewing_category'],
                                          values=['Regular', 'Binge', 'Sample', 'Rewatch'],
                                          state='readonly',
                                          width=22)
        self.category_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Required fields note
        row += 1
        note_label = ttk.Label(parent, text="* Required fields", font=('Arial', 8), foreground='red')
        note_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def create_form_buttons(self, parent):
        """Create form action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=20, column=0, columnspan=2, pady=(20, 0), sticky=tk.W)
        
        # Save button
        self.save_btn = ttk.Button(button_frame,
                                  text="💾 Save",
                                  command=self.save_watch_record,
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
                                  command=self.edit_watch_record,
                                  style='Secondary.TButton')
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete button
        self.delete_btn = ttk.Button(button_frame,
                                    text="🗑️ Delete",
                                    command=self.delete_watch_record,
                                    style='Accent.TButton')
        self.delete_btn.pack(side=tk.LEFT)
    
    def create_analytics_section(self, parent):
        """Create analytics section"""
        # Right frame for analytics
        analytics_frame = ttk.LabelFrame(parent, text="Viewing Analytics", padding="10")
        analytics_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Analytics tabs
        analytics_notebook = ttk.Notebook(analytics_frame)
        analytics_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        summary_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(summary_frame, text="📊 Summary")
        self.create_summary_analytics(summary_frame)
        
        # Charts tab
        charts_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(charts_frame, text="📈 Charts")
        self.create_charts_analytics(charts_frame)
        
        # Trends tab
        trends_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(trends_frame, text="📉 Trends")
        self.create_trends_analytics(trends_frame)
    
    def create_summary_analytics(self, parent):
        """Create summary analytics"""
        # Statistics cards
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create statistics labels
        self.stats_labels = {}
        
        # Row 1
        row1_frame = ttk.Frame(stats_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.stats_labels['total_records'] = self.create_stat_card(
            row1_frame, "📺 Total Records", "0", self.colors['primary'], "left")
        self.stats_labels['total_hours'] = self.create_stat_card(
            row1_frame, "⏱️ Total Hours", "0h", self.colors['secondary'], "left")
        
        # Row 2
        row2_frame = ttk.Frame(stats_frame)
        row2_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.stats_labels['avg_duration'] = self.create_stat_card(
            row2_frame, "📊 Avg Duration", "0 min", self.colors['warning'], "left")
        self.stats_labels['completion_rate'] = self.create_stat_card(
            row2_frame, "✅ Completion Rate", "0%", self.colors['success'], "left")
        
        # Top content section
        top_content_frame = ttk.LabelFrame(parent, text="🏆 Top Content", padding="10")
        top_content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top content treeview
        top_columns = ('Rank', 'Title', 'Views', 'Avg Duration')
        self.top_content_tree = ttk.Treeview(top_content_frame, columns=top_columns, 
                                           show='headings', height=8)
        
        for col in top_columns:
            self.top_content_tree.heading(col, text=col)
            self.top_content_tree.column(col, width=100, anchor=tk.CENTER)
        
        self.top_content_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_stat_card(self, parent, title, value, color, side):
        """Create individual statistics card"""
        card_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1, padding=(10, 5))
        card_frame.pack(side=side, fill=tk.BOTH, expand=True, padx=(0, 5) if side == "left" else (0, 0))
        
        # Title
        title_label = ttk.Label(card_frame, text=title, font=('Arial', 9), 
                               foreground=self.colors['dark'])
        title_label.pack(anchor=tk.W)
        
        # Value
        value_label = ttk.Label(card_frame, text=value, font=('Arial', 14, 'bold'), 
                               foreground=color)
        value_label.pack(anchor=tk.W)
        
        return value_label
    
    def create_charts_analytics(self, parent):
        """Create charts analytics"""
        # Matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.fig.patch.set_facecolor('white')
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial empty charts
        self.update_charts()
    
    def create_trends_analytics(self, parent):
        """Create trends analytics"""
        trends_text = tk.Text(parent, height=15, width=50, wrap=tk.WORD, state=tk.DISABLED)
        trends_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=trends_text.yview)
        trends_text.configure(yscrollcommand=trends_scrollbar.set)
        
        trends_text.pack(side="left", fill="both", expand=True)
        trends_scrollbar.pack(side="right", fill="y")
        
        self.trends_text = trends_text
    
    def set_form_state(self, state):
        """Set form state (view, edit, new)"""
        self.form_state = state
        
        if state == 'view':
            # Disable all form fields
            self.profile_combo.config(state='disabled')
            self.content_combo.config(state='disabled')
            self.date_entry.config(state='disabled')
            self.duration_entry.config(state='readonly')
            self.completion_entry.config(state='readonly')
            self.category_combo.config(state='disabled')
            
            # Show/hide buttons
            self.save_btn.pack_forget()
            self.cancel_btn.pack_forget()
            self.edit_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.delete_btn.pack(side=tk.LEFT)
            
        elif state in ['edit', 'new']:
            # Enable form fields
            self.profile_combo.config(state='readonly')
            self.content_combo.config(state='readonly')
            self.date_entry.config(state='normal')
            self.duration_entry.config(state='normal')
            self.completion_entry.config(state='normal')
            self.category_combo.config(state='readonly')
            
            # Show/hide buttons
            self.edit_btn.pack_forget()
            self.delete_btn.pack_forget()
            self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.cancel_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    def load_reference_data(self):
        """Load reference data for dropdowns"""
        try:
            # Load profiles
            self.profiles_data = self.db_manager.get_profiles()
            profile_values = []
            for profile in self.profiles_data:
                profile_text = f"{profile['profilename']} - {profile['firstname']} {profile['lastname']} (ID: {profile['profileid']})"
                profile_values.append(profile_text)
            self.profile_combo.config(values=profile_values)
            
            # Load titles/content
            titles_query = "SELECT Title_ID, Title_Name FROM Title ORDER BY Title_Name"
            self.titles_data = self.db_manager.execute_query(titles_query) or []
            title_values = []
            for title in self.titles_data:
                title_text = f"{title['title_name']} (ID: {title['title_id']})"
                title_values.append(title_text)
            self.content_combo.config(values=title_values)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load reference data: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        for var in self.form_vars.values():
            var.set('')
        
        # Set default values
        self.date_entry.set_date(date.today())
        self.form_vars['viewing_category'].set('Regular')
        self.form_vars['completion_percentage'].set('0.0')
    
    def load_watch_record_to_form(self, record):
        """Load watch record data to form"""
        self.form_vars['WatchHistoryID'].set(str(record['watchhistoryid']))
        self.form_vars['movieID'].set(str(record['movieid']) if record['movieid'] else '')
        self.form_vars['durationWatched'].set(str(record['durationwatched']) if record['durationwatched'] else '0')
        self.form_vars['completion_percentage'].set(str(record['completion_percentage']) if record['completion_percentage'] else '0')
        self.form_vars['viewing_category'].set(record['viewing_category'] or 'Regular')
        
        # Set date
        if record['watchdate']:
            self.date_entry.set_date(record['watchdate'])
        
        # Set profile selection
        if record.get('profilename'):
            profile_text = f"{record['profilename']} - {record['firstname']} {record['lastname']} (ID: {record.get('profileid', 'N/A')})"
            self.profile_combo.set(profile_text)
        
        # Set content selection
        if record.get('title_name'):
            content_text = f"{record['title_name']} (ID: {record['movieid']})"
            self.content_combo.set(content_text)
    
    def validate_form(self):
        """Validate form data"""
        errors = []
        
        # Required fields
        if not self.profile_combo.get():
            errors.append("Please select a profile")
        
        if not self.content_combo.get():
            errors.append("Please select content")
        
        if not self.form_vars['durationWatched'].get().strip():
            errors.append("Duration is required")
        
        # Validate duration is numeric and positive
        try:
            duration = float(self.form_vars['durationWatched'].get())
            if duration < 0:
                errors.append("Duration must be positive")
        except ValueError:
            errors.append("Duration must be a valid number")
        
        # Validate completion percentage
        try:
            completion = float(self.form_vars['completion_percentage'].get() or 0)
            if completion < 0 or completion > 100:
                errors.append("Completion percentage must be between 0 and 100")
        except ValueError:
            errors.append("Completion percentage must be a valid number")
        
        return errors
    
    def auto_calculate_completion(self):
        """Auto-calculate completion percentage based on content duration"""
        try:
            # Get selected content
            content_text = self.content_combo.get()
            if not content_text:
                messagebox.showinfo("Info", "Please select content first")
                return
            
            # Extract content ID
            content_id = int(content_text.split('(ID: ')[1].split(')')[0])
            
            # Get content duration
            duration_query = """
                SELECT m.Duration 
                FROM Movie m 
                JOIN Title t ON m.Title_ID = t.Title_ID 
                WHERE t.Title_ID = %s
            """
            result = self.db_manager.execute_query(duration_query, (content_id,))
            
            if result and result[0]['duration']:
                content_duration = result[0]['duration']
                watched_duration = float(self.form_vars['durationWatched'].get() or 0)
                
                if content_duration > 0:
                    completion = min(100, (watched_duration / content_duration) * 100)
                    self.form_vars['completion_percentage'].set(f"{completion:.1f}")
                else:
                    messagebox.showinfo("Info", "Content duration not available")
            else:
                messagebox.showinfo("Info", "This might be a TV show. Completion calculated as percentage of episode.")
                # For TV shows, assume 45 minute episodes
                watched_duration = float(self.form_vars['durationWatched'].get() or 0)
                completion = min(100, (watched_duration / 45) * 100)
                self.form_vars['completion_percentage'].set(f"{completion:.1f}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate completion: {str(e)}")
    
    def refresh_watch_history_list(self):
        """Refresh watch history list from database"""
        try:
            # Build filters
            search_term = self.search_var.get().strip()
            date_from = self.date_from_entry.get_date()
            date_to = self.date_to_entry.get_date()
            category_filter = self.category_filter.get()
            completion_filter = self.completion_filter.get()
            
            # Calculate offset
            offset = (self.current_page - 1) * self.items_per_page
            
            # Get watch history with filters
            self.watch_history_data = self.get_filtered_watch_history(
                search_term, date_from, date_to, category_filter, completion_filter,
                limit=self.items_per_page, offset=offset
            )
            
            # Update treeview
            self.update_watch_history_tree()
            
            # Update pagination
            self.update_pagination()
            
            # Update analytics
            self.update_analytics()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load watch history: {str(e)}")
    
    def get_filtered_watch_history(self, search_term, date_from, date_to, category_filter, 
                                  completion_filter, limit=None, offset=None):
        """Get filtered watch history from database"""
        query = """
            SELECT wh.WatchHistoryID, wh.movieID, wh.watchDate, wh.durationWatched,
                   wh.completion_percentage, wh.viewing_category,
                   t.Title_Name, p.profileName, p.profileID,
                   c.firstName, c.lastName
            FROM WatchHistory wh
            LEFT JOIN Title t ON wh.movieID = t.Title_ID
            LEFT JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID
            LEFT JOIN Customer c ON p.customerID = c.customerID
            WHERE wh.watchDate BETWEEN %s AND %s
        """
        
        params = [date_from, date_to]
        
        # Add search filter
        if search_term:
            query += " AND (t.Title_Name ILIKE %s OR p.profileName ILIKE %s OR c.firstName ILIKE %s OR c.lastName ILIKE %s)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
        
        # Add category filter
        if category_filter and category_filter != 'All':
            query += " AND wh.viewing_category = %s"
            params.append(category_filter)
        
        # Add completion filter
        if completion_filter and completion_filter != 'All':
            if completion_filter == 'Complete (>80%)':
                query += " AND wh.completion_percentage > 80"
            elif completion_filter == 'Partial (20-80%)':
                query += " AND wh.completion_percentage BETWEEN 20 AND 80"
            elif completion_filter == 'Sample (<20%)':
                query += " AND wh.completion_percentage < 20"
        
        query += " ORDER BY wh.watchDate DESC"
        
        # Add pagination
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        if offset:
            query += " OFFSET %s"
            params.append(offset)
        
        return self.db_manager.execute_query(query, params) or []
    
    def update_watch_history_tree(self):
        """Update watch history treeview with current data"""
        # Clear existing items
        for item in self.watch_tree.get_children():
            self.watch_tree.delete(item)
        
        # Add records to tree
        for record in self.watch_history_data:
            # Format data
            watch_date = record['watchdate'].strftime('%Y-%m-%d') if record['watchdate'] else 'N/A'
            profile_name = record['profilename'] or 'Unknown'
            customer_name = f"{record['firstname']} {record['lastname']}" if record['firstname'] else 'Unknown'
            content_title = record['title_name'] or 'Unknown Content'
            duration = f"{record['durationwatched']:.1f}" if record['durationwatched'] else '0.0'
            completion = f"{record['completion_percentage']:.1f}%" if record['completion_percentage'] else '0.0%'
            category = record['viewing_category'] or 'Regular'
            
            values = (
                record['watchhistoryid'],
                watch_date,
                profile_name,
                customer_name,
                content_title,
                duration,
                completion,
                category
            )
            
            self.watch_tree.insert('', 'end', values=values)
    
    def update_pagination(self):
        """Update pagination controls"""
        # Calculate total pages
        total_records = self.get_total_watch_history_count()
        self.total_pages = max(1, (total_records + self.items_per_page - 1) // self.items_per_page)
        
        # Update page label
        self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")
        
        # Update button states
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)
    
    def get_total_watch_history_count(self):
        """Get total count of watch history records with current filters"""
        try:
            search_term = self.search_var.get().strip()
            date_from = self.date_from_entry.get_date()
            date_to = self.date_to_entry.get_date()
            category_filter = self.category_filter.get()
            completion_filter = self.completion_filter.get()
            
            query = """
                SELECT COUNT(*)
                FROM WatchHistory wh
                LEFT JOIN Title t ON wh.movieID = t.Title_ID
                LEFT JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID
                LEFT JOIN Customer c ON p.customerID = c.customerID
                WHERE wh.watchDate BETWEEN %s AND %s
            """
            
            params = [date_from, date_to]
            
            # Add filters (same as in get_filtered_watch_history)
            if search_term:
                query += " AND (t.Title_Name ILIKE %s OR p.profileName ILIKE %s OR c.firstName ILIKE %s OR c.lastName ILIKE %s)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
            
            if category_filter and category_filter != 'All':
                query += " AND wh.viewing_category = %s"
                params.append(category_filter)
            
            if completion_filter and completion_filter != 'All':
                if completion_filter == 'Complete (>80%)':
                    query += " AND wh.completion_percentage > 80"
                elif completion_filter == 'Partial (20-80%)':
                    query += " AND wh.completion_percentage BETWEEN 20 AND 80"
                elif completion_filter == 'Sample (<20%)':
                    query += " AND wh.completion_percentage < 20"
            
            result = self.db_manager.execute_query(query, params)
            return result[0][0] if result else 0
            
        except Exception as e:
            print(f"Error getting watch history count: {str(e)}")
            return 0
    
    def update_analytics(self):
        """Update analytics data"""
        try:
            # Get analytics data
            analytics_data = self.get_analytics_data()
            
            # Update summary statistics
            self.stats_labels['total_records'].config(text=str(analytics_data['total_records']))
            self.stats_labels['total_hours'].config(text=f"{analytics_data['total_hours']:.1f}h")
            self.stats_labels['avg_duration'].config(text=f"{analytics_data['avg_duration']:.1f} min")
            self.stats_labels['completion_rate'].config(text=f"{analytics_data['completion_rate']:.1f}%")
            
            # Update top content
            self.update_top_content(analytics_data['top_content'])
            
            # Update charts
            self.update_charts()
            
            # Update trends
            self.update_trends()
            
        except Exception as e:
            print(f"Error updating analytics: {str(e)}")
    
    def get_analytics_data(self):
        """Get analytics data from database"""
        try:
            date_from = self.date_from_entry.get_date()
            date_to = self.date_to_entry.get_date()
            
            # Basic statistics
            stats_query = """
                SELECT 
                    COUNT(*) as total_records,
                    COALESCE(SUM(durationWatched), 0) / 60.0 as total_hours,
                    COALESCE(AVG(durationWatched), 0) as avg_duration,
                    COALESCE(AVG(completion_percentage), 0) as completion_rate
                FROM WatchHistory
                WHERE watchDate BETWEEN %s AND %s
            """
            
            stats = self.db_manager.execute_query(stats_query, (date_from, date_to))
            
            # Top content
            top_content_query = """
                SELECT 
                    t.Title_Name,
                    COUNT(*) as view_count,
                    AVG(wh.durationWatched) as avg_duration
                FROM WatchHistory wh
                LEFT JOIN Title t ON wh.movieID = t.Title_ID
                WHERE wh.watchDate BETWEEN %s AND %s
                GROUP BY t.Title_Name, t.Title_ID
                ORDER BY view_count DESC
                LIMIT 10
            """
            
            top_content = self.db_manager.execute_query(top_content_query, (date_from, date_to))
            
            return {
                'total_records': stats[0][0] if stats else 0,
                'total_hours': stats[0][1] if stats else 0,
                'avg_duration': stats[0][2] if stats else 0,
                'completion_rate': stats[0][3] if stats else 0,
                'top_content': top_content or []
            }
            
        except Exception as e:
            print(f"Error getting analytics data: {str(e)}")
            return {
                'total_records': 0, 'total_hours': 0, 'avg_duration': 0, 
                'completion_rate': 0, 'top_content': []
            }
    
    def update_top_content(self, top_content_data):
        """Update top content tree"""
        # Clear existing items
        for item in self.top_content_tree.get_children():
            self.top_content_tree.delete(item)
        
        # Add top content
        for i, content in enumerate(top_content_data[:10], 1):
            values = (
                i,
                content['title_name'] or 'Unknown',
                content['view_count'],
                f"{content['avg_duration']:.1f} min" if content['avg_duration'] else '0 min'
            )
            self.top_content_tree.insert('', 'end', values=values)
    
    def update_charts(self):
        """Update analytics charts"""
        try:
            # Clear previous charts
            self.ax1.clear()
            self.ax2.clear()
            
            # Get chart data
            date_from = self.date_from_entry.get_date()
            date_to = self.date_to_entry.get_date()
            
            # Chart 1: Daily viewing hours
            daily_query = """
                SELECT 
                    DATE(watchDate) as watch_day,
                    SUM(durationWatched) / 60.0 as total_hours
                FROM WatchHistory
                WHERE watchDate BETWEEN %s AND %s
                GROUP BY DATE(watchDate)
                ORDER BY watch_day
            """
            
            daily_data = self.db_manager.execute_query(daily_query, (date_from, date_to))
            
            if daily_data:
                days = [str(row[0]) for row in daily_data]
                hours = [row[1] for row in daily_data]
                
                self.ax1.plot(days, hours, marker='o', linewidth=2, markersize=4)
                self.ax1.set_title('Daily Viewing Hours', fontsize=10, fontweight='bold')
                self.ax1.set_ylabel('Hours')
                self.ax1.tick_params(axis='x', rotation=45, labelsize=8)
                self.ax1.grid(True, alpha=0.3)
            
            # Chart 2: Completion rate distribution
            completion_query = """
                SELECT 
                    CASE 
                        WHEN completion_percentage >= 80 THEN 'Complete (80%+)'
                        WHEN completion_percentage >= 50 THEN 'Mostly (50-80%)'
                        WHEN completion_percentage >= 20 THEN 'Partial (20-50%)'
                        ELSE 'Sample (<20%)'
                    END as completion_category,
                    COUNT(*) as count
                FROM WatchHistory
                WHERE watchDate BETWEEN %s AND %s
                GROUP BY completion_category
            """
            
            completion_data = self.db_manager.execute_query(completion_query, (date_from, date_to))
            
            if completion_data:
                categories = [row[0] for row in completion_data]
                counts = [row[1] for row in completion_data]
                
                colors = ['#27AE60', '#F39C12', '#E74C3C', '#95A5A6']
                self.ax2.pie(counts, labels=categories, autopct='%1.1f%%', 
                           colors=colors[:len(categories)], startangle=90)
                self.ax2.set_title('Viewing Completion Distribution', fontsize=10, fontweight='bold')
            
            # Adjust layout and refresh
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating charts: {str(e)}")
    
    def update_trends(self):
        """Update trends analysis"""
        try:
            date_from = self.date_from_entry.get_date()
            date_to = self.date_to_entry.get_date()
            
            # Get trends data
            trends_query = """
                SELECT 
                    viewing_category,
                    COUNT(*) as total_views,
                    AVG(durationWatched) as avg_duration,
                    AVG(completion_percentage) as avg_completion
                FROM WatchHistory
                WHERE watchDate BETWEEN %s AND %s
                GROUP BY viewing_category
                ORDER BY total_views DESC
            """
            
            trends_data = self.db_manager.execute_query(trends_query, (date_from, date_to))
            
            # Format trends text
            trends_text = f"📈 VIEWING TRENDS ANALYSIS\\n"
            trends_text += f"Period: {date_from} to {date_to}\\n\\n"
            
            if trends_data:
                for trend in trends_data:
                    category = trend[0] or 'Unknown'
                    total_views = trend[1]
                    avg_duration = trend[2] or 0
                    avg_completion = trend[3] or 0
                    
                    trends_text += f"🔸 {category.upper()}:\\n"
                    trends_text += f"   Views: {total_views}\\n"
                    trends_text += f"   Avg Duration: {avg_duration:.1f} min\\n"
                    trends_text += f"   Avg Completion: {avg_completion:.1f}%\\n\\n"
            else:
                trends_text += "No data available for the selected period.\\n"
            
            # Update trends text widget
            self.trends_text.config(state=tk.NORMAL)
            self.trends_text.delete(1.0, tk.END)
            self.trends_text.insert(1.0, trends_text)
            self.trends_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error updating trends: {str(e)}")
    
    # Event handlers
    def on_search_change(self, *args):
        """Handle search text change"""
        self.current_page = 1
        self.refresh_watch_history_list()
    
    def on_watch_select(self, event):
        """Handle watch record selection in tree"""
        selection = self.watch_tree.selection()
        if selection:
            item = self.watch_tree.item(selection[0])
            watch_id = item['values'][0]
            
            # Find record in current data
            self.selected_record = None
            for record in self.watch_history_data:
                if record['watchhistoryid'] == watch_id:
                    self.selected_record = record
                    break
            
            if self.selected_record:
                self.load_watch_record_to_form(self.selected_record)
                self.set_form_state('view')
    
    def on_items_per_page_change(self, event):
        """Handle items per page change"""
        self.items_per_page = int(event.widget.get())
        self.current_page = 1
        self.refresh_watch_history_list()
    
    # Navigation methods
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_watch_history_list()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.refresh_watch_history_list()
    
    # CRUD operations
    def new_watch_record(self):
        """Start creating new watch record"""
        self.selected_record = None
        self.clear_form()
        
        # Set new watch history ID
        next_id = self.db_manager.get_next_id('WatchHistory', 'WatchHistoryID')
        self.form_vars['WatchHistoryID'].set(str(next_id))
        
        self.set_form_state('new')
        self.profile_combo.focus()
    
    def edit_watch_record(self):
        """Start editing selected watch record"""
        if not self.selected_record:
            messagebox.showwarning("Warning", "Please select a watch record to edit")
            return
        
        self.set_form_state('edit')
        self.duration_entry.focus()
    
    def save_watch_record(self):
        """Save watch record (create or update)"""
        # Validate form
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Validation Error", "\\n".join(errors))
            return
        
        try:
            # Extract IDs from combo selections
            profile_text = self.profile_combo.get()
            profile_id = int(profile_text.split('(ID: ')[1].split(')')[0])
            
            content_text = self.content_combo.get()
            content_id = int(content_text.split('(ID: ')[1].split(')')[0])
            
            # Prepare watch record data
            watch_data = {
                'movieID': content_id,
                'watchDate': self.date_entry.get_date(),
                'durationWatched': float(self.form_vars['durationWatched'].get()),
                'completion_percentage': float(self.form_vars['completion_percentage'].get() or 0),
                'viewing_category': self.form_vars['viewing_category'].get()
            }
            
            if self.form_state == 'new':
                # Create new watch record
                watch_data['WatchHistoryID'] = int(self.form_vars['WatchHistoryID'].get())
                result = self.db_manager.create_watch_history(watch_data)
                
                if result:
                    messagebox.showinfo("Success", "Watch record created successfully!")
                    self.refresh_watch_history_list()
                    self.set_form_state('view')
                else:
                    messagebox.showerror("Error", "Failed to create watch record")
                    
            elif self.form_state == 'edit':
                # Update existing watch record
                watch_id = int(self.form_vars['WatchHistoryID'].get())
                result = self.db_manager.update_watch_history(watch_id, watch_data)
                
                if result:
                    messagebox.showinfo("Success", "Watch record updated successfully!")
                    self.refresh_watch_history_list()
                    self.set_form_state('view')
                else:
                    messagebox.showerror("Error", "Failed to update watch record")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save watch record: {str(e)}")
    
    def cancel_edit(self):
        """Cancel editing"""
        if self.selected_record:
            self.load_watch_record_to_form(self.selected_record)
            self.set_form_state('view')
        else:
            self.clear_form()
            self.set_form_state('view')
    
    def delete_watch_record(self):
        """Delete selected watch record"""
        if not self.selected_record:
            messagebox.showwarning("Warning", "Please select a watch record to delete")
            return
        
        watch_id = self.selected_record['watchhistoryid']
        content_title = self.selected_record.get('title_name', 'Unknown')
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete this watch record?\\n\\n"
                              f"Content: {content_title}\\n"
                              f"Watch ID: {watch_id}"):
            try:
                result = self.db_manager.delete_watch_history(watch_id)
                
                if result:
                    messagebox.showinfo("Success", "Watch record deleted successfully!")
                    self.clear_form()
                    self.selected_record = None
                    self.refresh_watch_history_list()
                    self.set_form_state('view')
                else:
                    messagebox.showerror("Error", "Failed to delete watch record")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete watch record: {str(e)}")
    
    # Context menu actions
    def edit_selected_record(self):
        """Edit record from context menu"""
        self.edit_watch_record()
    
    def delete_selected_record(self):
        """Delete record from context menu"""
        self.delete_watch_record()
    
    def mark_as_rewatch(self):
        """Mark selected record as rewatch"""
        if not self.selected_record:
            messagebox.showwarning("Warning", "Please select a watch record")
            return
        
        try:
            watch_id = self.selected_record['watchhistoryid']
            query = "UPDATE WatchHistory SET viewing_category = 'Rewatch' WHERE WatchHistoryID = %s"
            result = self.db_manager.execute_query(query, (watch_id,), fetch=False)
            
            if result:
                messagebox.showinfo("Success", "Record marked as rewatch")
                self.refresh_watch_history_list()
            else:
                messagebox.showerror("Error", "Failed to update record")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark as rewatch: {str(e)}")
    
    def view_content_details(self):
        """View content details for selected record"""
        if not self.selected_record:
            messagebox.showwarning("Warning", "Please select a watch record")
            return
        
        content_title = self.selected_record.get('title_name', 'Unknown')
        content_id = self.selected_record.get('movieid', 'Unknown')
        
        messagebox.showinfo("Content Details", 
                           f"Content: {content_title}\\n"
                           f"Content ID: {content_id}\\n\\n"
                           "Full content details would be shown here.")
    
    def view_profile_details(self):
        """View profile details for selected record"""
        if not self.selected_record:
            messagebox.showwarning("Warning", "Please select a watch record")
            return
        
        profile_name = self.selected_record.get('profilename', 'Unknown')
        customer_name = f"{self.selected_record.get('firstname', '')} {self.selected_record.get('lastname', '')}"
        
        messagebox.showinfo("Profile Details", 
                           f"Profile: {profile_name}\\n"
                           f"Customer: {customer_name}\\n\\n"
                           "Full profile details would be shown here.")
    
    def show_detailed_analytics(self):
        """Show detailed analytics in popup window"""
        try:
            # Create popup window
            popup = tk.Toplevel()
            popup.title("Detailed Analytics")
            popup.geometry("800x600")
            popup.transient(self.parent_frame)
            
            # Create notebook for different analytics
            notebook = ttk.Notebook(popup)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Content performance tab
            content_frame = ttk.Frame(notebook)
            notebook.add(content_frame, text="Content Performance")
            
            # User behavior tab
            behavior_frame = ttk.Frame(notebook)
            notebook.add(behavior_frame, text="User Behavior")
            
            # Time analysis tab
            time_frame = ttk.Frame(notebook)
            notebook.add(time_frame, text="Time Analysis")
            
            # TODO: Implement detailed analytics views
            ttk.Label(content_frame, text="Detailed content performance analytics would be shown here").pack(pady=50)
            ttk.Label(behavior_frame, text="User behavior analytics would be shown here").pack(pady=50)
            ttk.Label(time_frame, text="Time-based analytics would be shown here").pack(pady=50)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show detailed analytics: {str(e)}")
    
    def export_watch_history(self):
        """Export watch history data"""
        try:
            from tkinter import filedialog
            import csv
            
            # Get filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Watch History"
            )
            
            if filename:
                # Export current filtered data
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow(['Watch ID', 'Date', 'Profile', 'Customer', 'Content', 
                                   'Duration (min)', 'Completion %', 'Category'])
                    
                    # Write data
                    for record in self.watch_history_data:
                        writer.writerow([
                            record['watchhistoryid'],
                            record['watchdate'].strftime('%Y-%m-%d') if record['watchdate'] else '',
                            record['profilename'] or '',
                            f"{record['firstname']} {record['lastname']}" if record['firstname'] else '',
                            record['title_name'] or '',
                            record['durationwatched'] or 0,
                            record['completion_percentage'] or 0,
                            record['viewing_category'] or ''
                        ])
                
                messagebox.showinfo("Success", f"Watch history exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
          
