"""
Functions and Procedures Screen for Streaming Service Management System
מסך פונקציות ופרוצדורות למערכת ניהול שירותי סטרימינג

Manages and executes stored functions and procedures from Stage 4
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, date
import json

class FunctionsProcedures:
    """
    Functions and Procedures class for managing stored functions and procedures
    """
    
    def __init__(self, parent_frame, db_manager, colors):
        """
        Initialize functions and procedures management
        
        Args:
            parent_frame: Parent frame for functions and procedures
            db_manager: Database manager instance
            colors: Color scheme dictionary
        """
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.colors = colors
        
        # Available functions and procedures from Stage 4
        self.functions_procedures = {
            "functions": {
                "get_customer_total_watch_time": {
                    "name": "Get Customer Total Watch Time",
                    "description": "Calculate total watch time for a specific customer",
                    "parameters": [("customer_id", "int", "Customer ID")],
                    "sql": "SELECT get_customer_total_watch_time(%s)",
                    "return_type": "float"
                },
                "calculate_completion_rate": {
                    "name": "Calculate Content Completion Rate",
                    "description": "Calculate average completion rate for specific content",
                    "parameters": [("movie_id", "int", "Movie/Content ID")],
                    "sql": "SELECT calculate_completion_rate(%s)",
                    "return_type": "float"
                },
                "get_monthly_revenue": {
                    "name": "Get Monthly Revenue",
                    "description": "Calculate total revenue for a specific month",
                    "parameters": [("year", "int", "Year"), ("month", "int", "Month")],
                    "sql": "SELECT get_monthly_revenue(%s, %s)",
                    "return_type": "float"
                },
                "count_active_profiles": {
                    "name": "Count Active Profiles",
                    "description": "Count active profiles for a customer",
                    "parameters": [("customer_id", "int", "Customer ID")],
                    "sql": "SELECT count_active_profiles(%s)",
                    "return_type": "int"
                }
            },
            "procedures": {
                "update_customer_subscription": {
                    "name": "Update Customer Subscription",
                    "description": "Update customer subscription type and payment status",
                    "parameters": [
                        ("customer_id", "int", "Customer ID"),
                        ("new_subscription", "varchar", "New Subscription Type"),
                        ("new_status", "varchar", "New Payment Status")
                    ],
                    "sql": "CALL update_customer_subscription(%s, %s, %s)"
                },
                "cleanup_inactive_profiles": {
                    "name": "Cleanup Inactive Profiles",
                    "description": "Remove profiles that haven't been active for specified days",
                    "parameters": [("days_inactive", "int", "Days of inactivity")],
                    "sql": "CALL cleanup_inactive_profiles(%s)"
                },
                "generate_monthly_report": {
                    "name": "Generate Monthly Report",
                    "description": "Generate comprehensive monthly usage report",
                    "parameters": [("year", "int", "Year"), ("month", "int", "Month")],
                    "sql": "CALL generate_monthly_report(%s, %s)"
                },
                "backup_customer_data": {
                    "name": "Backup Customer Data",
                    "description": "Create backup of customer and related data",
                    "parameters": [("customer_id", "int", "Customer ID")],
                    "sql": "CALL backup_customer_data(%s)"
                }
            }
        }
        
        # Current execution results
        self.execution_results = []
        self.current_function = None
    
    def create_interface(self):
        """Create functions and procedures interface"""
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Content area with notebook tabs
        content_notebook = ttk.Notebook(main_container)
        content_notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Functions tab
        functions_frame = ttk.Frame(content_notebook)
        content_notebook.add(functions_frame, text="🔧 Functions")
        self.create_functions_tab(functions_frame)
        
        # Procedures tab
        procedures_frame = ttk.Frame(content_notebook)
        content_notebook.add(procedures_frame, text="⚙️ Procedures")
        self.create_procedures_tab(procedures_frame)
        
        # Custom SQL tab
        custom_frame = ttk.Frame(content_notebook)
        content_notebook.add(custom_frame, text="💻 Custom SQL")
        self.create_custom_sql_tab(custom_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame,
                               text="⚙️ Functions & Procedures",
                               font=('Arial', 16, 'bold'),
                               foreground=self.colors['primary'])
        title_label.pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame,
                  text="📊 Function Stats",
                  command=self.show_function_statistics,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="🔄 Refresh Schema",
                  command=self.refresh_schema,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="📋 Execution Log",
                  command=self.show_execution_log,
                  style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, pady=(5, 0))
    
    def create_functions_tab(self, parent):
        """Create functions tab"""
        # Split into left (functions list) and right (execution)
        paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - functions list
        functions_frame = ttk.LabelFrame(paned_window, text="Available Functions", padding="10")
        paned_window.add(functions_frame, weight=1)
        
        # Functions treeview
        func_columns = ('Function', 'Description', 'Parameters')
        self.functions_tree = ttk.Treeview(functions_frame, columns=func_columns, show='headings', height=12)
        
        self.functions_tree.heading('Function', text='Function Name')
        self.functions_tree.heading('Description', text='Description')
        self.functions_tree.heading('Parameters', text='Parameters')
        
        self.functions_tree.column('Function', width=200, anchor=tk.W)
        self.functions_tree.column('Description', width=300, anchor=tk.W)
        self.functions_tree.column('Parameters', width=150, anchor=tk.W)
        
        # Populate functions tree
        for func_id, func_info in self.functions_procedures['functions'].items():
            param_count = len(func_info['parameters'])
            param_text = f"{param_count} parameter{'s' if param_count != 1 else ''}"
            
            self.functions_tree.insert('', 'end', iid=f"func_{func_id}", values=(
                func_info['name'],
                func_info['description'],
                param_text
            ))
        
        # Scrollbar for functions tree
        func_scrollbar = ttk.Scrollbar(functions_frame, orient="vertical", command=self.functions_tree.yview)
        self.functions_tree.configure(yscrollcommand=func_scrollbar.set)
        
        # Pack functions tree
        self.functions_tree.pack(side="left", fill="both", expand=True)
        func_scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.functions_tree.bind('<<TreeviewSelect>>', self.on_function_select)
        
        # Right side - execution area
        exec_frame = ttk.LabelFrame(paned_window, text="Function Execution", padding="10")
        paned_window.add(exec_frame, weight=1)
        
        self.create_execution_area(exec_frame, "function")
    
    def create_procedures_tab(self, parent):
        """Create procedures tab"""
        # Split into left (procedures list) and right (execution)
        paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - procedures list
        procedures_frame = ttk.LabelFrame(paned_window, text="Available Procedures", padding="10")
        paned_window.add(procedures_frame, weight=1)
        
        # Procedures treeview
        proc_columns = ('Procedure', 'Description', 'Parameters')
        self.procedures_tree = ttk.Treeview(procedures_frame, columns=proc_columns, show='headings', height=12)
        
        self.procedures_tree.heading('Procedure', text='Procedure Name')
        self.procedures_tree.heading('Description', text='Description')
        self.procedures_tree.heading('Parameters', text='Parameters')
        
        self.procedures_tree.column('Procedure', width=200, anchor=tk.W)
        self.procedures_tree.column('Description', width=300, anchor=tk.W)
        self.procedures_tree.column('Parameters', width=150, anchor=tk.W)
        
        # Populate procedures tree
        for proc_id, proc_info in self.functions_procedures['procedures'].items():
            param_count = len(proc_info['parameters'])
            param_text = f"{param_count} parameter{'s' if param_count != 1 else ''}"
            
            self.procedures_tree.insert('', 'end', iid=f"proc_{proc_id}", values=(
                proc_info['name'],
                proc_info['description'],
                param_text
            ))
        
        # Scrollbar for procedures tree
        proc_scrollbar = ttk.Scrollbar(procedures_frame, orient="vertical", command=self.procedures_tree.yview)
        self.procedures_tree.configure(yscrollcommand=proc_scrollbar.set)
        
        # Pack procedures tree
        self.procedures_tree.pack(side="left", fill="both", expand=True)
        proc_scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.procedures_tree.bind('<<TreeviewSelect>>', self.on_procedure_select)
        
        # Right side - execution area
        exec_frame = ttk.LabelFrame(paned_window, text="Procedure Execution", padding="10")
        paned_window.add(exec_frame, weight=1)
        
        self.create_execution_area(exec_frame, "procedure")
    
    def create_execution_area(self, parent, exec_type):
        """Create execution area for functions or procedures"""
        # Function/Procedure info
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        if exec_type == "function":
            self.func_info_label = ttk.Label(info_frame, text="Select a function to execute", 
                                           font=('Arial', 10, 'bold'))
            self.func_info_label.pack(anchor=tk.W)
        else:
            self.proc_info_label = ttk.Label(info_frame, text="Select a procedure to execute", 
                                           font=('Arial', 10, 'bold'))
            self.proc_info_label.pack(anchor=tk.W)
        
        # Parameters frame
        params_frame = ttk.LabelFrame(parent, text="Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        if exec_type == "function":
            self.func_params_frame = ttk.Frame(params_frame)
            self.func_params_frame.pack(fill=tk.X)
            self.func_param_entries = {}
        else:
            self.proc_params_frame = ttk.Frame(params_frame)
            self.proc_params_frame.pack(fill=tk.X)
            self.proc_param_entries = {}
        
        # Execution buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        if exec_type == "function":
            ttk.Button(buttons_frame,
                      text="▶️ Execute Function",
                      command=self.execute_function,
                      style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        else:
            ttk.Button(buttons_frame,
                      text="▶️ Execute Procedure",
                      command=self.execute_procedure,
                      style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame,
                  text="📋 View SQL",
                  command=lambda: self.view_sql(exec_type),
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame,
                  text="🔄 Clear",
                  command=lambda: self.clear_results(exec_type),
                  style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Results area
        results_frame = ttk.LabelFrame(parent, text="Execution Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        if exec_type == "function":
            self.func_results_text = scrolledtext.ScrolledText(results_frame, height=15, width=60,
                                                              font=('Consolas', 10), wrap=tk.WORD)
            self.func_results_text.pack(fill=tk.BOTH, expand=True)
        else:
            self.proc_results_text = scrolledtext.ScrolledText(results_frame, height=15, width=60,
                                                              font=('Consolas', 10), wrap=tk.WORD)
            self.proc_results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_custom_sql_tab(self, parent):
        """Create custom SQL tab for advanced users"""
        # SQL input area
        input_frame = ttk.LabelFrame(parent, text="Custom SQL Input", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        # SQL text area
        self.custom_sql_text = scrolledtext.ScrolledText(input_frame, height=10, width=80,
                                                        font=('Consolas', 10), wrap=tk.NONE)
        self.custom_sql_text.pack(fill=tk.BOTH, expand=True)
        
        # Add sample SQL
        sample_sql = """-- Sample function call:
