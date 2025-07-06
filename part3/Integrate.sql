-- Integrate.sql - אינטגרציה בין מערכת Streaming Service לבין מערכת ניהול תוכן
-- מערכת שלי (Streaming) + מערכת החבר (Content Management עם יוצרים וסוכנים)

-- ===========================
-- שלב 1: הכנה לאינטגרציה - יישור מבני נתונים
-- ===========================

-- ווידוא שטבלת Title משותפת מוגדרת נכון
-- אם לא קיימת, ליצור אותה
CREATE TABLE IF NOT EXISTS Title (
    Title_ID INT PRIMARY KEY,
    Title_Name VARCHAR(200) NOT NULL,
    Age_Rating VARCHAR(10),
    Sequel_ID INT,
    FOREIGN KEY (Sequel_ID) REFERENCES Title(Title_ID)
);

-- הוספת עמודות נוספות לטבלת Title אם לא קיימות
ALTER TABLE Title ADD COLUMN IF NOT EXISTS Release_Date DATE;
ALTER TABLE Title ADD COLUMN IF NOT EXISTS Content_Type VARCHAR(20) DEFAULT 'Unknown';

-- ===========================
-- שלב 2: עדכון המערכת המקורית שלי לתמיכה במערכת החדשה
-- ===========================

-- עדכון טבלת WatchHistory - שינוי מ-movieID ל-Title_ID
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'watchhistory' AND column_name = 'movieid') THEN
        -- שינוי שם העמודה
        ALTER TABLE WatchHistory RENAME COLUMN movieID TO Title_ID;
        
        -- הוספת foreign key חדש לטבלת Title
        ALTER TABLE WatchHistory 
        ADD CONSTRAINT fk_watchhistory_title 
        FOREIGN KEY (Title_ID) REFERENCES Title(Title_ID);
    END IF;
END $$;

-- עדכון טבלת Reviews - מבנה חדש עם Title_ID
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'reviews' AND column_name = 'movieid') THEN
        
        -- הוספת Title_ID אם לא קיים
        ALTER TABLE Reviews ADD COLUMN IF NOT EXISTS Title_ID INT;
        
        -- עדכון Title_ID מתוך movieID (אם יש מיפוי)
        UPDATE Reviews 
        SET Title_ID = movieID 
        WHERE Title_ID IS NULL AND movieID IS NOT NULL;
        
        -- שינוי המפתח הראשי למבנה חדש
        ALTER TABLE Reviews DROP CONSTRAINT IF EXISTS reviews_pkey;
        ALTER TABLE Reviews DROP COLUMN IF EXISTS movieID;
        
        -- יצירת מפתח ראשי חדש
        ALTER TABLE Reviews ADD CONSTRAINT reviews_pkey 
        PRIMARY KEY (profileID, Title_ID);
        
        -- הוספת foreign key לטבלת Title
        ALTER TABLE Reviews 
        ADD CONSTRAINT fk_reviews_title 
        FOREIGN KEY (Title_ID) REFERENCES Title(Title_ID);
    END IF;
END $$;

-- עדכון טבלת Favorites
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'favorites' AND column_name = 'movieid') THEN
        
        ALTER TABLE Favorites RENAME COLUMN movieID TO Title_ID;
        
        ALTER TABLE Favorites 
        ADD CONSTRAINT fk_favorites_title 
        FOREIGN KEY (Title_ID) REFERENCES Title(Title_ID);
    END IF;
END $$;

-- עדכון טבלת MarksAsFavorite
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'marksasfavorite' AND column_name = 'movieid') THEN
        
        ALTER TABLE MarksAsFavorite RENAME COLUMN movieID TO Title_ID;
        
        ALTER TABLE MarksAsFavorite DROP CONSTRAINT IF EXISTS marksasfavorite_movieid_fkey;
        ALTER TABLE MarksAsFavorite 
        ADD CONSTRAINT fk_marksasfavorite_title 
        FOREIGN KEY (Title_ID) REFERENCES Title(Title_ID);
    END IF;
END $$;

-- ===========================
-- שלב 3: יצירת טבלאות חדשות מהמערכת של החבר
-- ===========================

-- טבלת Agent (סוכנים)
CREATE TABLE IF NOT EXISTS Agent (
    AgentID INT PRIMARY KEY,
    AgentFullName VARCHAR(100) NOT NULL,
    AgencyName VARCHAR(100),
    PhoneNumber VARCHAR(20),
    Email VARCHAR(100) UNIQUE
);

-- טבלת Content_Creator (יוצרי תוכן)
CREATE TABLE IF NOT EXISTS Content_Creator (
    CreatorID INT PRIMARY KEY,
    Content_CreatorFullName VARCHAR(100) NOT NULL,
    BirthDate DATE,
    Country VARCHAR(50),
    IsActive BOOLEAN DEFAULT TRUE,
    JoinDate DATE DEFAULT CURRENT_DATE,
    AgentID INT,
    FOREIGN KEY (AgentID) REFERENCES Agent(AgentID)
);

