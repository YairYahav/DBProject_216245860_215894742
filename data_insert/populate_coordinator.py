מתאם

import sqlite3
import os
from populate_from_json import populate_from_json
from populate_from_excel import populate_from_excel
from populate_from_python import populate_from_python

def create_database(db_path):
    """
    Creates the database schema based on the provided SQL statements.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE Customer
        (
          firstName VARCHAR NOT NULL,
          lastName VARCHAR NOT NULL,
          customerID INT NOT NULL,
          dateOfBirth DATE NOT NULL,
          customerSince DATE NOT NULL,
          PRIMARY KEY (customerID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Devices
        (
          deviceName VARCHAR NOT NULL,
          deviceID INT NOT NULL,
          lastSeen DATE NOT NULL,
          deviceType VARCHAR NOT NULL,
          customerID INT NOT NULL,
          PRIMARY KEY (deviceID),
          FOREIGN KEY (customerID) REFERENCES customer(customerID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE WatchHistory
        (
          movieID INT NOT NULL,
          watchDate DATE NOT NULL,
          durationWatched FLOAT NOT NULL,
          WatchHistoryID INT NOT NULL,
          PRIMARY KEY (WatchHistoryID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Favorites
        (
          movieID INT NOT NULL,
          lastSeen DATE NOT NULL,
          totalTimeWatched FLOAT NOT NULL,
          PRIMARY KEY (movieID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Payment
        (
          paymentID INT NOT NULL,
          paymentDate DATE NOT NULL,
          amount FLOAT NOT NULL,
          currency VARCHAR NOT NULL,
          paymentMethod VARCHAR NOT NULL,
          status VARCHAR NOT NULL,
          customerID INT NOT NULL,
          PRIMARY KEY (paymentID),
          FOREIGN KEY (customerID) REFERENCES customer(customerID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Profile
        (
          profileName VARCHAR NOT NULL,
          profilePicture VARCHAR NOT NULL,
          isOnline BOOL NOT NULL,
          profileID INT NOT NULL,
          WatchHistoryID INT NOT NULL,
          customerID INT NOT NULL,
          PRIMARY KEY (profileID),
          FOREIGN KEY (WatchHistoryID) REFERENCES WatchHistory(WatchHistoryID),
          FOREIGN KEY (customerID) REFERENCES customer(customerID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Reviews
        (
          rating INT NOT NULL,
          movieID INT NOT NULL,
          comment VARCHAR NOT NULL,
          reviewDate DATE NOT NULL,
          profileID INT NOT NULL,
          PRIMARY KEY (movieID),
          FOREIGN KEY (profileID) REFERENCES Profile(profileID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE MarksAsFavorite
        (
          profileID INT NOT NULL,
          movieID INT NOT NULL,
          PRIMARY KEY (profileID, movieID),
          FOREIGN KEY (profileID) REFERENCES Profile(profileID),
          FOREIGN KEY (movieID) REFERENCES Favorites(movieID)
        )
    """)
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Database schema created at {db_path}")


def populate_database(db_path):
    """
    Populates the database using all three methods.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    # Create the database schema
    create_database(db_path)
    
    # Populate using the three different methods
    populate_from_json(db_path)
    populate_from_excel(db_path)
    populate_from_python(db_path)
    
    # Verify data count
    verify_data_count(db_path)


def verify_data_count(db_path):
    """
    Verifies that each table has at least 400 entries.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = [
        "Customer", 
        "Devices", 
        "WatchHistory", 
        "Favorites", 
        "Payment", 
        "Profile", 
        "Reviews", 
        "MarksAsFavorite"
    ]
    
    print("\nVerification of data counts:")
    print("-" * 40)
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        status = "✓" if count >= 400 else "✗"
        print(f"{table}: {count} entries {status}")
    
    conn.close()


if _name_ == "_main_":
    db_path = "streaming_service.db"
    populate_database(db_path)
    print("\nDatabase population complete!")
