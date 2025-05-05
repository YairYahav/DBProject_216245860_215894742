excel

import sqlite3
import pandas as pd
import random
import datetime
import os
from pathlib import Path

def populate_from_excel(db_path):
    """
    Populates approximately 1/3 of the database with data from Excel files.
    Each table will get around 133-134 entries from this function.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Setup Excel files directory
    excel_dir = Path("excel_data")
    excel_dir.mkdir(exist_ok=True)
    
    # Generate Excel files if they don't exist
    generate_excel_files(excel_dir)
    
    # Read data from Excel files and insert into database
    # Customer table
    df_customers = pd.read_excel(excel_dir / "customers.xlsx")
    for _, row in df_customers.iterrows():
        cursor.execute("""
            INSERT INTO Customer (firstName, lastName, customerID, dateOfBirth, customerSince)
            VALUES (?, ?, ?, ?, ?)
        """, (
            row["firstName"],
            row["lastName"],
            row["customerID"],
            row["dateOfBirth"],
            row["customerSince"]
        ))
    
    # Devices table
    df_devices = pd.read_excel(excel_dir / "devices.xlsx")
    for _, row in df_devices.iterrows():
        cursor.execute("""
            INSERT INTO Devices (deviceName, deviceID, lastSeen, deviceType, customerID)
            VALUES (?, ?, ?, ?, ?)
        """, (
            row["deviceName"],
            row["deviceID"],
            row["lastSeen"],
            row["deviceType"],
            row["customerID"]
        ))
    
    # WatchHistory table
    df_watch_history = pd.read_excel(excel_dir / "watch_history.xlsx")
    for _, row in df_watch_history.iterrows():
        cursor.execute("""
            INSERT INTO WatchHistory (movieID, watchDate, durationWatched, WatchHistoryID)
            VALUES (?, ?, ?, ?)
        """, (
            row["movieID"],
            row["watchDate"],
            row["durationWatched"],
            row["WatchHistoryID"]
        ))
    
    # Favorites table
    df_favorites = pd.read_excel(excel_dir / "favorites.xlsx")
    for _, row in df_favorites.iterrows():
        cursor.execute("""
            INSERT INTO Favorites (movieID, lastSeen, totalTimeWatched)
            VALUES (?, ?, ?)
        """, (
            row["movieID"],
            row["lastSeen"],
            row["totalTimeWatched"]
        ))
    
    # Payment table
    df_payments = pd.read_excel(excel_dir / "payments.xlsx")
    for _, row in df_payments.iterrows():
        cursor.execute("""
            INSERT INTO Payment (paymentID, paymentDate, amount, currency, paymentMethod, status, customerID)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row["paymentID"],
            row["paymentDate"],
            row["amount"],
            row["currency"],
            row["paymentMethod"],
            row["status"],
            row["customerID"]
        ))
    
    # Profile table
    df_profiles = pd.read_excel(excel_dir / "profiles.xlsx")
    for _, row in df_profiles.iterrows():
        cursor.execute("""
            INSERT INTO Profile (profileName, profilePicture, isOnline, profileID, WatchHistoryID, customerID)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row["profileName"],
            row["profilePicture"],
            row["isOnline"],
            row["profileID"],
            row["WatchHistoryID"],
            row["customerID"]
        ))
    
    # Reviews table
    df_reviews = pd.read_excel(excel_dir / "reviews.xlsx")
    for _, row in df_reviews.iterrows():
        cursor.execute("""
            INSERT INTO Reviews (rating, movieID, comment, reviewDate, profileID)
            VALUES (?, ?, ?, ?, ?)
        """, (
            row["rating"],
            row["movieID"],
            row["comment"],
            row["reviewDate"],
            row["profileID"]
        ))
    
    # MarksAsFavorite table
    df_marks = pd.read_excel(excel_dir / "marks_as_favorite.xlsx")
    for _, row in df_marks.iterrows():
        cursor.execute("""
            INSERT INTO MarksAsFavorite (profileID, movieID)
            VALUES (?, ?)
        """, (
            row["profileID"],
            row["movieID"]
        ))
    
    # Commit and close connection
    conn.commit()
    conn.close()
    
    print(f"Successfully populated 1/3 of the database from Excel files")


def generate_excel_files(excel_dir):
    """
    Generates Excel files with mock data for each table.
    
    Args:
        excel_dir (Path): Directory path to save Excel files
    """
    # Base IDs for this function - starting from where the first function left off
    base_id = 135
    
    # Generate customer data
    customers = []
    for i in range(133):
        customer_id = base_id + i
        customers.append({
            "firstName": f"ExcelFirstName{i}",
            "lastName": f"ExcelLastName{i}",
            "customerID": customer_id,
            "dateOfBirth": (datetime.date(1970, 1, 1) + datetime.timedelta(days=random.randint(0, 18250))).strftime('%Y-%m-%d'),
            "customerSince": (datetime.date(2015, 1, 1) + datetime.timedelta(days=random.randint(0, 3000))).strftime('%Y-%m-%d'),
        })
    
    # Generate devices data (multiple devices per customer)
    devices = []
    device_id = base_id
    for customer in customers:
        num_devices = random.randint(1, 3)
        for j in range(num_devices):
            devices.append({
                "deviceName": random.choice(["Mobile", "Laptop", "TV", "Tablet", "Game Console"]) + f"_{j}",
                "deviceID": device_id,
                "lastSeen": (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
                "deviceType": random.choice(["iOS", "Android", "Windows", "macOS", "SmartTV"]),
                "customerID": customer["customerID"]
            })
            device_id += 1
    
    # Generate watch history data
    watch_history = []
    for i in range(133):
        watch_history_id = base_id + i
        watch_history.append({
            "movieID": random.randint(1001, 2000),
            "watchDate": (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            "durationWatched": round(random.uniform(10, 180), 2),
            "WatchHistoryID": watch_history_id
        })
    
    # Generate favorites data
    favorites = []
    for i in range(133):
        movie_id = base_id + i
        favorites.append({
            "movieID": movie_id,
            "lastSeen": (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            "totalTimeWatched": round(random.uniform(60, 600), 2)
        })
    
    # Generate payment data
    payments = []
    for i in range(133):
        payment_id = base_id + i
        customer_id = random.choice(customers)["customerID"]
        payments.append({
            "paymentID": payment_id,
            "paymentDate": (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            "amount": round(random.uniform(5, 50), 2),
            "currency": random.choice(["USD", "EUR", "GBP", "CAD"]),
            "paymentMethod": random.choice(["Credit Card", "PayPal", "Bank Transfer", "Apple Pay", "Google Pay"]),
            "status": random.choice(["Completed", "Pending", "Failed"]),
            "customerID": customer_id
        })
    
    # Generate profile data
    profiles = []
    for i in range(133):
        profile_id = base_id + i
        watch_history_id = base_id + i  # Assuming 1:1 relationship with watch history
        customer_id = random.choice(customers)["customerID"]
        profiles.append({
            "profileName": f"ExcelProfile{i}",
            "profilePicture": f"excel_avatar_{i}.png",
            "isOnline": random.choice([True, False]),
            "profileID": profile_id,
            "WatchHistoryID": watch_history_id,
            "customerID": customer_id
        })
    
    # Generate reviews data
    reviews = []
    for i in range(133):
        movie_id = base_id + i
        profile_id = random.choice(profiles)["profileID"]
        reviews.append({
            "rating": random.randint(1, 5),
            "movieID": movie_id,
            "comment": f"This is an Excel review comment {i}",
            "reviewDate": (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            "profileID": profile_id
        })
    
    # Generate marks as favorite data
    marks_as_favorite = []
    for i in range(133):
        profile_id = random.choice(profiles)["profileID"]
        movie_id = random.choice(favorites)["movieID"]
        marks_as_favorite.append({
            "profileID": profile_id,
            "movieID": movie_id
        })
    
    # Convert to DataFrames and save to Excel files
    pd.DataFrame(customers).to_excel(excel_dir / "customers.xlsx", index=False)
    pd.DataFrame(devices).to_excel(excel_dir / "devices.xlsx", index=False)
    pd.DataFrame(watch_history).to_excel(excel_dir / "watch_history.xlsx", index=False)
    pd.DataFrame(favorites).to_excel(excel_dir / "favorites.xlsx", index=False)
    pd.DataFrame(payments).to_excel(excel_dir / "payments.xlsx", index=False)
    pd.DataFrame(profiles).to_excel(excel_dir / "profiles.xlsx", index=False)
    pd.DataFrame(reviews).to_excel(excel_dir / "reviews.xlsx", index=False)
    pd.DataFrame(marks_as_favorite).to_excel(excel_dir / "marks_as_favorite.xlsx", index=False)


if _name_ == "_main_":
    # Example usage
    populate_from_excel("streaming_service.db")
