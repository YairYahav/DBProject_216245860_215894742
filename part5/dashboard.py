"""
Dashboard Screen for Streaming Service Management System
מסך ראשי למערכת ניהול שירותי סטרימינג

Displays system overview, statistics, and quick actions
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading

class Dashboard:
    """
    Dashboard class for displaying system overview and statistics
    """
    
    def __init__(self, parent_frame, db_manager, colors):
        """
        Initialize dashboard
        
        Args:
            parent_frame: Parent frame for dashboard
            db_manager: Database manager instance
            colors: Color scheme dictionary
        """
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.colors = colors
        
        # Statistics data
        self.stats_data = {}
        self.refresh_in_progress = False
    
    def create_dashboard(self):
        """Create dashboard interface"""
        # Main container with scrollable frame
        self.create_main_container()
        
        # Header section
        self.create_header_section()
        
        # Statistics cards
        self.create_statistics_cards()
        
        # Quick actions section
        self.create_quick_actions()
        
        # Recent activity section
        self.create_recent_activity()
        
        # System status section
        self.create_system_status()
        
        # Load initial data
        self.refresh_dashboard_data()
    
    def create_main_container(self):
        """Create main scrollable container"""
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.parent_frame, bg=self.colors['light'])
        self.scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_header_section(self):
        """Create dashboard header"""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Title and timestamp
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(fill=tk.X)
        
        # Dashboard title
        title_label = ttk.Label(title_frame,
                               text="📊 System Dashboard",
                               font=('Arial', 18, 'bold'),
                               foreground=self.colors['primary'])
        title_label.pack(side=tk.LEFT)
        
        # Last updated timestamp
        self.timestamp_label = ttk.Label(title_frame,
                                        text="Last updated: Loading...",
                                        font=('Arial', 9),
                                        foreground=self.colors['dark'])
        self.timestamp_label.pack(side=tk.RIGHT)
        
        # Refresh button
        refresh_btn = ttk.Button(title_frame,
                               text="🔄 Refresh",
                               command=self.refresh_dashboard_data,
                               style='Secondary.TButton')
        refresh_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Separator
        separator = ttk.Separator(header_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 0))
    
    def create_statistics_cards(self):
        """Create statistics cards section"""
        stats_frame = ttk.LabelFrame(self.scrollable_frame, text="📈 System Statistics", padding="15")
        stats_frame.pack(fill=tk.X, padx=20, pady=(10, 10))
        
        # Create grid for statistics cards
        self.stats_cards = {}\n        \n        # Row 1: User Statistics\n        row1_frame = ttk.Frame(stats_frame)\n        row1_frame.pack(fill=tk.X, pady=(0, 10))\n        \n        self.stats_cards['customers'] = self.create_stat_card(\n            row1_frame, \"👥 Total Customers\", \"0\", self.colors['primary'], \"left\")\n        self.stats_cards['profiles'] = self.create_stat_card(\n            row1_frame, \"👤 Active Profiles\", \"0\", self.colors['secondary'], \"left\")\n        self.stats_cards['online'] = self.create_stat_card(\n            row1_frame, \"🟢 Online Now\", \"0\", self.colors['success'], \"left\")\n        \n        # Row 2: Content Statistics\n        row2_frame = ttk.Frame(stats_frame)\n        row2_frame.pack(fill=tk.X, pady=(0, 10))\n        \n        self.stats_cards['total_content'] = self.create_stat_card(\n            row2_frame, \"🎬 Total Content\", \"0\", self.colors['accent'], \"left\")\n        self.stats_cards['watch_sessions'] = self.create_stat_card(\n            row2_frame, \"📺 Watch Sessions (24h)\", \"0\", self.colors['warning'], \"left\")\n        self.stats_cards['total_hours'] = self.create_stat_card(\n            row2_frame, \"⏱️ Total Hours Watched\", \"0\", self.colors['dark'], \"left\")\n        \n        # Row 3: Financial Statistics\n        row3_frame = ttk.Frame(stats_frame)\n        row3_frame.pack(fill=tk.X)\n        \n        self.stats_cards['revenue'] = self.create_stat_card(\n            row3_frame, \"💰 Monthly Revenue\", \"$0\", self.colors['success'], \"left\")\n        self.stats_cards['avg_rating'] = self.create_stat_card(\n            row3_frame, \"⭐ Average Rating\", \"0.0\", self.colors['warning'], \"left\")\n        self.stats_cards['completion_rate'] = self.create_stat_card(\n            row3_frame, \"📊 Completion Rate\", \"0%\", self.colors['secondary'], \"left\")\n    \n    def create_stat_card(self, parent, title, value, color, side):\n        \"\"\"Create individual statistics card\"\"\"\n        card_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1)\n        card_frame.pack(side=side, fill=tk.BOTH, expand=True, padx=(0, 10) if side == \"left\" else (0, 0))\n        \n        # Configure card styling\n        card_frame.configure(padding=(15, 10))\n        \n        # Title\n        title_label = ttk.Label(card_frame,\n                               text=title,\n                               font=('Arial', 10),\n                               foreground=self.colors['dark'])\n        title_label.pack(anchor=tk.W)\n        \n        # Value\n        value_label = ttk.Label(card_frame,\n                               text=value,\n                               font=('Arial', 16, 'bold'),\n                               foreground=color)\n        value_label.pack(anchor=tk.W)\n        \n        return value_label\n    \n    def create_quick_actions(self):\n        \"\"\"Create quick actions section\"\"\"\n        actions_frame = ttk.LabelFrame(self.scrollable_frame, text=\"⚡ Quick Actions\", padding=\"15\")\n        actions_frame.pack(fill=tk.X, padx=20, pady=(10, 10))\n        \n        # Create grid for action buttons\n        buttons_frame = ttk.Frame(actions_frame)\n        buttons_frame.pack(fill=tk.X)\n        \n        # Action buttons\n        actions = [\n            (\"👥 Add Customer\", self.quick_add_customer, self.colors['primary']),\n            (\"👤 Add Profile\", self.quick_add_profile, self.colors['secondary']),\n            (\"📺 Record Viewing\", self.quick_add_viewing, self.colors['accent']),\n            (\"📊 View Reports\", self.quick_view_reports, self.colors['warning']),\n            (\"⚙️ Run Maintenance\", self.quick_maintenance, self.colors['dark']),\n            (\"🔍 Search Content\", self.quick_search, self.colors['success'])\n        ]\n        \n        # Arrange buttons in 3x2 grid\n        for i, (text, command, color) in enumerate(actions):\n            row = i // 3\n            col = i % 3\n            \n            btn = ttk.Button(buttons_frame,\n                           text=text,\n                           command=command,\n                           style='Primary.TButton')\n            btn.grid(row=row, column=col, padx=5, pady=5, sticky=\"ew\")\n        \n        # Configure grid weights\n        for i in range(3):\n            buttons_frame.columnconfigure(i, weight=1)\n    \n    def create_recent_activity(self):\n        \"\"\"Create recent activity section\"\"\"\n        activity_frame = ttk.LabelFrame(self.scrollable_frame, text=\"📋 Recent Activity\", padding=\"15\")\n        activity_frame.pack(fill=tk.X, padx=20, pady=(10, 10))\n        \n        # Create treeview for recent activity\n        columns = (\"Time\", \"Type\", \"Description\", \"User\")\n        self.activity_tree = ttk.Treeview(activity_frame, columns=columns, show=\"headings\", height=6)\n        \n        # Configure columns\n        self.activity_tree.heading(\"Time\", text=\"Time\")\n        self.activity_tree.heading(\"Type\", text=\"Type\")\n        self.activity_tree.heading(\"Description\", text=\"Description\")\n        self.activity_tree.heading(\"User\", text=\"User\")\n        \n        self.activity_tree.column(\"Time\", width=100, anchor=tk.CENTER)\n        self.activity_tree.column(\"Type\", width=80, anchor=tk.CENTER)\n        self.activity_tree.column(\"Description\", width=300, anchor=tk.W)\n        self.activity_tree.column(\"User\", width=100, anchor=tk.CENTER)\n        \n        # Scrollbar for activity tree\n        activity_scroll = ttk.Scrollbar(activity_frame, orient=\"vertical\", command=self.activity_tree.yview)\n        self.activity_tree.configure(yscrollcommand=activity_scroll.set)\n        \n        # Pack treeview and scrollbar\n        self.activity_tree.pack(side=\"left\", fill=\"both\", expand=True)\n        activity_scroll.pack(side=\"right\", fill=\"y\")\n    \n    def create_system_status(self):\n        \"\"\"Create system status section\"\"\"\n        status_frame = ttk.LabelFrame(self.scrollable_frame, text=\"🖥️ System Status\", padding=\"15\")\n        status_frame.pack(fill=tk.X, padx=20, pady=(10, 20))\n        \n        # Database status\n        db_frame = ttk.Frame(status_frame)\n        db_frame.pack(fill=tk.X, pady=(0, 10))\n        \n        ttk.Label(db_frame, text=\"Database:\", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)\n        self.db_status_label = ttk.Label(db_frame, text=\"Connected ✅\", foreground=self.colors['success'])\n        self.db_status_label.pack(side=tk.LEFT, padx=(10, 0))\n        \n        # Performance metrics\n        perf_frame = ttk.Frame(status_frame)\n        perf_frame.pack(fill=tk.X, pady=(0, 10))\n        \n        ttk.Label(perf_frame, text=\"Performance:\", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)\n        self.perf_status_label = ttk.Label(perf_frame, text=\"Optimal ✅\", foreground=self.colors['success'])\n        self.perf_status_label.pack(side=tk.LEFT, padx=(10, 0))\n        \n        # Last backup\n        backup_frame = ttk.Frame(status_frame)\n        backup_frame.pack(fill=tk.X)\n        \n        ttk.Label(backup_frame, text=\"Last Backup:\", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)\n        self.backup_status_label = ttk.Label(backup_frame, text=\"N/A\", foreground=self.colors['warning'])\n        self.backup_status_label.pack(side=tk.LEFT, padx=(10, 0))\n    \n    def refresh_dashboard_data(self):\n        \"\"\"Refresh dashboard data\"\"\"\n        if self.refresh_in_progress:\n            return\n        \n        self.refresh_in_progress = True\n        \n        # Update timestamp\n        self.timestamp_label.config(text=f\"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\")\n        \n        # Load data in background thread\n        thread = threading.Thread(target=self._load_dashboard_data)\n        thread.daemon = True\n        thread.start()\n    \n    def _load_dashboard_data(self):\n        \"\"\"Load dashboard data from database\"\"\"\n        try:\n            # Load statistics\n            self._load_statistics()\n            \n            # Load recent activity\n            self._load_recent_activity()\n            \n            # Update UI in main thread\n            self.parent_frame.after(0, self._update_dashboard_ui)\n            \n        except Exception as e:\n            print(f\"Error loading dashboard data: {str(e)}\")\n            # Show error in main thread\n            self.parent_frame.after(0, lambda: messagebox.showerror(\"Error\", f\"Failed to load dashboard data: {str(e)}\"))\n        \n        finally:\n            self.refresh_in_progress = False\n    \n    def _load_statistics(self):\n        \"\"\"Load statistics from database\"\"\"\n        try:\n            # Total customers\n            customers = self.db_manager.execute_query(\"SELECT COUNT(*) FROM Customer\")\n            self.stats_data['customers'] = customers[0][0] if customers else 0\n            \n            # Active profiles\n            profiles = self.db_manager.execute_query(\"SELECT COUNT(*) FROM Profile WHERE account_status = 'Active'\")\n            self.stats_data['profiles'] = profiles[0][0] if profiles else 0\n            \n            # Online profiles\n            online = self.db_manager.execute_query(\"SELECT COUNT(*) FROM Profile WHERE isOnline = true\")\n            self.stats_data['online'] = online[0][0] if online else 0\n            \n            # Total content\n            content = self.db_manager.execute_query(\"SELECT COUNT(*) FROM Title\")\n            self.stats_data['total_content'] = content[0][0] if content else 0\n            \n            # Watch sessions last 24h\n            sessions = self.db_manager.execute_query(\n                \"SELECT COUNT(*) FROM WatchHistory WHERE watchDate >= CURRENT_DATE - INTERVAL '1 day'\"\n            )\n            self.stats_data['watch_sessions'] = sessions[0][0] if sessions else 0\n            \n            # Total hours watched\n            hours = self.db_manager.execute_query(\n                \"SELECT COALESCE(SUM(durationWatched), 0) / 60.0 FROM WatchHistory\"\n            )\n            self.stats_data['total_hours'] = round(hours[0][0], 1) if hours else 0\n            \n            # Monthly revenue (mock data)\n            revenue = self.db_manager.execute_query(\n                \"SELECT COALESCE(SUM(amount), 0) FROM Payment WHERE paymentDate >= DATE_TRUNC('month', CURRENT_DATE)\"\n            )\n            self.stats_data['revenue'] = round(revenue[0][0], 2) if revenue else 0\n            \n            # Average rating\n            rating = self.db_manager.execute_query(\n                \"SELECT COALESCE(AVG(rating), 0) FROM Reviews\"\n            )\n            self.stats_data['avg_rating'] = round(rating[0][0], 1) if rating else 0\n            \n            # Completion rate (mock calculation)\n            completion = self.db_manager.execute_query(\n                \"SELECT COALESCE(AVG(completion_percentage), 0) FROM WatchHistory WHERE completion_percentage > 0\"\n            )\n            self.stats_data['completion_rate'] = round(completion[0][0], 1) if completion else 0\n            \n        except Exception as e:\n            print(f\"Error loading statistics: {str(e)}\")\n            # Set default values\n            self.stats_data = {\n                'customers': 0, 'profiles': 0, 'online': 0, 'total_content': 0,\n                'watch_sessions': 0, 'total_hours': 0, 'revenue': 0,\n                'avg_rating': 0, 'completion_rate': 0\n            }\n    \n    def _load_recent_activity(self):\n        \"\"\"Load recent activity from database\"\"\"\n        try:\n            # Get recent watch history\n            activity_query = \"\"\"\n                SELECT \n                    wh.watchDate,\n                    'Watch' as activity_type,\n                    CONCAT('Watched \"', COALESCE(t.Title_Name, 'Unknown'), '\" for ', \n                           ROUND(wh.durationWatched, 1), ' minutes') as description,\n                    CONCAT(c.firstName, ' ', c.lastName) as user_name\n                FROM WatchHistory wh\n                LEFT JOIN Title t ON wh.movieID = t.Title_ID\n                LEFT JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID\n                LEFT JOIN Customer c ON p.customerID = c.customerID\n                WHERE wh.watchDate >= CURRENT_DATE - INTERVAL '7 days'\n                ORDER BY wh.watchDate DESC\n                LIMIT 20\n            \"\"\"\n            \n            self.stats_data['recent_activity'] = self.db_manager.execute_query(activity_query) or []\n            \n        except Exception as e:\n            print(f\"Error loading recent activity: {str(e)}\")\n            self.stats_data['recent_activity'] = []\n    \n    def _update_dashboard_ui(self):\n        \"\"\"Update dashboard UI with loaded data\"\"\"\n        try:\n            # Update statistics cards\n            self.stats_cards['customers'].config(text=str(self.stats_data['customers']))\n            self.stats_cards['profiles'].config(text=str(self.stats_data['profiles']))\n            self.stats_cards['online'].config(text=str(self.stats_data['online']))\n            self.stats_cards['total_content'].config(text=str(self.stats_data['total_content']))\n            self.stats_cards['watch_sessions'].config(text=str(self.stats_data['watch_sessions']))\n            self.stats_cards['total_hours'].config(text=f\"{self.stats_data['total_hours']:,.1f}h\")\n            self.stats_cards['revenue'].config(text=f\"${self.stats_data['revenue']:,.2f}\")\n            self.stats_cards['avg_rating'].config(text=f\"{self.stats_data['avg_rating']:.1f}/5\")\n            self.stats_cards['completion_rate'].config(text=f\"{self.stats_data['completion_rate']:.1f}%\")\n            \n            # Update recent activity\n            self.activity_tree.delete(*self.activity_tree.get_children())\n            \n            for activity in self.stats_data['recent_activity']:\n                time_str = activity[0].strftime('%H:%M') if activity[0] else 'N/A'\n                self.activity_tree.insert('', 'end', values=(\n                    time_str,\n                    activity[1] or 'N/A',\n                    activity[2] or 'N/A',\n                    activity[3] or 'N/A'\n                ))\n            \n            # Update system status\n            if self.db_manager.is_connected():\n                self.db_status_label.config(text=\"Connected ✅\", foreground=self.colors['success'])\n            else:\n                self.db_status_label.config(text=\"Disconnected ❌\", foreground=self.colors['accent'])\n                \n        except Exception as e:\n            print(f\"Error updating dashboard UI: {str(e)}\")\n    \n    # Quick action methods\n    def quick_add_customer(self):\n        \"\"\"Quick add customer action\"\"\"\n        messagebox.showinfo(\"Quick Action\", \"Navigate to Customer Management to add a new customer.\")\n    \n    def quick_add_profile(self):\n        \"\"\"Quick add profile action\"\"\"\n        messagebox.showinfo(\"Quick Action\", \"Navigate to Profile Management to add a new profile.\")\n    \n    def quick_add_viewing(self):\n        \"\"\"Quick add viewing action\"\"\"\n        messagebox.showinfo(\"Quick Action\", \"Navigate to Watch History Management to record viewing.\")\n    \n    def quick_view_reports(self):\n        \"\"\"Quick view reports action\"\"\"\n        messagebox.showinfo(\"Quick Action\", \"Navigate to Queries & Reports to view detailed reports.\")\n    \n    def quick_maintenance(self):\n        \"\"\"Quick maintenance action\"\"\"\n        messagebox.showinfo(\"Quick Action\", \"Navigate to Functions & Procedures to run maintenance tasks.\")\n    \n    def quick_search(self):\n        \"\"\"Quick search action\"\"\"\n        messagebox.showinfo(\"Quick Action\", \"Use the navigation menu to search in specific sections.\")
