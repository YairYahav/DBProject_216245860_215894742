json

import json
import sqlite3
import datetime
import random
from pathlib import Path

def populate_from_json(db_path):
    """
    Populates approximately 1/3 of the database with data from JSON files.
    Each table will get around 133-134 entries from this function.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Load JSON data
    data_path = Path("data_files")
    
    # Create data directory if it doesn't exist
    data_path.mkdir(exist_ok=True)
    
    # Generate JSON data files if they don't exist
    generate_json_files(data_path)
    
    # Load data from JSON files
    with open(data_path / "customers.json", "r") as f:
        customers = json.load(f)
    
    with open(data_path / "devices.json", "r") as f:
        devices = json.load(f)
    
    with open(data_path / "watch_history.json", "r") as f:
        watch_history = json.load(f)
    
    with open(data_path / "favorites.json", "r") as f:
        favorites = json.load(f)
    
    with open(data_path / "payments.json", "r") as f:
        payments = json.load(f)
    
    with open(data_path / "profiles.json", "r") as f:
        profiles = json.load(f)
    
    with open(data_path / "reviews.json", "r") as f:
        reviews = json.load(f)
    
    with open(data_path / "marks_as_favorite.json", "r") as f:
        marks_as_favorite = json.load(f)
    
    # Insert data into tables
    # Customer table
    for customer in customers:
        cursor.execute("""
            INSERT INTO Customer (firstName, lastName, customerID, dateOfBirth, customerSince)
            VALUES (?, ?, ?, ?, ?)
        """, (
            customer["firstName"],
            customer["lastName"],
            customer["customerID"],
            customer["dateOfBirth"],
            customer["customerSince"]
        ))
    
    # Devices table
    for device in devices:
        cursor.execute("""
            INSERT INTO Devices (deviceName, deviceID, lastSeen, deviceType, customerID)
            VALUES (?, ?, ?, ?, ?)
        """, (
            device["deviceName"],
            device["deviceID"],
            device["lastSeen"],
            device["deviceType"],
            device["customerID"]
        ))
    
    # WatchHistory table
    for history in watch_history:
        cursor.execute("""
            INSERT INTO WatchHistory (movieID, watchDate, durationWatched, WatchHistoryID)
            VALUES (?, ?, ?, ?)
        """, (
            history["movieID"],
            history["watchDate"],
            history["durationWatched"],
            history["WatchHistoryID"]
        ))
    
    # Favorites table
    for favorite in favorites:
        cursor.execute("""
            INSERT INTO Favorites (movieID, lastSeen, totalTimeWatched)
            VALUES (?, ?, ?)
        """, (
            favorite["movieID"],
            favorite["lastSeen"],
            favorite["totalTimeWatched"]
        ))
    
    # Payment table
    for payment in payments:
        cursor.execute("""
            INSERT INTO Payment (paymentID, paymentDate, amount, currency, paymentMethod, status, customerID)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            payment["paymentID"],
            payment["paymentDate"],
            payment["amount"],
            payment["currency"],
            payment["paymentMethod"],
            payment["status"],
            payment["customerID"]
        ))
    
    # Profile table
    for profile in profiles:
        cursor.execute("""
            INSERT INTO Profile (profileName, profilePicture, isOnline, profileID, WatchHistoryID, customerID)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            profile["profileName"],
            profile["profilePicture"],
            profile["isOnline"],
            profile["profileID"],
            profile["WatchHistoryID"],
            profile["customerID"]
        ))
    
    # Reviews table
    for review in reviews:
        cursor.execute("""
            INSERT INTO Reviews (rating, movieID, comment, reviewDate, profileID)
            VALUES (?, ?, ?, ?, ?)
        """, (
            review["rating"],
            review["movieID"],
            review["comment"],
            review["reviewDate"],
            review["profileID"]
        ))
    
    # MarksAsFavorite table
    for mark in marks_as_favorite:
        cursor.execute("""
            INSERT INTO MarksAsFavorite (profileID, movieID)
            VALUES (?, ?)
        """, (
            mark["profileID"],
            mark["movieID"]
        ))
    
    # Commit and close connection
    conn.commit()
    conn.close()
    
    print(f"Successfully populated 1/3 of the database from JSON files")


def generate_json_files(data_path):
    """
    Generates JSON files with mock data for each table.
    This is a helper function to create the source JSON files.
    
    Args:
        data_path (Path): Directory path to save JSON files
    """
    # Generate customer data
    customers = []
    for i in range(134):
        customer_id = i + 1
        customer = {
            "firstName": f"FirstName{i}",
            "lastName": f"LastName{i}",
            "customerID": customer_id,
            "dateOfBirth": (datetime.date(1970, 1, 1) + datetime.timedelta(days=random.randint(0, 18250))).isoformat(),
            "customerSince": (datetime.date(2015, 1, 1) + datetime.timedelta(days=random.randint(0, 3000))).isoformat(),
        }
        customers.append(customer)
    
    # Generate devices data (multiple devices per customer)
    devices = []
    device_id = 1
    for customer in customers:
        num_devices = random.randint(1, 3)
        for j in range(num_devices):
            device = {
                "deviceName": random.choice(["Mobile", "Laptop", "TV", "Tablet", "Game Console"]) + f"_{j}",
                "deviceID": device_id,
                "lastSeen": (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 365))).isoformat(),
                "deviceType": random.choice(["iOS", "Android", "Windows", "macOS", "SmartTV"]),
                "customerID": customer["customerID"]
            }
            devices.append(device)
            device_id += 1
    
    # Generate watch history data
    watch_history = []
    for i in range(134):
        watch_history.append({
            "movieID": random.randint(1, 1000),
            "watchDate": (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 365))).isoformat(),
            "durationWatched": round(random.uniform(10, 180), 2),
            "WatchHistoryID": i + 1
        })
    
    # Generate favorites data
    favorites = []
    for i in range(134):
        favorites.append({
            "movieID": i + 1,
            "lastSeen": (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 365))).isoformat(),
            "totalTimeWatched": round(random.uniform(60, 600), 2)
        })
    
    # Generate payment data
    payments = []
    for i in range(134):
        customer_id = random.randint(1, len(customers))
        payments.append({
            "paymentID": i + 1,
            "paymentDate": (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 365))).isoformat(),
            "amount": round(random.uniform(5, 50), 2),
            "currency": random.choice(["USD", "EUR", "GBP", "CAD"]),
            "paymentMethod": random.choice(["Credit Card", "PayPal", "Bank Transfer", "Apple Pay", "Google Pay"]),
            "status": random.choice(["Completed", "Pending", "Failed"]),
            "customerID": customer_id
        })
    
    # Generate profile data
    profiles = []
    for i in range(134):
        customer_id = random.randint(1, len(customers))
        profiles.append({
            "profileName": f"Profile{i}",
            "profilePicture": f"avatar_{i}.png",
            "isOnline": random.choice([True, False]),
            "profileID": i + 1,
            "WatchHistoryID": i + 1,  # Assuming 1:1 relationship with watch history
            "customerID": customer_id
        })
    
    # Generate reviews data
    reviews = []
    for i in range(134):
        reviews.append({
            "rating": random.randint(1, 5),
            "movieID": i + 1,
            "comment": f"This is review comment {i}",
            "reviewDate": (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 365))).isoformat(),
            "profileID": random.randint(1, len(profiles))
        })
    
    # Generate marks as favorite data
    marks_as_favorite = []
    for i in range(134):
        marks_as_favorite.append({
            "profileID": random.randint(1, len(profiles)),
            "movieID": random.randint(1, len(favorites))
        })
    
    # Save data to JSON files
    with open(data_path / "customers.json", "w") as f:
        json.dump(customers, f, indent=2)
    
    with open(data_path / "devices.json", "w") as f:
        json.dump(devices, f, indent=2)
    
    with open(data_path / "watch_history.json", "w") as f:
        json.dump(watch_history, f, indent=2)
    
    with open(data_path / "favorites.json", "w") as f:
        json.dump(favorites, f, indent=2)
    
    with open(data_path / "payments.json", "w") as f:
        json.dump(payments, f, indent=2)
    
    with open(data_path / "profiles.json", "w") as f:
        json.dump(profiles, f, indent=2)
    
    with open(data_path / "reviews.json", "w") as f:
        json.dump(reviews, f, indent=2)
    
    with open(data_path / "marks_as_favorite.json", "w") as f:
        json.dump(marks_as_favorite, f, indent=2)


if _name_ == "_main_":
    # Example usage
    populate_from_json("streaming_service.db")
