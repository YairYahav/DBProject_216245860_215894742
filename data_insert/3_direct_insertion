python

import sqlite3
import random
import datetime
import string
from faker import Faker

def populate_from_python(db_path):
    """
    Populates approximately 1/3 of the database with data generated directly in Python.
    Each table will get around 133-134 entries from this function.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Initialize Faker for generating realistic data
    fake = Faker()
    
    # Base IDs for this function - starting from where the second function left off
    base_id = 268
    
    # Generate and insert customer data
    customers = []
    for i in range(133):
        customer_id = base_id + i
        first_name = fake.first_name()
        last_name = fake.last_name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=70).strftime('%Y-%m-%d')
        customer_since = fake.date_between_dates(
            date_start=datetime.date(2015, 1, 1),
            date_end=datetime.date(2023, 12, 31)
        ).strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO Customer (firstName, lastName, customerID, dateOfBirth, customerSince)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, customer_id, dob, customer_since))
        
        customers.append({
            "id": customer_id,
            "firstName": first_name,
            "lastName": last_name
        })
    
    # Generate and insert device data
    device_id = base_id
    device_types = ["Smartphone", "Tablet", "Smart TV", "Laptop", "Desktop", "Game Console"]
    os_types = ["iOS", "Android", "Windows", "macOS", "Roku", "FireTV", "PlayStation", "Xbox"]
    
    for customer in customers:
        # Each customer has 1-4 devices
        num_devices = random.randint(1, 4)
        for _ in range(num_devices):
            device_name = f"{random.choice(device_types)} - {fake.word().capitalize()}"
            last_seen = fake.date_between_dates(
                date_start=datetime.date(2023, 1, 1),
                date_end=datetime.date(2023, 12, 31)
            ).strftime('%Y-%m-%d')
            device_type = random.choice(os_types)
            
            cursor.execute("""
                INSERT INTO Devices (deviceName, deviceID, lastSeen, deviceType, customerID)
                VALUES (?, ?, ?, ?, ?)
            """, (device_name, device_id, last_seen, device_type, customer["id"]))
            
            device_id += 1
    
    # Generate and insert watch history
    watch_histories = []
    for i in range(133):
        watch_history_id = base_id + i
        movie_id = random.randint(2001, 3000)
        watch_date = fake.date_between_dates(
            date_start=datetime.date(2023, 1, 1),
            date_end=datetime.date(2023, 12, 31)
        ).strftime('%Y-%m-%d')
        duration_watched = round(random.uniform(15, 240), 2)  # In minutes
        
        cursor.execute("""
            INSERT INTO WatchHistory (movieID, watchDate, durationWatched, WatchHistoryID)
            VALUES (?, ?, ?, ?)
        """, (movie_id, watch_date, duration_watched, watch_history_id))
        
        watch_histories.append({
            "id": watch_history_id,
            "movieID": movie_id
        })
    
    # Generate and insert favorites
    for i in range(133):
        movie_id = base_id + i
        last_seen = fake.date_between_dates(
            date_start=datetime.date(2023, 1, 1),
            date_end=datetime.date(2023, 12, 31)
        ).strftime('%Y-%m-%d')
        total_time_watched = round(random.uniform(120, 900), 2)  # In minutes
        
        cursor.execute("""
            INSERT INTO Favorites (movieID, lastSeen, totalTimeWatched)
            VALUES (?, ?, ?)
        """, (movie_id, last_seen, total_time_watched))
    
    # Generate and insert payment data
    payment_methods = ["Credit Card", "PayPal", "Google Pay", "Apple Pay", "Bank Transfer", "Gift Card"]
    currencies = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY"]
    statuses = ["Completed", "Pending", "Failed", "Refunded"]
    
    for i in range(133):
        payment_id = base_id + i
        customer_id = random.choice(customers)["id"]
        payment_date = fake.date_between_dates(
            date_start=datetime.date(2023, 1, 1),
            date_end=datetime.date(2023, 12, 31)
        ).strftime('%Y-%m-%d')
        amount = round(random.uniform(5, 100), 2)
        currency = random.choice(currencies)
        payment_method = random.choice(payment_methods)
        status = random.choice(statuses)
        
        cursor.execute("""
            INSERT INTO Payment (paymentID, paymentDate, amount, currency, paymentMethod, status, customerID)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (payment_id, payment_date, amount, currency, payment_method, status, customer_id))
    
    # Generate and insert profile data
    profiles = []
    for i in range(133):
        profile_id = base_id + i
        watch_history_id = base_id + i  # 1:1 relationship with watch history
        customer_id = random.choice(customers)["id"]
        profile_name = fake.user_name()
        profile_picture = f"avatar_{fake.word()}.png"
        is_online = random.choice([0, 1])  # Boolean as integer
        
        cursor.execute("""
            INSERT INTO Profile (profileName, profilePicture, isOnline, profileID, WatchHistoryID, customerID)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (profile_name, profile_picture, is_online, profile_id, watch_history_id, customer_id))
        
        profiles.append({
            "id": profile_id
        })
    
    # Generate and insert reviews
    for i in range(133):
        movie_id = base_id + i
        profile_id = random.choice(profiles)["id"]
        rating = random.randint(1, 5)
        comment = fake.paragraph(nb_sentences=2)
        review_date = fake.date_between_dates(
            date_start=datetime.date(2023, 1, 1),
            date_end=datetime.date(2023, 12, 31)
        ).strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO Reviews (rating, movieID, comment, reviewDate, profileID)
            VALUES (?, ?, ?, ?, ?)
        """, (rating, movie_id, comment, review_date, profile_id))
    
    # Generate and insert marks as favorite
    for i in range(133):
        profile_id = random.choice(profiles)["id"]
        movie_id = base_id + random.randint(0, 132)  # One of the movies we created in favorites
        
        # Avoid duplicate primary keys
        cursor.execute("SELECT COUNT(*) FROM MarksAsFavorite WHERE profileID = ? AND movieID = ?", (profile_id, movie_id))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO MarksAsFavorite (profileID, movieID)
                VALUES (?, ?)
            """, (profile_id, movie_id))
    
    # Commit and close connection
    conn.commit()
    conn.close()
    
    print(f"Successfully populated 1/3 of the database using Python generation")


if _name_ == "_main_":
    # Example usage
    populate_from_python("streaming_service.db")
