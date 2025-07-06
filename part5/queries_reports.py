"""
Queries and Reports Screen for Streaming Service Management System
מסך שאילתות ודוחות למערכת ניהול שירותי סטרימינג

Executes predefined queries from Stage 2 and generates reports
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
import csv
import json
from tkcalendar import DateEntry

class QueriesReports:
    """
    Queries and Reports class for executing predefined queries and generating reports
    """
    
    def __init__(self, parent_frame, db_manager, colors):
        """
        Initialize queries and reports
        
        Args:
            parent_frame: Parent frame for queries and reports
            db_manager: Database manager instance
            colors: Color scheme dictionary
        """
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.colors = colors
        
        # Current query results
        self.current_results = []
        self.current_query_name = ""
        
        # Predefined queries from Stage 2
        self.predefined_queries = {
            "viewing_history_2024": {
                "name": "All profiles with viewing history in 2024, including customer name",
                "description": "Shows all profiles that watched content in 2024 with customer details",
                "sql": """
                    SELECT DISTINCT p.profileID, p.profileName, 
                           c.firstName || ' ' || c.lastName as customer_name,
                           wh.watchDate, t.Title_Name, wh.durationWatched
                    FROM Profile p
                    JOIN Customer c ON p.customerID = c.customerID
                    JOIN WatchHistory wh ON p.WatchHistoryID = wh.WatchHistoryID
                    LEFT JOIN Title t ON wh.movieID = t.Title_ID
                    WHERE EXTRACT(YEAR FROM wh.watchDate) = 2024
                    ORDER BY wh.watchDate DESC, p.profileName
                """,
                "columns": ["Profile ID", "Profile Name", "Customer Name", "Watch Date", "Title", "Duration (min)"]
            },
            
            "favorites_avg_time": {
                "name": "Average viewing time for favorite movies",
                "description": "Calculates average viewing time for content marked as favorites",
                "sql": """
                    SELECT f.movieID, t.Title_Name, f.totalTimeWatched,
                           COUNT(maf.profileID) as times_favorited,
                           f.totalTimeWatched / GREATEST(COUNT(maf.profileID), 1) as avg_time_per_user
                    FROM Favorites f
                    LEFT JOIN Title t ON f.movieID = t.Title_ID
                    LEFT JOIN MarksAsFavorite maf ON f.movieID = maf.movieID
                    GROUP BY f.movieID, t.Title_Name, f.totalTimeWatched
                    ORDER BY avg_time_per_user DESC
                """,
                "columns": ["Movie ID", "Title", "Total Time Watched", "Times Favorited", "Avg Time Per User"]
            },
            
            "payments_over_200": {
                "name": "Payment details of customers who paid over 200 NIS in the last year",
                "description": "Shows customers with high payment amounts in the last year",
                "sql": """
                    SELECT c.customerID, c.firstName, c.lastName, 
                           SUM(p.amount) as total_paid,
                           COUNT(p.paymentID) as payment_count,
                           AVG(p.amount) as avg_payment
                    FROM Customer c
                    JOIN Payment p ON c.customerID = p.customerID
                    WHERE p.paymentDate >= CURRENT_DATE - INTERVAL '1 year'
                    GROUP BY c.customerID, c.firstName, c.lastName
                    HAVING SUM(p.amount) > 200
                    ORDER BY total_paid DESC
                """,
                "columns": ["Customer ID", "First Name", "Last Name", "Total Paid", "Payment Count", "Avg Payment"]
            },
            
            "customers_multiple_devices": {
                "name": "Customers with more than two registered devices",
                "description": "Identifies customers with multiple devices for usage analysis",
                "sql": """
                    SELECT c.customerID, c.firstName, c.lastName,
                           COUNT(d.deviceID) as device_count,
                           STRING_AGG(d.deviceName, ', ') as device_names,
                           STRING_AGG(d.deviceType, ', ') as device_types
                    FROM Customer c
                    JOIN Devices d ON c.customerID = d.customerID
                    GROUP BY c.customerID, c.firstName, c.lastName
                    HAVING COUNT(d.deviceID) > 2
                    ORDER BY device_count DESC, c.lastName
                """,
                "columns": ["Customer ID", "First Name", "Last Name", "Device Count", "Device Names", "Device Types"]
            },
            
            "low_rated_favorites": {
                "name": "Profiles that added a favorite movie rated less than 3",
                "description": "Shows profiles with low-rated favorites (potential data quality issues)",
                "sql": """
                    SELECT p.profileID, p.profileName, 
                           c.firstName || ' ' || c.lastName as customer_name,
                           r.movieID, t.Title_Name, r.rating
                    FROM Profile p
                    JOIN Customer c ON p.customerID = c.customerID
                    JOIN MarksAsFavorite maf ON p.profileID = maf.profileID
                    JOIN Reviews r ON maf.movieID = r.movieID AND r.profileID = p.profileID
                    LEFT JOIN Title t ON r.movieID = t.Title_ID
                    WHERE r.rating < 3
                    ORDER BY r.rating ASC, p.profileName
                """,
                "columns": ["Profile ID", "Profile Name", "Customer Name", "Movie ID", "Title", "Rating"]
            },
            
            "october_watching": {
                "name": "All movies watched in October including duration",
                "description": "Shows all content watched during October with viewing details",
                "sql": """
                    SELECT wh.WatchHistoryID, p.profileName,
                           c.firstName || ' ' || c.lastName as customer_name,
                           t.Title_Name, wh.watchDate, wh.durationWatched,
                           wh.completion_percentage, wh.viewing_category
                    FROM WatchHistory wh
                    LEFT JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID
                    LEFT JOIN Customer c ON p.customerID = c.customerID
                    LEFT JOIN Title t ON wh.movieID = t.Title_ID
                    WHERE EXTRACT(MONTH FROM wh.watchDate) = 10
                    ORDER BY wh.watchDate DESC, wh.durationWatched DESC
                """,
                "columns": ["Watch ID", "Profile", "Customer", "Title", "Watch Date", "Duration", "Completion %", "Category"]
            },
            
            "no_payments_this_year": {
                "name": "Customers who have not made any payments this year",
                "description": "Identifies customers without recent payments (potential churn risk)",
                "sql": """
                    SELECT c.customerID, c.firstName, c.lastName,
                           c.customerSince, c.subscription_type, c.payment_status,
                           MAX(p.paymentDate) as last_payment_date
                    FROM Customer c
                    LEFT JOIN Payment p ON c.customerID = p.customerID
                    WHERE c.customerID NOT IN (
                        SELECT DISTINCT customerID 
                        FROM Payment 
                        WHERE EXTRACT(YEAR FROM paymentDate) = EXTRACT(YEAR FROM CURRENT_DATE)
                    )
                    GROUP BY c.customerID, c.firstName, c.lastName, 
                             c.customerSince, c.subscription_type, c.payment_status
                    ORDER BY c.customerSince DESC
                """,
                "columns": ["Customer ID", "First Name", "Last Name", "Customer Since", "Subscription", "Payment Status", "Last Payment"]
            },
            
            "monthly_viewing_trends": {
                "name": "Average viewing times by month",
                "description": "Shows viewing trends across different months",
                "sql": """
                    SELECT EXTRACT(YEAR FROM wh.watchDate) as year,
                           EXTRACT(MONTH FROM wh.watchDate) as month,
                           TO_CHAR(wh.watchDate, 'YYYY-MM') as year_month,
                           COUNT(*) as total_sessions,
                           AVG(wh.durationWatched) as avg_duration,
                           SUM(wh.durationWatched) / 60.0 as total_hours,
                           COUNT(DISTINCT p.profileID) as unique_viewers
                    FROM WatchHistory wh
                    LEFT JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID
                    WHERE wh.watchDate >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY EXTRACT(YEAR FROM wh.watchDate), EXTRACT(MONTH FROM wh.watchDate), TO_CHAR(wh.watchDate, 'YYYY-MM')
                    ORDER BY year DESC, month DESC
                """,
                "columns": ["Year", "Month", "Year-Month", "Total Sessions", "Avg Duration", "Total Hours", "Unique Viewers"]
            }
        }
    
    def create_interface(self):
        """Create queries and reports interface"""
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Content area with notebook tabs
        content_notebook = ttk.Notebook(main_container)
        content_notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Predefined Queries tab
        queries_frame = ttk.Frame(content_notebook)
        content_notebook.add(queries_frame, text="📊 Predefined Queries")
        self.create_predefined_queries_tab(queries_frame)
        
        # Custom Queries tab
        custom_frame = ttk.Frame(content_notebook)
        content_notebook.add(custom_frame, text="🔧 Custom Queries")
        self.create_custom_queries_tab(custom_frame)
        
        # Reports tab
        reports_frame = ttk.Frame(content_notebook)
        content_notebook.add(reports_frame, text="📈 Reports")
        self.create_reports_tab(reports_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame,
                               text="📊 Queries & Reports",
                               font=('Arial', 16, 'bold'),
                               foreground=self.colors['primary'])
        title_label.pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame,
                  text="📤 Export Results",
                  command=self.export_results,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="🔄 Clear Results",
                  command=self.clear_results,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="📋 Query History",
                  command=self.show_query_history,
                  style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, pady=(5, 0))
    
    def create_predefined_queries_tab(self, parent):
        """Create predefined queries tab"""
        # Split into left (queries list) and right (results)
        paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - queries list
        queries_frame = ttk.LabelFrame(paned_window, text="Available Queries", padding="10")
        paned_window.add(queries_frame, weight=1)
        
        # Queries listbox with descriptions
        queries_list_frame = ttk.Frame(queries_frame)
        queries_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for queries
        query_columns = ('Query', 'Description')
        self.queries_tree = ttk.Treeview(queries_list_frame, columns=query_columns, show='headings', height=8)
        
        self.queries_tree.heading('Query', text='Query Name')
        self.queries_tree.heading('Description', text='Description')
        
        self.queries_tree.column('Query', width=200, anchor=tk.W)
        self.queries_tree.column('Description', width=300, anchor=tk.W)
        
        # Populate queries tree
        for query_id, query_info in self.predefined_queries.items():
            self.queries_tree.insert('', 'end', iid=query_id, values=(
                query_info['name'],
                query_info['description']
            ))
        
        # Scrollbar for queries tree
        queries_scrollbar = ttk.Scrollbar(queries_list_frame, orient="vertical", command=self.queries_tree.yview)
        self.queries_tree.configure(yscrollcommand=queries_scrollbar.set)
        
        # Pack queries tree
        self.queries_tree.pack(side="left", fill="both", expand=True)
        queries_scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.queries_tree.bind('<<TreeviewSelect>>', self.on_query_select)
        
        # Query action buttons
        query_buttons_frame = ttk.Frame(queries_frame)
        query_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(query_buttons_frame,
                  text="▶️ Execute Query",
                  command=self.execute_selected_query,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(query_buttons_frame,
                  text="👁️ View SQL",
                  command=self.view_query_sql,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(query_buttons_frame,
                  text="📊 Analyze Results",
                  command=self.analyze_results,
                  style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Right side - results area
        results_frame = ttk.LabelFrame(paned_window, text="Query Results", padding="10")
        paned_window.add(results_frame, weight=2)
        
        self.create_results_area(results_frame)
    
    def create_custom_queries_tab(self, parent):
        """Create custom queries tab"""
        # Split into top (query editor) and bottom (results)
        custom_paned = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        custom_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top - Query editor
        editor_frame = ttk.LabelFrame(custom_paned, text="SQL Query Editor", padding="10")
        custom_paned.add(editor_frame, weight=1)
        
        # Query text area
        query_text_frame = ttk.Frame(editor_frame)
        query_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.custom_query_text = tk.Text(query_text_frame, height=10, width=80, 
                                        font=('Consolas', 10), wrap=tk.NONE)
        
        # Scrollbars for text area
        custom_v_scroll = ttk.Scrollbar(query_text_frame, orient="vertical", command=self.custom_query_text.yview)
        custom_h_scroll = ttk.Scrollbar(query_text_frame, orient="horizontal", command=self.custom_query_text.xview)
        self.custom_query_text.configure(yscrollcommand=custom_v_scroll.set, xscrollcommand=custom_h_scroll.set)
        
        # Pack text area and scrollbars
        self.custom_query_text.grid(row=0, column=0, sticky="nsew")
        custom_v_scroll.grid(row=0, column=1, sticky="ns")
        custom_h_scroll.grid(row=1, column=0, sticky="ew")
        
        query_text_frame.grid_rowconfigure(0, weight=1)
        query_text_frame.grid_columnconfigure(0, weight=1)
        
        # Query editor buttons
        editor_buttons_frame = ttk.Frame(editor_frame)
        editor_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(editor_buttons_frame,
                  text="▶️ Execute",
                  command=self.execute_custom_query,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(editor_buttons_frame,
                  text="💾 Save Query",
                  command=self.save_custom_query,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(editor_buttons_frame,
                  text="📂 Load Query",
                  command=self.load_custom_query,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(editor_buttons_frame,
                  text="🔍 Validate SQL",
                  command=self.validate_sql,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(editor_buttons_frame,
                  text="❌ Clear",
                  command=self.clear_custom_query,
                  style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Add placeholder text
        placeholder_text = """-- Enter your SQL query here