-- SELECT get_customer_total_watch_time(1);

-- Sample procedure call:
-- CALL update_customer_subscription(1, 'Premium', 'Current');

-- Enter your custom SQL here:
"""
        self.custom_sql_text.insert(1.0, sample_sql)
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame,
                  text="▶️ Execute",
                  command=self.execute_custom_sql,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame,
                  text="🔍 Validate",
                  command=self.validate_custom_sql,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame,
                  text="❌ Clear",
                  command=self.clear_custom_sql,
                  style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Results area
        results_frame = ttk.LabelFrame(parent, text="Custom SQL Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.custom_sql_results = scrolledtext.ScrolledText(results_frame, height=12, width=80,
                                                           font=('Consolas', 10), wrap=tk.WORD)
        self.custom_sql_results.pack(fill=tk.BOTH, expand=True)
    
    def on_function_select(self, event):
        """Handle function selection"""
        selection = self.functions_tree.selection()
        if selection:
            func_id = selection[0].replace('func_', '')
            self.current_function = ('function', func_id)
            self.load_function_details(func_id)
    
    def on_procedure_select(self, event):
        """Handle procedure selection"""
        selection = self.procedures_tree.selection()
        if selection:
            proc_id = selection[0].replace('proc_', '')
            self.current_function = ('procedure', proc_id)
            self.load_procedure_details(proc_id)
    
    def load_function_details(self, func_id):
        """Load function details and create parameter inputs"""
        func_info = self.functions_procedures['functions'][func_id]
        
        # Update info label
        self.func_info_label.config(text=f"Function: {func_info['name']}")
        
        # Clear existing parameter inputs
        for widget in self.func_params_frame.winfo_children():
            widget.destroy()
        self.func_param_entries = {}
        
        # Create parameter inputs
        for i, (param_name, param_type, param_desc) in enumerate(func_info['parameters']):
            row_frame = ttk.Frame(self.func_params_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            # Parameter label
            label_text = f"{param_desc} ({param_type}):"
            ttk.Label(row_frame, text=label_text, width=25).pack(side=tk.LEFT)
            
            # Parameter entry
            entry = ttk.Entry(row_frame, width=20)
            entry.pack(side=tk.LEFT, padx=(10, 0))
            
            self.func_param_entries[param_name] = entry
    
    def load_procedure_details(self, proc_id):
        """Load procedure details and create parameter inputs"""
        proc_info = self.functions_procedures['procedures'][proc_id]
        
        # Update info label
        self.proc_info_label.config(text=f"Procedure: {proc_info['name']}")
        
        # Clear existing parameter inputs
        for widget in self.proc_params_frame.winfo_children():
            widget.destroy()
        self.proc_param_entries = {}
        
        # Create parameter inputs
        for i, (param_name, param_type, param_desc) in enumerate(proc_info['parameters']):
            row_frame = ttk.Frame(self.proc_params_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            # Parameter label
            label_text = f"{param_desc} ({param_type}):"
            ttk.Label(row_frame, text=label_text, width=25).pack(side=tk.LEFT)
            
            # Parameter entry
            entry = ttk.Entry(row_frame, width=20)
            entry.pack(side=tk.LEFT, padx=(10, 0))
            
            self.proc_param_entries[param_name] = entry
    
    def execute_function(self):
        """Execute selected function"""
        if not self.current_function or self.current_function[0] != 'function':
            messagebox.showwarning("Warning", "Please select a function to execute")
            return
        
        try:
            func_id = self.current_function[1]
            func_info = self.functions_procedures['functions'][func_id]
            
            # Collect parameters
            params = []
            for param_name, param_type, param_desc in func_info['parameters']:
                value = self.func_param_entries[param_name].get().strip()
                if not value:
                    messagebox.showerror("Error", f"Parameter '{param_desc}' is required")
                    return
                
                # Convert to appropriate type
                try:
                    if param_type == 'int':
                        params.append(int(value))
                    elif param_type == 'float':
                        params.append(float(value))
                    else:
                        params.append(value)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid value for parameter '{param_desc}' (expected {param_type})")
                    return
            
            # Execute function
            start_time = datetime.now()
            result = self.db_manager.call_function(func_id, params)
            end_time = datetime.now()
            
            execution_time = (end_time - start_time).total_seconds()
            
            # Display results
            result_text = f"FUNCTION EXECUTION RESULTS\n"
            result_text += f"{'='*50}\n"
            result_text += f"Function: {func_info['name']}\n"
            result_text += f"Executed at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += f"Execution time: {execution_time:.3f} seconds\n"
            result_text += f"Parameters: {', '.join(map(str, params))}\n\n"
            result_text += f"RESULT:\n"
            result_text += f"{result}\n\n"
            
            self.func_results_text.delete(1.0, tk.END)
            self.func_results_text.insert(1.0, result_text)
            
            # Log execution
            self.log_execution('function', func_info['name'], params, result, execution_time)
            
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to execute function:\n\n{str(e)}")
            self.log_execution('function', func_info['name'], params, f"ERROR: {str(e)}", 0)
    
    def execute_procedure(self):
        """Execute selected procedure"""
        if not self.current_function or self.current_function[0] != 'procedure':
            messagebox.showwarning("Warning", "Please select a procedure to execute")
            return
        
        try:
            proc_id = self.current_function[1]
            proc_info = self.functions_procedures['procedures'][proc_id]
            
            # Collect parameters
            params = []
            for param_name, param_type, param_desc in proc_info['parameters']:
                value = self.proc_param_entries[param_name].get().strip()
                if not value:
                    messagebox.showerror("Error", f"Parameter '{param_desc}' is required")
                    return
                
                # Convert to appropriate type
                try:
                    if param_type == 'int':
                        params.append(int(value))
                    elif param_type == 'float':
                        params.append(float(value))
                    else:
                        params.append(value)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid value for parameter '{param_desc}' (expected {param_type})")
                    return
            
            # Execute procedure
            start_time = datetime.now()
            result = self.db_manager.call_procedure(proc_id, params)
            end_time = datetime.now()
            
            execution_time = (end_time - start_time).total_seconds()
            
            # Display results
            result_text = f"PROCEDURE EXECUTION RESULTS\n"
            result_text += f"{'='*50}\n"
            result_text += f"Procedure: {proc_info['name']}\n"
            result_text += f"Executed at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += f"Execution time: {execution_time:.3f} seconds\n"
            result_text += f"Parameters: {', '.join(map(str, params))}\n\n"
            result_text += f"RESULT:\n"
            if result:
                result_text += f"{result}\n"
            else:
                result_text += "Procedure executed successfully (no return value)\n"
            result_text += "\n"
            
            self.proc_results_text.delete(1.0, tk.END)
            self.proc_results_text.insert(1.0, result_text)
            
            # Log execution
            self.log_execution('procedure', proc_info['name'], params, result or "Success", execution_time)
            
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to execute procedure:\n\n{str(e)}")
            self.log_execution('procedure', proc_info['name'], params, f"ERROR: {str(e)}", 0)
    
    def execute_custom_sql(self):
        """Execute custom SQL"""
        try:
            sql = self.custom_sql_text.get(1.0, tk.END).strip()
            if not sql:
                messagebox.showwarning("Warning", "Please enter SQL to execute")
                return
            
            start_time = datetime.now()
            
            # Check if it's a SELECT statement or procedure call
            sql_upper = sql.upper().strip()
            if sql_upper.startswith('SELECT') or sql_upper.startswith('WITH'):
                result = self.db_manager.execute_query(sql)
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # Format results
                result_text = f"CUSTOM SQL EXECUTION RESULTS\n"
                result_text += f"{'='*50}\n"
                result_text += f"Executed at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                result_text += f"Execution time: {execution_time:.3f} seconds\n\n"
                result_text += f"SQL:\n{sql}\n\n"
                result_text += f"RESULTS ({len(result) if result else 0} rows):\n"
                
                if result:
                    # Display first few rows
                    for i, row in enumerate(result[:10]):
                        if isinstance(row, dict):
                            result_text += f"Row {i+1}: {dict(row)}\n"
                        else:
                            result_text += f"Row {i+1}: {row}\n"
                    
                    if len(result) > 10:
                        result_text += f"... and {len(result) - 10} more rows\n"
                else:
                    result_text += "No results returned\n"
                
            else:
                # Non-SELECT statement
                rows_affected = self.db_manager.execute_query(sql, fetch=False)
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                result_text = f"CUSTOM SQL EXECUTION RESULTS\n"
                result_text += f"{'='*50}\n"
                result_text += f"Executed at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                result_text += f"Execution time: {execution_time:.3f} seconds\n\n"
                result_text += f"SQL:\n{sql}\n\n"
                result_text += f"RESULT:\n"
                result_text += f"Command executed successfully. Rows affected: {rows_affected}\n"
            
            self.custom_sql_results.delete(1.0, tk.END)
            self.custom_sql_results.insert(1.0, result_text)
            
        except Exception as e:
            messagebox.showerror("SQL Error", f"Failed to execute SQL:\n\n{str(e)}")
    
    def validate_custom_sql(self):
        """Validate custom SQL syntax"""
        try:
            sql = self.custom_sql_text.get(1.0, tk.END).strip()
            if not sql:
                messagebox.showwarning("Warning", "Please enter SQL to validate")
                return
            
            # Try to explain the query for validation
            if sql.upper().strip().startswith('SELECT'):
                validation_sql = f"EXPLAIN {sql}"
                self.db_manager.execute_query(validation_sql)
                messagebox.showinfo("Validation", "✅ SQL syntax is valid")
            else:
                messagebox.showinfo("Validation", "⚠️ Non-SELECT statements cannot be validated without execution")
                
        except Exception as e:
            messagebox.showerror("Validation Error", f"❌ SQL syntax error:\n\n{str(e)}")
    
    def clear_custom_sql(self):
        """Clear custom SQL text area"""
        if messagebox.askyesno("Confirm", "Clear the SQL editor?"):
            self.custom_sql_text.delete(1.0, tk.END)
    
    def view_sql(self, exec_type):
        """View SQL for selected function or procedure"""
        if not self.current_function:
            messagebox.showwarning("Warning", f"Please select a {exec_type} first")
            return
        
        if exec_type == 'function':
            func_id = self.current_function[1]
            func_info = self.functions_procedures['functions'][func_id]
        else:
            proc_id = self.current_function[1]
            func_info = self.functions_procedures['procedures'][proc_id]
        
        # Create popup to show SQL
        popup = tk.Toplevel()
        popup.title(f"SQL - {func_info['name']}")
        popup.geometry("600x400")
        popup.transient(self.parent_frame)
        
        # SQL display
        sql_text = scrolledtext.ScrolledText(popup, font=('Consolas', 10))
        sql_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show SQL with parameter placeholders
        sql_content = f"-- {func_info['name']}\n"
        sql_content += f"-- {func_info['description']}\n\n"
        sql_content += f"-- Parameters:\n"
        for param_name, param_type, param_desc in func_info['parameters']:
            sql_content += f"-- {param_name} ({param_type}): {param_desc}\n"
        sql_content += f"\n{func_info['sql']};\n"
        
        sql_text.insert(1.0, sql_content)
        sql_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)
    
    def clear_results(self, exec_type):
        """Clear execution results"""
        if exec_type == 'function':
            self.func_results_text.delete(1.0, tk.END)
        else:
            self.proc_results_text.delete(1.0, tk.END)
    
    def log_execution(self, exec_type, name, params, result, execution_time):
        """Log function/procedure execution"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': exec_type,
            'name': name,
            'parameters': params,
            'result': str(result)[:100] + '...' if len(str(result)) > 100 else str(result),
            'execution_time': execution_time,
            'status': 'success' if not str(result).startswith('ERROR') else 'error'
        }
        
        self.execution_results.append(log_entry)
        
        # Keep only last 100 executions
        if len(self.execution_results) > 100:
            self.execution_results = self.execution_results[-100:]
    
    def show_execution_log(self):
        """Show execution log in popup"""
        popup = tk.Toplevel()
        popup.title("Execution Log")
        popup.geometry("800x500")
        popup.transient(self.parent_frame)
        
        # Log treeview
        log_columns = ('Time', 'Type', 'Name', 'Parameters', 'Status', 'Time (s)')
        log_tree = ttk.Treeview(popup, columns=log_columns, show='headings')
        
        for col in log_columns:
            log_tree.heading(col, text=col)
            log_tree.column(col, width=120, anchor=tk.CENTER)
        
        # Add log entries
        for entry in reversed(self.execution_results[-50:]):  # Show last 50
            values = (
                entry['timestamp'].split('T')[1][:8],  # Time only
                entry['type'].title(),
                entry['name'],
                f"{len(entry['parameters'])} params",
                entry['status'].title(),
                f"{entry['execution_time']:.3f}"
            )
            log_tree.insert('', 'end', values=values)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=log_tree.yview)
        log_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        log_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Close button
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)
    
    def show_function_statistics(self):
        """Show function execution statistics"""
        if not self.execution_results:
            messagebox.showinfo("Statistics", "No execution history available")
            return
        
        # Calculate statistics
        total_executions = len(self.execution_results)
        successful_executions = sum(1 for entry in self.execution_results if entry['status'] == 'success')
        failed_executions = total_executions - successful_executions
        avg_execution_time = sum(entry['execution_time'] for entry in self.execution_results) / total_executions
        
        # Most used functions/procedures
        usage_count = {}
        for entry in self.execution_results:
            key = f"{entry['type']}: {entry['name']}"
            usage_count[key] = usage_count.get(key, 0) + 1
        
        most_used = sorted(usage_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Format statistics
        stats_text = f"""Function & Procedure Statistics:

Total Executions: {total_executions}
Successful: {successful_executions} ({successful_executions/total_executions*100:.1f}%)
Failed: {failed_executions} ({failed_executions/total_executions*100:.1f}%)
Average Execution Time: {avg_execution_time:.3f} seconds

Most Used:"""
        
        for name, count in most_used:
            stats_text += f"\n  • {name}: {count} times"
        
        messagebox.showinfo("Function Statistics", stats_text)
    
    def refresh_schema(self):
        """Refresh database schema information"""
        try:
            # This would refresh the list of available functions and procedures
            # from the actual database schema
            messagebox.showinfo("Schema Refresh", 
                               "Schema refreshed successfully!\n\n"
                               "In a full implementation, this would:\n"
                               "• Query database for available functions\n"
                               "• Update the functions and procedures lists\n"
                               "• Refresh parameter information")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh schema: {str(e)}")
          