-- טבלת Contract (חוזים)
CREATE TABLE IF NOT EXISTS Contract (
    ContractID INT PRIMARY KEY,
    StartDate DATE NOT NULL,
    EndDate DATE,
    Payment DECIMAL(10,2),
    RoleContract VARCHAR(50),
    Title_ID INT,
    CreatorID INT,
    FOREIGN KEY (Title_ID) REFERENCES Title(Title_ID),
    FOREIGN KEY (CreatorID) REFERENCES Content_Creator(CreatorID)
);

-- טבלת Creator_Award (פרסים ליוצרים)
CREATE TABLE IF NOT EXISTS Creator_Award (
    AwardID INT PRIMARY KEY,
    AwardName VARCHAR(100) NOT NULL,
    AwardYear INT CHECK (AwardYear >= 1900 AND AwardYear <= EXTRACT(YEAR FROM CURRENT_DATE)),
    CreatorID INT,
    FOREIGN KEY (CreatorID) REFERENCES Content_Creator(CreatorID)
);

-- טבלת Movie (פרטי סרטים - נוצרת מחדש אם לא קיימת)
CREATE TABLE IF NOT EXISTS Movie (
    Title_ID INT PRIMARY KEY,
    Release_Date DATE,
    Duration FLOAT,
    Movie_Type VARCHAR(50),
    FOREIGN KEY (Title_ID) REFERENCES Title(Title_ID) ON DELETE CASCADE
);