-- Example:
SELECT c.firstName, c.lastName, COUNT(p.profileID) as profile_count
FROM Customer c
LEFT JOIN Profile p ON c.customerID = p.customerID
GROUP BY c.customerID, c.firstName, c.lastName
ORDER BY profile_count DESC;"""
        
        self.custom_query_text.insert(1.0, placeholder_text)
        
        # Bottom - Results
        custom_results_frame = ttk.LabelFrame(custom_paned, text="Custom Query Results", padding="10")
        custom_paned.add(custom_results_frame, weight=1)
        
        self.create_results_area(custom_results_frame, "custom")
    
    def create_reports_tab(self, parent):
        """Create reports tab"""
        # Reports configuration frame
        config_frame = ttk.LabelFrame(parent, text="Report Configuration", padding="15")
        config_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Report type selection
        ttk.Label(config_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.report_type = ttk.Combobox(config_frame,
                                       values=['Customer Summary', 'Content Performance', 
                                              'Viewing Analytics', 'Revenue Report', 
                                              'User Engagement', 'System Health'],
                                       state='readonly',
                                       width=20)
        self.report_type.set('Customer Summary')
        self.report_type.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 20))
        
        # Date range
        ttk.Label(config_frame, text="Date Range:").grid(row=0, column=2, sticky=tk.W, pady=5)
        
        date_frame = ttk.Frame(config_frame)
        date_frame.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(10, 0))
        
        self.report_date_from = DateEntry(date_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.report_date_from.set_date(date.today() - timedelta(days=30))
        self.report_date_from.pack(side=tk.LEFT)
        
        ttk.Label(date_frame, text=" to ").pack(side=tk.LEFT)
        
        self.report_date_to = DateEntry(date_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.report_date_to.set_date(date.today())
        self.report_date_to.pack(side=tk.LEFT)
        
        # Report generation buttons
        report_buttons_frame = ttk.Frame(config_frame)
        report_buttons_frame.grid(row=1, column=0, columnspan=4, pady=(15, 0))
        
        ttk.Button(report_buttons_frame,
                  text="📊 Generate Report",
                  command=self.generate_report,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(report_buttons_frame,
                  text="📧 Email Report",
                  command=self.email_report,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(report_buttons_frame,
                  text="📅 Schedule Report",
                  command=self.schedule_report,
                  style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Report results area
        report_results_frame = ttk.LabelFrame(parent, text="Generated Report", padding="10")
        report_results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.create_results_area(report_results_frame, "report")
    
    def create_results_area(self, parent, area_type="default"):
        """Create results display area"""
        # Results info frame
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Results count and query name
        if area_type == "default":
            self.results_info_label = ttk.Label(info_frame, text="No query executed", 
                                               font=('Arial', 10, 'bold'))
        elif area_type == "custom":
            self.custom_results_info_label = ttk.Label(info_frame, text="No custom query executed", 
                                                      font=('Arial', 10, 'bold'))
        else:
            self.report_results_info_label = ttk.Label(info_frame, text="No report generated", 
                                                      font=('Arial', 10, 'bold'))
        
        if area_type == "default":
            self.results_info_label.pack(side=tk.LEFT)
        elif area_type == "custom":
            self.custom_results_info_label.pack(side=tk.LEFT)
        else:
            self.report_results_info_label.pack(side=tk.LEFT)
        
        # Execution time
        if area_type == "default":
            self.execution_time_label = ttk.Label(info_frame, text="", foreground=self.colors['dark'])
            self.execution_time_label.pack(side=tk.RIGHT)
        
        # Results treeview
        results_tree_frame = ttk.Frame(parent)
        results_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview (will be configured dynamically)
        if area_type == "default":
            self.results_tree = ttk.Treeview(results_tree_frame, show='headings', height=15)
        elif area_type == "custom":
            self.custom_results_tree = ttk.Treeview(results_tree_frame, show='headings', height=10)
        else:
            self.report_results_tree = ttk.Treeview(results_tree_frame, show='headings', height=12)
        
        # Scrollbars
        if area_type == "default":
            tree_widget = self.results_tree
        elif area_type == "custom":
            tree_widget = self.custom_results_tree
        else:
            tree_widget = self.report_results_tree
        
        v_scrollbar = ttk.Scrollbar(results_tree_frame, orient="vertical", command=tree_widget.yview)
        h_scrollbar = ttk.Scrollbar(results_tree_frame, orient="horizontal", command=tree_widget.xview)
        tree_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        tree_widget.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        results_tree_frame.grid_rowconfigure(0, weight=1)
        results_tree_frame.grid_columnconfigure(0, weight=1)
    
    def on_query_select(self, event):
        """Handle query selection from predefined queries list"""
        selection = self.queries_tree.selection()
        if selection:
            self.selected_query_id = selection[0]
    
    def execute_selected_query(self):
        """Execute the selected predefined query"""
        try:
            if not hasattr(self, 'selected_query_id'):
                messagebox.showwarning("Warning", "Please select a query to execute")
                return
            
            query_info = self.predefined_queries[self.selected_query_id]
            
            # Execute query with timing
            start_time = datetime.now()
            
            results = self.db_manager.execute_query(query_info['sql'])
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Store results
            self.current_results = results or []
            self.current_query_name = query_info['name']
            
            # Update results display
            self.display_query_results(query_info['columns'], self.current_results, execution_time)
            
            # Update info label
            self.results_info_label.config(
                text=f"Query: {query_info['name']} | Results: {len(self.current_results)} rows"
            )
            self.execution_time_label.config(text=f"Execution time: {execution_time:.3f}s")
            
        except Exception as e:
            messagebox.showerror("Query Error", f"Failed to execute query:\n\n{str(e)}")
    
    def display_query_results(self, columns, results, execution_time=None, tree_widget=None):
        """Display query results in treeview"""
        if tree_widget is None:
            tree_widget = self.results_tree
        
        # Clear existing results
        for item in tree_widget.get_children():
            tree_widget.delete(item)
        
        if not results:
            return
        
        # Configure columns
        tree_widget['columns'] = columns
        
        for col in columns:
            tree_widget.heading(col, text=col)
            tree_widget.column(col, width=150, anchor=tk.W)
        
        # Add results
        for row in results:
            # Convert row to list of strings
            if isinstance(row, dict):
                values = [str(row.get(col.lower().replace(' ', '').replace('(', '').replace(')', ''), '') or '') for col in columns]
            else:
                values = [str(val) if val is not None else '' for val in row]
            
            tree_widget.insert('', 'end', values=values)
    
    def view_query_sql(self):
        """View SQL of selected query"""
        try:
            if not hasattr(self, 'selected_query_id'):
                messagebox.showwarning("Warning", "Please select a query")
                return
            
            query_info = self.predefined_queries[self.selected_query_id]
            
            # Create popup window to show SQL
            popup = tk.Toplevel()
            popup.title(f"SQL Query - {query_info['name']}")
            popup.geometry("800x500")
            popup.transient(self.parent_frame)
            
            # SQL text area
            sql_frame = ttk.Frame(popup)
            sql_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            sql_text = tk.Text(sql_frame, font=('Consolas', 10), wrap=tk.NONE)
            sql_text.insert(1.0, query_info['sql'])
            sql_text.config(state=tk.DISABLED)
            
            # Scrollbars
            sql_v_scroll = ttk.Scrollbar(sql_frame, orient="vertical", command=sql_text.yview)
            sql_h_scroll = ttk.Scrollbar(sql_frame, orient="horizontal", command=sql_text.xview)
            sql_text.configure(yscrollcommand=sql_v_scroll.set, xscrollcommand=sql_h_scroll.set)
            
            # Pack
            sql_text.grid(row=0, column=0, sticky="nsew")
            sql_v_scroll.grid(row=0, column=1, sticky="ns")
            sql_h_scroll.grid(row=1, column=0, sticky="ew")
            
            sql_frame.grid_rowconfigure(0, weight=1)
            sql_frame.grid_columnconfigure(0, weight=1)
            
            # Buttons
            button_frame = ttk.Frame(popup)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            ttk.Button(button_frame, text="Copy to Clipboard", 
                      command=lambda: self.copy_to_clipboard(query_info['sql'])).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Close", command=popup.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display SQL: {str(e)}")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.parent_frame.clipboard_clear()
        self.parent_frame.clipboard_append(text)
        messagebox.showinfo("Success", "SQL copied to clipboard")
    
    def execute_custom_query(self):
        """Execute custom SQL query"""
        try:
            sql_query = self.custom_query_text.get(1.0, tk.END).strip()
            
            if not sql_query:
                messagebox.showwarning("Warning", "Please enter a SQL query")
                return
            
            # Execute query with timing
            start_time = datetime.now()
            
            # Determine if it's a SELECT query
            is_select = sql_query.upper().strip().startswith('SELECT')
            
            if is_select:
                results = self.db_manager.execute_query(sql_query)
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                if results:
                    # Get column names from first row (if dict) or create generic ones
                    if isinstance(results[0], dict):
                        columns = list(results[0].keys())
                    else:
                        columns = [f"Column_{i+1}" for i in range(len(results[0]))]
                    
                    # Display results
                    self.display_query_results(columns, results, execution_time, self.custom_results_tree)
                    
                    # Update info
                    self.custom_results_info_label.config(
                        text=f"Custom Query Results: {len(results)} rows | Execution time: {execution_time:.3f}s"
                    )
                else:
                    self.custom_results_info_label.config(text="Query executed successfully - No results returned")
                    
            else:
                # Non-SELECT query (INSERT, UPDATE, DELETE, etc.)
                rows_affected = self.db_manager.execute_query(sql_query, fetch=False)
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # Clear results tree
                for item in self.custom_results_tree.get_children():
                    self.custom_results_tree.delete(item)
                
                self.custom_results_info_label.config(
                    text=f"Query executed successfully - {rows_affected} rows affected | Execution time: {execution_time:.3f}s"
                )
                
        except Exception as e:
            messagebox.showerror("Query Error", f"Failed to execute custom query:\n\n{str(e)}")
    
    def validate_sql(self):
        """Validate SQL syntax"""
        try:
            sql_query = self.custom_query_text.get(1.0, tk.END).strip()
            
            if not sql_query:
                messagebox.showwarning("Warning", "Please enter a SQL query")
                return
            
            # Try to prepare/explain the query
            try:
                # Simple validation - try to execute with LIMIT 0
                if sql_query.upper().strip().startswith('SELECT'):
                    validation_query = f"EXPLAIN ({sql_query})"
                    self.db_manager.execute_query(validation_query)
                    messagebox.showinfo("Validation", "✅ SQL syntax is valid")
                else:
                    messagebox.showinfo("Validation", "⚠️ Non-SELECT queries cannot be validated without execution")
                    
            except Exception as e:
                messagebox.showerror("Validation Error", f"❌ SQL syntax error:\n\n{str(e)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to validate SQL: {str(e)}")
    
    def save_custom_query(self):
        """Save custom query to file"""
        try:
            sql_query = self.custom_query_text.get(1.0, tk.END).strip()
            
            if not sql_query:
                messagebox.showwarning("Warning", "No query to save")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".sql",
                filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Save SQL Query"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(sql_query)
                
                messagebox.showinfo("Success", f"Query saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save query: {str(e)}")
    
    def load_custom_query(self):
        """Load custom query from file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Load SQL Query"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    sql_query = f.read()
                
                self.custom_query_text.delete(1.0, tk.END)
                self.custom_query_text.insert(1.0, sql_query)
                
                messagebox.showinfo("Success", f"Query loaded from {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load query: {str(e)}")
    
    def clear_custom_query(self):
        """Clear custom query text area"""
        if messagebox.askyesno("Confirm", "Clear the query editor?"):
            self.custom_query_text.delete(1.0, tk.END)
    
    def generate_report(self):
        """Generate selected report"""
        try:
            report_type = self.report_type.get()
            date_from = self.report_date_from.get_date()
            date_to = self.report_date_to.get_date()
            
            # Get report data based on type
            if report_type == "Customer Summary":
                results, columns = self.generate_customer_summary_report(date_from, date_to)
            elif report_type == "Content Performance":
                results, columns = self.generate_content_performance_report(date_from, date_to)
            elif report_type == "Viewing Analytics":
                results, columns = self.generate_viewing_analytics_report(date_from, date_to)
            elif report_type == "Revenue Report":
                results, columns = self.generate_revenue_report(date_from, date_to)
            elif report_type == "User Engagement":
                results, columns = self.generate_user_engagement_report(date_from, date_to)
            else:  # System Health
                results, columns = self.generate_system_health_report(date_from, date_to)
            
            # Display results
            self.display_query_results(columns, results, tree_widget=self.report_results_tree)
            
            # Update info
            self.report_results_info_label.config(
                text=f"Report: {report_type} | Period: {date_from} to {date_to} | Results: {len(results)} rows"
            )
            
            # Store for export
            self.current_results = results
            self.current_query_name = f"{report_type} Report"
            
        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to generate report:\n\n{str(e)}")
    
    def generate_customer_summary_report(self, date_from, date_to):
        """Generate customer summary report"""
        query = """
            SELECT 
                c.customerID,
                c.firstName || ' ' || c.lastName as customer_name,
                c.subscription_type,
                c.payment_status,
                COUNT(DISTINCT p.profileID) as total_profiles,
                COUNT(DISTINCT wh.WatchHistoryID) as total_viewing_sessions,
                COALESCE(SUM(wh.durationWatched), 0) / 60.0 as total_hours_watched,
                COALESCE(SUM(pay.amount), 0) as total_payments,
                MAX(wh.watchDate) as last_viewing_date
            FROM Customer c
            LEFT JOIN Profile p ON c.customerID = p.customerID
            LEFT JOIN WatchHistory wh ON p.WatchHistoryID = wh.WatchHistoryID 
                AND wh.watchDate BETWEEN %s AND %s
            LEFT JOIN Payment pay ON c.customerID = pay.customerID 
                AND pay.paymentDate BETWEEN %s AND %s
            GROUP BY c.customerID, c.firstName, c.lastName, c.subscription_type, c.payment_status
            ORDER BY total_hours_watched DESC
        """
        
        results = self.db_manager.execute_query(query, (date_from, date_to, date_from, date_to))
        columns = ["Customer ID", "Customer Name", "Subscription", "Payment Status", 
                  "Profiles", "Viewing Sessions", "Hours Watched", "Total Payments", "Last Viewing"]
        
        return results, columns
    
    def generate_content_performance_report(self, date_from, date_to):
        """Generate content performance report"""
        query = """
            SELECT 
                t.Title_ID,
                t.Title_Name,
                COUNT(DISTINCT wh.WatchHistoryID) as total_views,
                COUNT(DISTINCT p.profileID) as unique_viewers,
                AVG(wh.durationWatched) as avg_watch_duration,
                AVG(wh.completion_percentage) as avg_completion_rate,
                COUNT(DISTINCT r.profileID) as total_reviews,
                AVG(r.rating) as avg_rating,
                COUNT(DISTINCT maf.profileID) as times_favorited
            FROM Title t
            LEFT JOIN WatchHistory wh ON t.Title_ID = wh.movieID 
                AND wh.watchDate BETWEEN %s AND %s
            LEFT JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID
            LEFT JOIN Reviews r ON t.Title_ID = r.movieID
            LEFT JOIN MarksAsFavorite maf ON t.Title_ID = maf.movieID
            GROUP BY t.Title_ID, t.Title_Name
            HAVING COUNT(DISTINCT wh.WatchHistoryID) > 0
            ORDER BY total_views DESC
        """
        
        results = self.db_manager.execute_query(query, (date_from, date_to))
        columns = ["Title ID", "Title Name", "Total Views", "Unique Viewers", 
                  "Avg Duration", "Avg Completion %", "Reviews", "Avg Rating", "Times Favorited"]
        
        return results, columns
    
    def generate_viewing_analytics_report(self, date_from, date_to):
        """Generate viewing analytics report"""
        query = """
            SELECT 
                DATE(wh.watchDate) as viewing_date,
                wh.viewing_category,
                COUNT(*) as total_sessions,
                COUNT(DISTINCT p.profileID) as unique_viewers,
                AVG(wh.durationWatched) as avg_duration,
                SUM(wh.durationWatched) / 60.0 as total_hours,
                AVG(wh.completion_percentage) as avg_completion
            FROM WatchHistory wh
            LEFT JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID
            WHERE wh.watchDate BETWEEN %s AND %s
            GROUP BY DATE(wh.watchDate), wh.viewing_category
            ORDER BY viewing_date DESC, wh.viewing_category
        """
        
        results = self.db_manager.execute_query(query, (date_from, date_to))
        columns = ["Date", "Category", "Sessions", "Unique Viewers", 
                  "Avg Duration", "Total Hours", "Avg Completion %"]
        
        return results, columns
    
    def generate_revenue_report(self, date_from, date_to):
        """Generate revenue report"""
        query = """
            SELECT 
                DATE(p.paymentDate) as payment_date,
                p.currency,
                p.paymentMethod,
                p.status,
                COUNT(*) as transaction_count,
                SUM(p.amount) as total_amount,
                AVG(p.amount) as avg_amount,
                COUNT(DISTINCT p.customerID) as unique_customers
            FROM Payment p
            WHERE p.paymentDate BETWEEN %s AND %s
            GROUP BY DATE(p.paymentDate), p.currency, p.paymentMethod, p.status
            ORDER BY payment_date DESC, total_amount DESC
        """
        
        results = self.db_manager.execute_query(query, (date_from, date_to))
        columns = ["Payment Date", "Currency", "Payment Method", "Status", 
                  "Transaction Count", "Total Amount", "Avg Amount", "Unique Customers"]
        
        return results, columns
    
    def generate_user_engagement_report(self, date_from, date_to):
        """Generate user engagement report"""
        query = """
            SELECT 
                p.profileID,
                p.profileName,
                c.firstName || ' ' || c.lastName as customer_name,
                COUNT(DISTINCT wh.WatchHistoryID) as viewing_sessions,
                SUM(wh.durationWatched) / 60.0 as total_hours,
                AVG(wh.completion_percentage) as avg_completion,
                COUNT(DISTINCT r.movieID) as reviews_written,
                COUNT(DISTINCT maf.movieID) as favorites_marked,
                MAX(wh.watchDate) as last_activity
            FROM Profile p
            JOIN Customer c ON p.customerID = c.customerID
            LEFT JOIN WatchHistory wh ON p.WatchHistoryID = wh.WatchHistoryID 
                AND wh.watchDate BETWEEN %s AND %s
            LEFT JOIN Reviews r ON p.profileID = r.profileID
            LEFT JOIN MarksAsFavorite maf ON p.profileID = maf.profileID
            GROUP BY p.profileID, p.profileName, c.firstName, c.lastName
            HAVING COUNT(DISTINCT wh.WatchHistoryID) > 0
            ORDER BY viewing_sessions DESC, total_hours DESC
        """
        
        results = self.db_manager.execute_query(query, (date_from, date_to))
        columns = ["Profile ID", "Profile Name", "Customer", "Sessions", 
                  "Total Hours", "Avg Completion %", "Reviews", "Favorites", "Last Activity"]
        
        return results, columns
    
    def generate_system_health_report(self, date_from, date_to):
        """Generate system health report"""
        query = """
            SELECT 
                'Total Customers' as metric,
                COUNT(*)::text as value,
                'Active customer accounts' as description
            FROM Customer
            WHERE customerSince <= %s
            
            UNION ALL
            
            SELECT 
                'Active Profiles' as metric,
                COUNT(*)::text as value,
                'Profiles with recent activity' as description
            FROM Profile p
            JOIN WatchHistory wh ON p.WatchHistoryID = wh.WatchHistoryID
            WHERE wh.watchDate BETWEEN %s AND %s
            
            UNION ALL
            
            SELECT 
                'Total Viewing Hours' as metric,
                ROUND(SUM(durationWatched) / 60.0, 2)::text as value,
                'Hours watched in period' as description
            FROM WatchHistory
            WHERE watchDate BETWEEN %s AND %s
            
            UNION ALL
            
            SELECT 
                'Average Rating' as metric,
                ROUND(AVG(rating), 2)::text as value,
                'Average content rating' as description
            FROM Reviews
            
            UNION ALL
            
            SELECT 
                'Completion Rate' as metric,
                ROUND(AVG(completion_percentage), 1)::text || '%' as value,
                'Average viewing completion rate' as description
            FROM WatchHistory
            WHERE watchDate BETWEEN %s AND %s
            AND completion_percentage > 0
        """
        
        results = self.db_manager.execute_query(query, (date_to, date_from, date_to, date_from, date_to, date_from, date_to))
        columns = ["Metric", "Value", "Description"]
        
        return results, columns
    
    def analyze_results(self):
        """Analyze current query results"""
        if not self.current_results:
            messagebox.showwarning("Warning", "No results to analyze")
            return
        
        try:
            # Create analysis popup
            popup = tk.Toplevel()
            popup.title(f"Results Analysis - {self.current_query_name}")
            popup.geometry("600x500")
            popup.transient(self.parent_frame)
            
            # Analysis text area
            analysis_text = tk.Text(popup, wrap=tk.WORD, font=('Consolas', 10))
            analysis_scrollbar = ttk.Scrollbar(popup, orient="vertical", command=analysis_text.yview)
            analysis_text.configure(yscrollcommand=analysis_scrollbar.set)
            
            # Generate analysis
            analysis = self.generate_results_analysis()
            analysis_text.insert(1.0, analysis)
            analysis_text.config(state=tk.DISABLED)
            
            # Pack widgets
            analysis_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            analysis_scrollbar.pack(side="right", fill="y", pady=10)
            
            # Close button
            ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze results: {str(e)}")
    
    def generate_results_analysis(self):
        """Generate analysis text for current results"""
        if not self.current_results:
            return "No results to analyze."
        
        analysis = f"📊 RESULTS ANALYSIS: {self.current_query_name}\n"
        analysis += "=" * 50 + "\n\n"
        
        # Basic statistics
        total_rows = len(self.current_results)
        analysis += f"📈 Basic Statistics:\n"
        analysis += f"   • Total rows: {total_rows:,}\n"
        
        if total_rows > 0:
            # Sample data structure
            sample_row = self.current_results[0]
            if isinstance(sample_row, dict):
                columns = list(sample_row.keys())
            else:
                columns = [f"Column_{i+1}" for i in range(len(sample_row))]
            
            analysis += f"   • Total columns: {len(columns)}\n"
            analysis += f"   • Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}\n\n"
            
            # Numeric analysis
            analysis += f"🔢 Numeric Analysis:\n"
            for i, col in enumerate(columns[:3]):  # Analyze first 3 columns
                try:
                    if isinstance(sample_row, dict):
                        values = [row.get(col) for row in self.current_results if row.get(col) is not None]
                    else:
                        values = [row[i] for row in self.current_results if i < len(row) and row[i] is not None]
                    
                    # Try to convert to numeric
                    numeric_values = []
                    for val in values:
                        try:
                            numeric_values.append(float(val))
                        except (ValueError, TypeError):
                            break
                    
                    if numeric_values and len(numeric_values) > len(values) * 0.5:
                        analysis += f"   • {col}:\n"
                        analysis += f"     - Min: {min(numeric_values):,.2f}\n"
                        analysis += f"     - Max: {max(numeric_values):,.2f}\n"
                        analysis += f"     - Avg: {sum(numeric_values)/len(numeric_values):,.2f}\n"
                        
                except Exception:
                    continue
            
            # Data quality
            analysis += f"\n🔍 Data Quality:\n"
            null_counts = {}
            for i, col in enumerate(columns[:5]):
                try:
                    if isinstance(sample_row, dict):
                        null_count = sum(1 for row in self.current_results if not row.get(col))
                    else:
                        null_count = sum(1 for row in self.current_results if i >= len(row) or not row[i])
                    
                    null_percentage = (null_count / total_rows) * 100
                    analysis += f"   • {col}: {null_count} nulls ({null_percentage:.1f}%)\n"
                    
                except Exception:
                    continue
            
            # Insights
            analysis += f"\n💡 Key Insights:\n"
            if total_rows > 1000:
                analysis += f"   • Large dataset with {total_rows:,} records - consider pagination\n"
            elif total_rows < 10:
                analysis += f"   • Small dataset with only {total_rows} records\n"
            
            # Performance recommendations
            analysis += f"\n⚡ Performance Recommendations:\n"
            if total_rows > 5000:
                analysis += f"   • Consider adding LIMIT clause for large result sets\n"
                analysis += f"   • Use indexes on frequently queried columns\n"
            
            analysis += f"   • Current query returned {total_rows:,} rows\n"
            analysis += f"   • Consider caching results for repeated use\n"
        
        return analysis
    
    def export_results(self):
        """Export current results to file"""
        if not self.current_results:
            messagebox.showwarning("Warning", "No results to export")
            return
        
        try:
            # Get filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("Excel files", "*.xlsx")],
                title="Export Query Results",
                initialvalue=f"{self.current_query_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if not filename:
                return
            
            # Export based on file extension
            if filename.lower().endswith('.csv'):
                self.export_to_csv(filename)
            elif filename.lower().endswith('.json'):
                self.export_to_json(filename)
            elif filename.lower().endswith('.xlsx'):
                self.export_to_excel(filename)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
            
            messagebox.showinfo("Success", f"Results exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
    def export_to_csv(self, filename):
        """Export results to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if not self.current_results:
                return
            
            # Get column names
            if isinstance(self.current_results[0], dict):
                columns = list(self.current_results[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()
                writer.writerows(self.current_results)
            else:
                writer = csv.writer(csvfile)
                writer.writerows(self.current_results)
    
    def export_to_json(self, filename):
        """Export results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            # Convert to JSON-serializable format
            json_data = {
                'query_name': self.current_query_name,
                'export_date': datetime.now().isoformat(),
                'total_rows': len(self.current_results),
                'results': []
            }
            
            for row in self.current_results:
                if isinstance(row, dict):
                    # Convert any non-serializable objects to strings
                    json_row = {}
                    for key, value in row.items():
                        try:
                            json.dumps(value)  # Test if serializable
                            json_row[key] = value
                        except (TypeError, ValueError):
                            json_row[key] = str(value)
                    json_data['results'].append(json_row)
                else:
                    # Convert tuple/list to dict
                    json_row = {f'column_{i+1}': str(val) for i, val in enumerate(row)}
                    json_data['results'].append(json_row)
            
            json.dump(json_data, jsonfile, indent=2, default=str)
    
    def export_to_excel(self, filename):
        """Export results to Excel file"""
        try:
            import pandas as pd
            
            if isinstance(self.current_results[0], dict):
                df = pd.DataFrame(self.current_results)
            else:
                df = pd.DataFrame(self.current_results)
            
            # Write to Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Query Results', index=False)
                
                # Add metadata sheet
                metadata = pd.DataFrame({
                    'Property': ['Query Name', 'Export Date', 'Total Rows'],
                    'Value': [self.current_query_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), len(self.current_results)]
                })
                metadata.to_excel(writer, sheet_name='Metadata', index=False)
                
        except ImportError:
            messagebox.showerror("Error", "pandas library required for Excel export")
    
    def clear_results(self):
        """Clear current results"""
        try:
            # Clear results trees
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            for item in self.custom_results_tree.get_children():
                self.custom_results_tree.delete(item)
            
            for item in self.report_results_tree.get_children():
                self.report_results_tree.delete(item)
            
            # Reset info labels
            self.results_info_label.config(text="No query executed")
            self.execution_time_label.config(text="")
            self.custom_results_info_label.config(text="No custom query executed")
            self.report_results_info_label.config(text="No report generated")
            
            # Clear stored results
            self.current_results = []
            self.current_query_name = ""
            
            messagebox.showinfo("Success", "Results cleared")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear results: {str(e)}")
    
    def show_query_history(self):
        """Show query execution history"""
        messagebox.showinfo("Query History", "Query history feature would be implemented here.\n\nThis would show:\n• Previously executed queries\n• Execution times\n• Results counts\n• Saved queries")
    
    def email_report(self):
        """Email generated report"""
        messagebox.showinfo("Email Report", "Email functionality would be implemented here.\n\nThis would:\n• Generate PDF report\n• Send via email\n• Schedule automatic delivery")
    
    def schedule_report(self):
        """Schedule automatic report generation"""
        messagebox.showinfo("Schedule Report", "Report scheduling would be implemented here.\n\nThis would allow:\n• Daily/Weekly/Monthly schedules\n• Automatic generation\n• Email delivery\n• Custom parameters")
      
