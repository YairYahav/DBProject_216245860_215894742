"""
Database Connection Manager for Streaming Service
מנהל חיבור בסיס נתונים למערכת סטרימינג

Handles PostgreSQL connections, queries, and error management
"""

import psycopg2
from psycopg2 import sql, extras
import os
from datetime import datetime, date
import json
from typing import List, Dict, Any, Optional, Tuple
import logging
from contextlib import contextmanager

class DatabaseManager:
    """
    Database manager class for PostgreSQL operations
    """
    
    def __init__(self):
        """Initialize database manager"""
        self.connection = None
        self.connection_params = None
        self.logger = self.setup_logging()
        
        # Default connection parameters
        self.default_params = {
            'host': 'localhost',
            'port': '5432',
            'database': 'streaming_service',
            'user': 'postgres',
            'password': ''
        }
    
    def setup_logging(self):
        """Setup logging for database operations"""
        logger = logging.getLogger('DatabaseManager')
        logger.setLevel(logging.INFO)
        
        # Create file handler if not exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def connect(self, host=None, port=None, database=None, user=None, password=None):
        """
        Connect to PostgreSQL database
        
        Args:
            host (str): Database host
            port (str): Database port
            database (str): Database name
            user (str): Username
            password (str): Password
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Use provided parameters or defaults
            self.connection_params = {
                'host': host or self.default_params['host'],
                'port': port or self.default_params['port'],
                'database': database or self.default_params['database'],
                'user': user or self.default_params['user'],
                'password': password or self.default_params['password']
            }
            
            # Establish connection
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.autocommit = False
            
            self.logger.info(f"Connected to database: {self.connection_params['database']}")
            return True
            
        except psycopg2.Error as e:
            self.logger.error(f"Database connection failed: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during connection: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.logger.info("Database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database connection: {str(e)}")
    
    def close_connection(self):
        """Alias for disconnect method"""
        self.disconnect()
    
    def is_connected(self):
        """
        Check if database connection is active
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            if self.connection and not self.connection.closed:
                # Test connection with simple query
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return True
        except:
            pass
        return False
    
    def reconnect(self):
        """Reconnect to database using stored parameters"""
        if self.connection_params:
            self.disconnect()
            return self.connect(**self.connection_params)
        return False
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor
        
        Yields:
            cursor: Database cursor
        """
        if not self.is_connected():
            if not self.reconnect():
                raise psycopg2.Error("No database connection available")
        
        cursor = self.connection.cursor(cursor_factory=extras.RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()
    
    def execute_query(self, query, params=None, fetch=True):
        """
        Execute SQL query
        
        Args:
            query (str): SQL query
            params (tuple): Query parameters
            fetch (bool): Whether to fetch results
            
        Returns:
            list: Query results if fetch=True, None otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                
                if fetch:
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return cursor.rowcount
                    
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Query execution failed: {str(e)}")
            raise e
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Unexpected error during query execution: {str(e)}")
            raise e
    
    def execute_many(self, query, params_list):
        """
        Execute query with multiple parameter sets
        
        Args:
            query (str): SQL query
            params_list (list): List of parameter tuples
            
        Returns:
            int: Number of affected rows
        """
        try:
            with self.get_cursor() as cursor:
                cursor.executemany(query, params_list)
                self.connection.commit()
                return cursor.rowcount
                
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Batch query execution failed: {str(e)}")
            raise e
    
    def call_procedure(self, procedure_name, params=None):
        """
        Call stored procedure
        
        Args:
            procedure_name (str): Procedure name
            params (tuple): Procedure parameters
            
        Returns:
            list: Procedure results
        """
        try:
            with self.get_cursor() as cursor:
                cursor.callproc(procedure_name, params)
                self.connection.commit()
                
                # Try to fetch results if available
                try:
                    return cursor.fetchall()
                except psycopg2.ProgrammingError:
                    return None
                    
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Procedure call failed: {str(e)}")
            raise e
    
    def call_function(self, function_name, params=None):
        """
        Call stored function
        
        Args:
            function_name (str): Function name
            params (tuple): Function parameters
            
        Returns:
            Any: Function result
        """
        try:
            with self.get_cursor() as cursor:
                # Build function call
                if params:
                    placeholders = ', '.join(['%s'] * len(params))
                    query = f"SELECT {function_name}({placeholders})"
                    cursor.execute(query, params)
                else:
                    query = f"SELECT {function_name}()"
                    cursor.execute(query)
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except psycopg2.Error as e:
            self.logger.error(f"Function call failed: {str(e)}")
            raise e
    
    # CRUD Operations for Customer table
    def get_customers(self, limit=None, offset=None, search_term=None):
        """Get customers with optional filtering"""
        query = """
            SELECT customerID, firstName, lastName, dateOfBirth, customerSince,
                   subscription_type, payment_status, last_login_date
            FROM Customer
        """
        params = []
        
        if search_term:
            query += " WHERE firstName ILIKE %s OR lastName ILIKE %s"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        query += " ORDER BY customerID"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
            
        if offset:
            query += " OFFSET %s"
            params.append(offset)
        
        return self.execute_query(query, params)
    
    def get_customer_by_id(self, customer_id):
        """Get customer by ID"""
        query = """
            SELECT customerID, firstName, lastName, dateOfBirth, customerSince,
                   subscription_type, payment_status, last_login_date
            FROM Customer
            WHERE customerID = %s
        """
        result = self.execute_query(query, (customer_id,))
        return result[0] if result else None
    
    def create_customer(self, customer_data):
        """Create new customer"""
        query = """
            INSERT INTO Customer (firstName, lastName, customerID, dateOfBirth, 
                                customerSince, subscription_type, payment_status)
            VALUES (%(firstName)s, %(lastName)s, %(customerID)s, %(dateOfBirth)s,
                   %(customerSince)s, %(subscription_type)s, %(payment_status)s)
            RETURNING customerID
        """
        result = self.execute_query(query, customer_data)
        return result[0]['customerid'] if result else None
    
    def update_customer(self, customer_id, customer_data):
        """Update customer"""
        query = """
            UPDATE Customer 
            SET firstName = %(firstName)s, lastName = %(lastName)s,
                dateOfBirth = %(dateOfBirth)s, subscription_type = %(subscription_type)s,
                payment_status = %(payment_status)s, last_login_date = %(last_login_date)s
            WHERE customerID = %(customerID)s
        """
        customer_data['customerID'] = customer_id
        return self.execute_query(query, customer_data, fetch=False)
    
    def delete_customer(self, customer_id):
        """Delete customer"""
        query = "DELETE FROM Customer WHERE customerID = %s"
        return self.execute_query(query, (customer_id,), fetch=False)
    
    # CRUD Operations for Profile table
    def get_profiles(self, customer_id=None):
        """Get profiles with optional customer filtering"""
        query = """
            SELECT p.profileID, p.profileName, p.profilePicture, p.isOnline,
                   p.customerID, p.WatchHistoryID, p.account_status,
                   c.firstName, c.lastName
            FROM Profile p
            JOIN Customer c ON p.customerID = c.customerID
        """
        params = []
        
        if customer_id:
            query += " WHERE p.customerID = %s"
            params.append(customer_id)
        
        query += " ORDER BY p.profileID"
        
        return self.execute_query(query, params)
    
    def get_profile_by_id(self, profile_id):
        """Get profile by ID"""
        query = """
            SELECT p.profileID, p.profileName, p.profilePicture, p.isOnline,
                   p.customerID, p.WatchHistoryID, p.account_status,
                   c.firstName, c.lastName
            FROM Profile p
            JOIN Customer c ON p.customerID = c.customerID
            WHERE p.profileID = %s
        """
        result = self.execute_query(query, (profile_id,))
        return result[0] if result else None
    
    def create_profile(self, profile_data):
        """Create new profile"""
        query = """
            INSERT INTO Profile (profileName, profilePicture, isOnline, profileID,
                               WatchHistoryID, customerID, account_status)
            VALUES (%(profileName)s, %(profilePicture)s, %(isOnline)s, %(profileID)s,
                   %(WatchHistoryID)s, %(customerID)s, %(account_status)s)
            RETURNING profileID
        """
        result = self.execute_query(query, profile_data)
        return result[0]['profileid'] if result else None
    
    def update_profile(self, profile_id, profile_data):
        """Update profile"""
        query = """
            UPDATE Profile 
            SET profileName = %(profileName)s, profilePicture = %(profilePicture)s,
                isOnline = %(isOnline)s, account_status = %(account_status)s
            WHERE profileID = %(profileID)s
        """
        profile_data['profileID'] = profile_id
        return self.execute_query(query, profile_data, fetch=False)
    
    def delete_profile(self, profile_id):
        """Delete profile"""
        query = "DELETE FROM Profile WHERE profileID = %s"
        return self.execute_query(query, (profile_id,), fetch=False)
    
    # CRUD Operations for WatchHistory table
    def get_watch_history(self, profile_id=None, limit=None):
        """Get watch history with optional filtering"""
        query = """
            SELECT wh.WatchHistoryID, wh.movieID, wh.watchDate, wh.durationWatched,
                   wh.completion_percentage, wh.viewing_category,
                   t.Title_Name, p.profileName, c.firstName, c.lastName
            FROM WatchHistory wh
            LEFT JOIN Title t ON wh.movieID = t.Title_ID
            LEFT JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID
            LEFT JOIN Customer c ON p.customerID = c.customerID
        """
        params = []
        
        if profile_id:
            query += " WHERE p.profileID = %s"
            params.append(profile_id)
        
        query += " ORDER BY wh.watchDate DESC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        return self.execute_query(query, params)
    
    def create_watch_history(self, watch_data):
        """Create new watch history record"""
        query = """
            INSERT INTO WatchHistory (WatchHistoryID, movieID, watchDate, 
                                    durationWatched, completion_percentage, viewing_category)
            VALUES (%(WatchHistoryID)s, %(movieID)s, %(watchDate)s,
                   %(durationWatched)s, %(completion_percentage)s, %(viewing_category)s)
            RETURNING WatchHistoryID
        """
        result = self.execute_query(query, watch_data)
        return result[0]['watchhistoryid'] if result else None
    
    def update_watch_history(self, watch_id, watch_data):
        """Update watch history record"""
        query = """
            UPDATE WatchHistory 
            SET movieID = %(movieID)s, watchDate = %(watchDate)s,
                durationWatched = %(durationWatched)s, 
                completion_percentage = %(completion_percentage)s,
                viewing_category = %(viewing_category)s
            WHERE WatchHistoryID = %(WatchHistoryID)s
        """
        watch_data['WatchHistoryID'] = watch_id
        return self.execute_query(query, watch_data, fetch=False)
    
    def delete_watch_history(self, watch_id):
        """Delete watch history record"""
        query = "DELETE FROM WatchHistory WHERE WatchHistoryID = %s"
        return self.execute_query(query, (watch_id,), fetch=False)
    
    # Utility methods
    def get_next_id(self, table_name, id_column):
        """Get next available ID for table"""
        query = f"SELECT COALESCE(MAX({id_column}), 0) + 1 FROM {table_name}"
        result = self.execute_query(query)
        return result[0][0] if result else 1
    
    def get_table_info(self, table_name):
        """Get table column information"""
        query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = current_schema()
            ORDER BY ordinal_position
        """
        return self.execute_query(query, (table_name,))
    
    def test_connection(self):
        """Test database connection"""
        try:
            result = self.execute_query("SELECT current_database(), current_user, now()")
            return {
                'status': 'success',
                'database': result[0][0],
                'user': result[0][1],
                'timestamp': result[0][2]
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