-- טבלת Genre (ז'אנרים)
CREATE TABLE IF NOT EXISTS Genre (
    Genre_ID INT PRIMARY KEY,
    Genre_Name VARCHAR(100) NOT NULL UNIQUE
);

-- טבלת MovieGenre (קשר M:M בין סרטים לז'אנרים)
CREATE TABLE IF NOT EXISTS MovieGenre (
    Title_ID INT,
    Genre_ID INT,
    PRIMARY KEY (Title_ID, Genre_ID),
    FOREIGN KEY (Title_ID) REFERENCES Title(Title_ID) ON DELETE CASCADE,
    FOREIGN KEY (Genre_ID) REFERENCES Genre(Genre_ID) ON DELETE CASCADE
);

-- טבלת Content_Award (פרסים לתוכן)
CREATE TABLE IF NOT EXISTS Content_Award (
    AwardID INT PRIMARY KEY,
    Award_Name VARCHAR(100) NOT NULL,
    Given_By VARCHAR(100),
    Award_Year INT,
    Title_ID INT,
    FOREIGN KEY (Title_ID) REFERENCES Title(Title_ID)
);

-- ===========================
-- שלב 4: הרחבת המערכת המקורית שלי
-- ===========================

-- הוספת שדות חדשים לטבלת Customer
ALTER TABLE Customer ADD COLUMN IF NOT EXISTS UserType VARCHAR(20) DEFAULT 'Regular' 
    CHECK (UserType IN ('Regular', 'Premium', 'VIP'));
    
ALTER TABLE Customer ADD COLUMN IF NOT EXISTS AgentID INT;
ALTER TABLE Customer ADD CONSTRAINT IF NOT EXISTS fk_customer_agent 
    FOREIGN KEY (AgentID) REFERENCES Agent(AgentID);

-- הוספת שדה לחיבור Profile ליוצרי תוכן
ALTER TABLE Profile ADD COLUMN IF NOT EXISTS CreatorID INT;
ALTER TABLE Profile ADD CONSTRAINT IF NOT EXISTS fk_profile_creator 
    FOREIGN KEY (CreatorID) REFERENCES Content_Creator(CreatorID);

-- טבלת Feedback משותפת (אם לא קיימת)
CREATE TABLE IF NOT EXISTS Feedback (
    FeedbackID INT PRIMARY KEY,
    FeedbackDate DATE NOT NULL DEFAULT CURRENT_DATE,
    FeedbackRating INT CHECK (FeedbackRating BETWEEN 1 AND 5),
    FeedbackComment TEXT,
    Title_ID INT,
    ProfileID INT,
    FOREIGN KEY (Title_ID) REFERENCES Title(Title_ID),
    FOREIGN KEY (ProfileID) REFERENCES Profile(ProfileID)
);

-- ===========================
-- שלב 5: יצירת אינדקסים לשיפור ביצועים
-- ===========================

-- אינדקסים על טבלאות חדשות
CREATE INDEX IF NOT EXISTS idx_title_name ON Title(Title_Name);
CREATE INDEX IF NOT EXISTS idx_movie_release_date ON Movie(Release_Date);
CREATE INDEX IF NOT EXISTS idx_contract_creator ON Contract(CreatorID);
CREATE INDEX IF NOT EXISTS idx_contract_title ON Contract(Title_ID);

-- אינדקסים על טבלאות מעודכנות
CREATE INDEX IF NOT EXISTS idx_watchhistory_title ON WatchHistory(Title_ID);
CREATE INDEX IF NOT EXISTS idx_reviews_title ON Reviews(Title_ID);
CREATE INDEX IF NOT EXISTS idx_customer_agent ON Customer(AgentID);

-- ===========================
-- שלב 6: יצירת views עזר לאינטגרציה
-- ===========================

-- View של תוכן מלא עם פרטי יוצרים
CREATE OR REPLACE VIEW Complete_Content_View AS
SELECT 
    t.Title_ID,
    t.Title_Name,
    t.Age_Rating,
    t.Content_Type,
    m.Release_Date,
    m.Duration,
    m.Movie_Type,
    cc.Content_CreatorFullName AS Creator_Name,
    cc.Country AS Creator_Country,
    a.AgencyName,
    COUNT(DISTINCT c.ContractID) AS Contract_Count,
    STRING_AGG(DISTINCT g.Genre_Name, ', ') AS Genres
FROM Title t
LEFT JOIN Movie m ON t.Title_ID = m.Title_ID
LEFT JOIN Contract c ON t.Title_ID = c.Title_ID
LEFT JOIN Content_Creator cc ON c.CreatorID = cc.CreatorID
LEFT JOIN Agent a ON cc.AgentID = a.AgentID
LEFT JOIN MovieGenre mg ON t.Title_ID = mg.Title_ID
LEFT JOIN Genre g ON mg.Genre_ID = g.Genre_ID
GROUP BY t.Title_ID, t.Title_Name, t.Age_Rating, t.Content_Type,
         m.Release_Date, m.Duration, m.Movie_Type, cc.Content_CreatorFullName,
         cc.Country, a.AgencyName;

-- View של פעילות לקוחות מורחבת
CREATE OR REPLACE VIEW Extended_Customer_Activity AS
SELECT 
    c.customerID,
    c.firstName || ' ' || c.lastName AS fullName,
    c.UserType,
    a.AgentFullName AS Agent_Name,
    p.profileName,
    w.watchDate,
    w.durationWatched,
    t.Title_Name,
    t.Content_Type,
    m.Release_Date,
    cc.Content_CreatorFullName AS Creator_Name
FROM Customer c
LEFT JOIN Agent a ON c.AgentID = a.AgentID
LEFT JOIN Profile p ON c.customerID = p.customerID
LEFT JOIN WatchHistory w ON p.WatchHistoryID = w.WatchHistoryID
LEFT JOIN Title t ON w.Title_ID = t.Title_ID
LEFT JOIN Movie m ON t.Title_ID = m.Title_ID
LEFT JOIN Contract con ON t.Title_ID = con.Title_ID
LEFT JOIN Content_Creator cc ON con.CreatorID = cc.CreatorID;

-- ===========================
-- שלב 7: הוספת אילוצים ובדיקות
-- ===========================

-- אילוצים על טבלת Contract
ALTER TABLE Contract ADD CONSTRAINT IF NOT EXISTS chk_contract_dates 
    CHECK (EndDate IS NULL OR EndDate >= StartDate);

-- אילוצים על טבלת Movie
ALTER TABLE Movie ADD CONSTRAINT IF NOT EXISTS chk_movie_duration_positive 
    CHECK (Duration IS NULL OR Duration > 0);

-- אילוצים על טבלת Reviews (אם לא קיימים)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints 
                   WHERE constraint_name = 'chk_review_rating') THEN
        ALTER TABLE Reviews ADD CONSTRAINT chk_review_rating 
        CHECK (rating BETWEEN 1 AND 5);
    END IF;
END $$;

-- ===========================
-- שלב 8: הערות ותיעוד
-- ===========================

COMMENT ON TABLE Title IS 'טבלה מרכזית משותפת לכל התוכן במערכת המאוחדת';
COMMENT ON TABLE Content_Creator IS 'יוצרי תוכן מהמערכת החדשה';
COMMENT ON TABLE Agent IS 'סוכנים המייצגים יוצרי תוכן ולקוחות VIP';
COMMENT ON TABLE Contract IS 'חוזים בין יוצרי תוכן לתוכן שנוצר';
COMMENT ON VIEW Complete_Content_View IS 'מבט מלא על תוכן עם פרטי יוצרים וסוכנים';
COMMENT ON VIEW Extended_Customer_Activity IS 'מבט מורחב על פעילות לקוחות כולל יוצרי תוכן';

-- הודעת סיום
SELECT 'Integration completed successfully!' AS Status,
       'Both systems are now integrated' AS Message;
