# 🎬 DB5785 - Streaming Service Database Project 🗄️

A comprehensive database management system for a streaming service platform, built with PostgreSQL and Docker, featuring multiple user profiles, content management, payment processing, and viewing analytics.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Phase A - Database Design and Population](#phase-a---database-design-and-population)
- [Phase B - Queries and Constraints](#phase-b---queries-and-constraints)
- [Phase C - Integration and Views](#phase-c---integration-and-views)
- [Phase D - Advanced Database Programming](#phase-d---advanced-database-programming)
- [Phase E - Graphical User Interface](#phase-e---graphical-user-interface)
- [Setup Instructions](#setup-instructions)
- [Database Schema](#database-schema)

---

## 🎯 Project Overview

This project implements a complete database system for a streaming service platform similar to Netflix. The system manages customers, viewing profiles, content, payments, device tracking, and user preferences through a normalized relational database structure.

### Key Features
- **Multi-profile customer accounts** - Family members can have separate viewing profiles
- **Device management** - Track multiple viewing devices per customer
- **Payment processing** - Subscription billing and payment history
- **Content tracking** - Viewing history, favorites, and ratings
- **Analytics support** - Complex queries for business intelligence

---

## 📊 Phase A - Database Design and Population

### Database Schema Design

The streaming service database consists of 8 core entities designed in 3NF normalization:

#### Core Tables

**1. Customer Table** - Central customer information
- `customerID (INT PRIMARY KEY)` - Unique customer identifier
- `firstName (VARCHAR)` - Customer's first name
- `lastName (VARCHAR)` - Customer's last name  
- `dateOfBirth (DATE)` - For age verification and parental controls
- `customerSince (DATE)` - Account creation date for loyalty tracking

**2. Devices Table** - Multiple viewing devices per customer
- `deviceID (INT PRIMARY KEY)` - Unique device identifier
- `deviceName (VARCHAR)` - Human-readable device name
- `deviceType (VARCHAR)` - Device type (iOS, Android, Smart TV, etc.)
- `lastSeen (DATE)` - Last activity for security monitoring
- `customerID (INT, FOREIGN KEY)` - Links device to customer

**3. Profile Table** - Multiple viewing profiles per customer account
- `profileID (INT PRIMARY KEY)` - Unique profile identifier
- `profileName (VARCHAR)` - Display name for profile
- `profilePicture (VARCHAR)` - Avatar image path
- `isOnline (BOOL)` - Current online status
- `WatchHistoryID (INT, FOREIGN KEY)` - Links to viewing history
- `customerID (INT, FOREIGN KEY)` - Links profile to customer

**4. WatchHistory Table** - Viewing history tracking
- `WatchHistoryID (INT PRIMARY KEY)` - Unique record identifier
- `movieID (INT)` - Reference to content watched
- `watchDate (DATE)` - When content was viewed
- `durationWatched (FLOAT)` - Minutes watched for completion tracking

**5. Payment Table** - Subscription payments and billing
- `paymentID (INT PRIMARY KEY)` - Unique payment identifier
- `paymentDate (DATE)` - When payment was processed
- `amount (FLOAT)` - Payment amount
- `currency (VARCHAR)` - Currency type (USD, EUR, NIS, etc.)
- `paymentMethod (VARCHAR)` - Payment method used
- `status (VARCHAR)` - Payment status (Completed, Pending, Failed)
- `customerID (INT, FOREIGN KEY)` - Links payment to customer

**6. Favorites Table** - User's favorite content
- `movieID (INT PRIMARY KEY)` - Unique content identifier
- `lastSeen (DATE)` - Last time marked as favorite
- `totalTimeWatched (FLOAT)` - Total viewing time for content

**7. Reviews Table** - User reviews and ratings
- `movieID (INT PRIMARY KEY)` - Content being reviewed
- `rating (INT)` - Star rating (1-5)
- `comment (VARCHAR)` - Written review text
- `reviewDate (DATE)` - When review was submitted
- `profileID (INT, FOREIGN KEY)` - Links review to profile

**8. MarksAsFavorite Table** - Junction table for profile favorites
- `profileID (INT, FOREIGN KEY)` - Profile marking favorite
- `movieID (INT, FOREIGN KEY)` - Content marked as favorite
- Composite primary key (profileID, movieID)

### Entity Relationship Diagrams

#### ERD (Entity Relationship Diagram)
![ERD](images/erd/ERD.PNG)

#### DSD (Database Schema Diagram)  
![DSD](images/erd/DSD.png)

### Data Population Methods

The database was populated using three different approaches:

1. **Python Script Generation** - [Generate Data Python Code](Backups/Backup1%20/generatedata.py)
2. **SQL Insert Statements** - [Generate Data SQL Code](Backups/Backup1%20/generatedata.sql)  
3. **Mockaroo Data Service** - [Excel Template Generator](Backups/Backup1%20/excelTemplateGen.py)

Each table contains 400+ records with realistic streaming service data.

### Database Creation Files

- [Create Tables SQL](code/sql/createtable.sql) - Table creation script
- Database backup and restore procedures implemented

---

## 🔍 Phase B - Queries and Constraints

### Complex SELECT Queries

**1. All profiles with viewing history in 2024, including customer names**
![Viewing History 2024](images/queries/viewing_history_2024.png)

**2. Average viewing time for favorite movies**
![Favorites Average](images/queries/favorites_avg.png)

**3. Payment details of customers who paid over 200 NIS in the last year**
![Paid Over 200](images/queries/paid_over_200.png)

**4. Customers with more than two registered devices**
![More Than Two Devices](images/queries/more_than_two_devices.png)

**5. List of profiles that added a favorite movie rated less than 3**
![Low Rated Favorite Movie](images/queries/low_rated_fav_movie.png)

**6. All movies watched in October including viewing duration**
![October Watched Movies](images/queries/october_watched_movies.png)

**7. Details of customers who have not made any payments this year**
![Did Not Buy](images/queries/did_not_buy.png)

**8. Average viewing times by month**
![Average Viewing Time](images/queries/avg_viewing_time.png)

### Data Modification Operations

#### DELETE Operations

**1. Deleting profiles inactive for over a year**
- Before: ![Before One Year](images/queries/before_one_year.png)
- After: ![After One Year](images/queries/after_one_years.png)

**2. Deleting devices not seen for over two years**
- Before: ![Before Two Years](images/queries/before_two_years.png)
- After: ![After Two Years](images/queries/after_two_years.png)

**3. Deleting failed payments**
- Before: ![Before Failed Payments](images/queries/before_failed_payments_delete.png)
- After: ![After Failed Payments](images/queries/after_failed_payments_delete.png)

#### UPDATE Operations

**1. Updating payment status to "Completed"**
- Before: ![Before Completed](images/queries/before_completed.png)
- After: ![After Completed](images/queries/after_completed.png)

**2. Adding default profile pictures for users without pictures**
- Before: ![Before Default Pictures](images/queries/before_default_pictures.png)
- After: ![After Default Pictures](images/queries/after_default_pictures.png)

**3. Upgrading positive reviews to 5-star rating**
- Before: ![Before Upgrade to 5](images/queries/before_5.png)
- After: ![After Upgrade to 5](images/queries/after_5.png)

### Transaction Control

#### Rollback Demonstration
- Mid Rollback: ![Mid Rollback](images/queries/before_rollback.png)
- After Rollback: ![After Rollback](images/queries/after_rollback.png)

### Database Constraints

**1. Payment amount cannot be negative**
![Positive Amount](images/queries/positive_amount.png)

**2. Payment status must be from specific list**
![Formal Payment Status](images/queries/formal_payment_status.png)

**3. Every profile must have a default picture**
![Not Null Picture](images/queries/not_null_picture.png)

### Query Files
- [Queries](part2/Queries.sql) - All SELECT, UPDATE, DELETE queries
- [Constraints](part2/Constraints.sql) - Database constraint definitions
- [Rollback Commit](part2/RollBackCommit) - Transaction control examples

---

## 🔗 Phase C - Integration and Views

### Database Integration

In this phase, we integrated our content management system with a creators and production management system through reverse engineering and schema integration.

#### Reverse Engineering Process

We received a backup of a creators management database and performed reverse engineering to understand its structure:

**External System ERD**
![External ERD](images/theirs/their_erd.png)

**External System DSD**  
![External DSD](images/theirs/their_dsd.png)

#### Integration Process

The integration focused on merging the Production table from the creators system into our existing Title table to create a unified content entity.

**Integrated ERD**
![Integrated ERD](images/integrated/integrated_erd.png)

**Integrated DSD**
![Integrated DSD](images/integrated/integrated_dsd.png)

### Database Views

**Database Population Verification**
![Database Populated](part3/database_populated.png)

**Schema Modification Success**
![Alter Table Works](part3/alterTableWorks.png)

#### View 1 - Content Analytics
![View 1](part3/viewImages/view1.png)

**Query 1.1**
![Query 1.1](part3/viewImages/query11.png)

**Query 1.2**
![Query 1.2](part3/viewImages/query12.png)

#### View 2 - Customer Analytics
![View 2](part3/viewImages/view2.png)

**Query 2.1**
![Query 2.1](part3/viewImages/query21.png)

**Query 2.2**
![Query 2.2](part3/viewImages/query22.png)

---

## 💻 Phase D - Advanced Database Programming

### PL/pgSQL Programming

Developed advanced database programs including functions, procedures, triggers, and main programs implementing various streaming service functionalities.

**Programming Implementation Success**
![Part 4 Works](part4/part4Works.png)

#### Implemented Features:
- **2 Functions** - Complex data processing and calculations
- **2 Procedures** - Data management and business logic
- **2 Triggers** - Automatic data validation and logging
- **2 Main Programs** - Orchestrating function and procedure calls

### Programming Elements Used:
- Cursors (implicit and explicit)
- Ref Cursor returns
- DML operations (INSERT, UPDATE, DELETE)
- Conditional statements and loops
- Exception handling
- Record types

---

## 🖥️ Phase E - Graphical User Interface

### Application Interface

Developed a comprehensive GUI application for database interaction using Python.

#### Login System
![Login](part5/images/login.png)

#### Customer Management
![Customers](part5/images/costumers.png)

#### Add New Customer
![Add Customer](part5/images/add_costumer.png)

#### Delete Customer
![Delete Customer](part5/images/delete.png)

#### Edit Customer Information
![Edit Customer](part5/images/edit_costumer.png)

### GUI Features:
- **CRUD Operations** - Create, Read, Update, Delete for 3+ tables
- **Query Execution** - Run complex queries from Phase B
- **Function/Procedure Calls** - Execute database programs from Phase D
- **User-friendly Interface** - Intuitive navigation and data visualization

### Application Files:
- Main application: `streaming_service_gui.py`
- Supporting modules and configuration files included

---

## 🛠️ Setup Instructions

### Prerequisites
- **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (optional) - [Install Docker Compose](https://docs.docker.com/compose/install/)

### PostgreSQL Setup

```bash
# Pull PostgreSQL image
docker pull postgres:latest

# Create volume for data persistence
docker volume create postgres_data

# Run PostgreSQL container
docker run --name postgres -e POSTGRES_PASSWORD=your_password -d -p 5432:5432 -v postgres_data:/var/lib/postgresql/data postgres
```

### pgAdmin Setup

```bash
# Pull pgAdmin image
docker pull dpage/pgadmin4:latest

# Run pgAdmin container
docker run --name pgadmin -d -p 5050:80 -e PGADMIN_DEFAULT_EMAIL=admin@example.com -e PGADMIN_DEFAULT_PASSWORD=admin dpage/pgadmin4:latest
```

### Database Connection

1. Access pgAdmin at `http://localhost:5050`
2. Connect to PostgreSQL using:
   - Host: `postgres` (or find IP with `docker inspect --format='{{.NetworkSettings.IPAddress}}' postgres`)
   - Port: `5432`
   - Username: `postgres`
   - Password: `your_password`

---

## 📁 Project Structure

```
DBProject/
├── images/
│   ├── erd/              # ERD and DSD diagrams
│   ├── queries/          # Query result screenshots
│   ├── theirs/           # External system diagrams
│   └── integrated/       # Integration diagrams
├── code/sql/             # SQL creation scripts
├── part2/                # Phase B files
├── part3/                # Phase C files  
├── part4/                # Phase D files
├── part5/                # Phase E GUI files
├── Backups/              # Data generation scripts
└── README.md            # This file
```

---

## 🎯 Project Outcomes

This comprehensive database project demonstrates:

- **Database Design** - Normalized schema design following 3NF principles
- **Data Management** - Complex queries, constraints, and data integrity
- **System Integration** - Merging multiple database systems
- **Advanced Programming** - PL/pgSQL functions, procedures, and triggers
- **Application Development** - Full-featured GUI for database interaction
- **DevOps Practices** - Containerized deployment with Docker

The streaming service database successfully models real-world scenarios and provides a robust foundation for a production streaming platform.

---

## 📚 Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgAdmin Documentation](https://www.pgadmin.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
