-- קובץ שינויי טבלאות לתמיכה בתוכניות המתקדמות
-- =========================================================

-- ================================================
-- שיפורי טבלת Profile
-- ================================================

-- הוספת עמודה לזמן פעילות אחרון
ALTER TABLE Profile 
ADD COLUMN IF NOT EXISTS last_activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- הוספת עמודה לספירת התחברויות יומית (לזיהוי פעילות חשודה)
ALTER TABLE Profile 
ADD COLUMN IF NOT EXISTS daily_login_count INT DEFAULT 0;

-- הוספת עמודה לסטטוס חשבון
ALTER TABLE Profile 
ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) DEFAULT 'Active' 
CHECK (account_status IN ('Active', 'Inactive', 'Suspended', 'Trial'));

-- עדכון ערכי ברירת מחדל לפרופילים קיימים
UPDATE Profile 
SET last_activity_timestamp = CURRENT_TIMESTAMP 
WHERE last_activity_timestamp IS NULL;

UPDATE Profile 
SET account_status = 'Active' 
WHERE account_status IS NULL;

-- ================================================
-- שיפורי טבלת WatchHistory
-- ================================================

-- הוספת עמודה לאחוז השלמת הצפייה
ALTER TABLE WatchHistory 
ADD COLUMN IF NOT EXISTS completion_percentage DECIMAL(5,2) DEFAULT 0.0;

-- הוספת עמודה לקטגוריית הצפייה
ALTER TABLE WatchHistory 
ADD COLUMN IF NOT EXISTS viewing_category VARCHAR(20) DEFAULT 'Regular'
CHECK (viewing_category IN ('Regular', 'Binge', 'Sample', 'Rewatch'));

-- הוספת עמודה לזיהוי מכשיר הצפייה
ALTER TABLE WatchHistory 
ADD COLUMN IF NOT EXISTS device_id_used INT;

-- יצירת קישור למכשיר (Foreign Key)
ALTER TABLE WatchHistory 
ADD CONSTRAINT fk_watchhistory_device 
FOREIGN KEY (device_id_used) REFERENCES Devices(deviceID) ON DELETE SET NULL;

-- ================================================
-- שיפורי טבלת Favorites
-- ================================================

-- הוספת עמודה לדירוג מועדפים (1-10)
ALTER TABLE Favorites 
ADD COLUMN IF NOT EXISTS favorite_rating INT DEFAULT 5 
CHECK (favorite_rating BETWEEN 1 AND 10);

-- הוספת עמודה לקטגוריית מועדפים
ALTER TABLE Favorites 
ADD COLUMN IF NOT EXISTS favorite_category VARCHAR(30) DEFAULT 'General'
CHECK (favorite_category IN ('General', 'Must_Watch', 'Guilty_Pleasure', 'Educational', 'Family'));

-- הוספת עמודה למספר פעמים שנצפה
ALTER TABLE Favorites 
ADD COLUMN IF NOT EXISTS view_count INT DEFAULT 1;

-- ================================================
-- שיפורי טבלת Reviews
-- ================================================

-- הוספת עמודה לסוג הביקורת
ALTER TABLE Reviews 
ADD COLUMN IF NOT EXISTS review_type VARCHAR(20) DEFAULT 'User_Review'
CHECK (review_type IN ('User_Review', 'Quick_Rating', 'Detailed_Review', 'Recommendation'));

-- הוספת עמודה לסטטוס הביקורת
ALTER TABLE Reviews 
ADD COLUMN IF NOT EXISTS review_status VARCHAR(15) DEFAULT 'Active'
CHECK (review_status IN ('Active', 'Hidden', 'Flagged', 'Deleted'));

-- הוספת עמודה למספר לייקים על הביקורת
ALTER TABLE Reviews 
ADD COLUMN IF NOT EXISTS helpful_votes INT DEFAULT 0;

-- ================================================
-- שיפורי טבלת Customer
-- ================================================

-- הוספת עמודה לסוג חשבון
ALTER TABLE Customer 
ADD COLUMN IF NOT EXISTS subscription_type VARCHAR(20) DEFAULT 'Basic'
CHECK (subscription_type IN ('Basic', 'Premium', 'Family', 'Student', 'Trial'));

-- הוספת עמודה לסטטוס תשלום
ALTER TABLE Customer 
ADD COLUMN IF NOT EXISTS payment_status VARCHAR(15) DEFAULT 'Current'
CHECK (payment_status IN ('Current', 'Overdue', 'Suspended', 'Cancelled'));

-- הוספת עמודה לזמן פעילות אחרון של הלקוח
ALTER TABLE Customer 
ADD COLUMN IF NOT EXISTS last_login_date DATE DEFAULT CURRENT_DATE;

-- ================================================
-- שיפורי טבלת Devices
-- ================================================

-- הוספת עמודה לסטטוס מכשיר
ALTER TABLE Devices 
ADD COLUMN IF NOT EXISTS device_status VARCHAR(15) DEFAULT 'Active'
CHECK (device_status IN ('Active', 'Inactive', 'Blocked', 'Retired'));

-- הוספת עמודה לזיהוי גרסת אפליקציה
ALTER TABLE Devices 
ADD COLUMN IF NOT EXISTS app_version VARCHAR(20) DEFAULT '1.0.0';

-- הוספת עמודה למיקום גיאוגרפי (לאבטחה)
ALTER TABLE Devices 
ADD COLUMN IF NOT EXISTS last_known_location VARCHAR(100);

-- ================================================
-- יצירת טבלה חדשה לסטטיסטיקות מערכת
-- ================================================

CREATE TABLE IF NOT EXISTS SystemStatistics (
    stat_id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL DEFAULT CURRENT_DATE,
    stat_type VARCHAR(50) NOT NULL,
    stat_value DECIMAL(15,2) NOT NULL,
    stat_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stat_date, stat_type)
);

-- הוספת אינדקס לחיפוש מהיר
CREATE INDEX IF NOT EXISTS idx_system_stats_date_type 
ON SystemStatistics(stat_date, stat_type);

-- ================================================
-- יצירת טבלה לניהול המלצות
-- ================================================

CREATE TABLE IF NOT EXISTS RecommendationCache (
    recommendation_id SERIAL PRIMARY KEY,
    profile_id INT NOT NULL,
    recommended_title_id INT NOT NULL,
    recommendation_score DECIMAL(5,2) NOT NULL,
    recommendation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    is_viewed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (profile_id) REFERENCES Profile(profileID) ON DELETE CASCADE,
    FOREIGN KEY (recommended_title_id) REFERENCES Title(Title_ID) ON DELETE CASCADE,
    UNIQUE(profile_id, recommended_title_id)
);

-- אינדקסים לביצועים
CREATE INDEX IF NOT EXISTS idx_recommendation_profile 
ON RecommendationCache(profile_id, expires_at);

CREATE INDEX IF NOT EXISTS idx_recommendation_score 
ON RecommendationCache(recommendation_score DESC);

-- ================================================
-- יצירת טבלה ללוג פעילויות מערכת
-- ================================================

CREATE TABLE IF NOT EXISTS SystemActivityLog (
    log_id SERIAL PRIMARY KEY,
    activity_type VARCHAR(50) NOT NULL,
    user_id INT,
    profile_id INT,
    activity_details JSONB,
    severity_level VARCHAR(20) DEFAULT 'INFO' 
        CHECK (severity_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- אינדקסים לביצועים וחיפוש
CREATE INDEX IF NOT EXISTS idx_activity_log_type_date 
ON SystemActivityLog(activity_type, created_at);

CREATE INDEX IF NOT EXISTS idx_activity_log_severity 
ON SystemActivityLog(severity_level, created_at);

CREATE INDEX IF NOT EXISTS idx_activity_log_user 
ON SystemActivityLog(user_id, created_at);

-- ================================================
-- אילוצים נוספים לשלמות נתונים
-- ================================================

-- וידוא שדירוגים חיוביים
ALTER TABLE Reviews 
ADD CONSTRAINT chk_rating_positive 
CHECK (rating > 0);

-- וידוא שזמן צפייה חיובי
ALTER TABLE WatchHistory 
ADD CONSTRAINT chk_duration_positive 
CHECK (durationWatched >= 0);

-- וידוא שזמן צפייה כולל במועדפים חיובי
ALTER TABLE Favorites 
ADD CONSTRAINT chk_total_time_positive 
CHECK (totalTimeWatched >= 0);

-- וידוא שגיל דירוג תקין
ALTER TABLE Title 
ADD CONSTRAINT chk_age_rating_valid 
CHECK (Age_Rating >= 0 AND Age_Rating <= 21);

-- ================================================
-- אינדקסים לשיפור ביצועים
-- ================================================

-- אינדקס על תאריך צפייה (לשאילתות זמן)
CREATE INDEX IF NOT EXISTS idx_watchhistory_date 
ON WatchHistory(watchDate);

-- אינדקס על movieID בהיסטוריית צפייה
CREATE INDEX IF NOT EXISTS idx_watchhistory_movie 
ON WatchHistory(movieID);

-- אינדקס משולב על פרופיל ותאריך
CREATE INDEX IF NOT EXISTS idx_profile_activity 
ON Profile(customerID, last_activity_timestamp);

-- אינדקס על ז'אנרים לחיפוש מהיר
CREATE INDEX IF NOT EXISTS idx_moviegenre_genre 
ON MovieGenre(Genre_ID);

-- אינדקס על דירוגים גבוהים
CREATE INDEX IF NOT EXISTS idx_reviews_high_rating 
ON Reviews(rating) WHERE rating >= 4;

-- אינדקס על תשלומים פעילים
CREATE INDEX IF NOT EXISTS idx_payment_active 
ON Payment(customerID, paymentDate) WHERE status = 'Completed';

-- ================================================
-- פונקציה לעדכון אוטומטי של סטטיסטיקות
-- ================================================

CREATE OR REPLACE FUNCTION update_system_statistics()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- עדכון סטטיסטיקות יומיות
    INSERT INTO SystemStatistics (stat_type, stat_value, stat_description)
    VALUES 
        ('daily_active_users', 
         (SELECT COUNT(DISTINCT customerID) FROM Profile WHERE last_activity_timestamp >= CURRENT_DATE),
         'Number of unique active users today'),
        
        ('daily_viewing_hours', 
         (SELECT COALESCE(SUM(durationWatched), 0) / 60.0 FROM WatchHistory WHERE watchDate = CURRENT_DATE),
         'Total viewing hours today'),
        
        ('new_reviews_today', 
         (SELECT COUNT(*) FROM Reviews WHERE reviewDate = CURRENT_DATE),
         'Number of new reviews submitted today'),
        
        ('system_health_score', 
         (SELECT CASE WHEN COUNT(*) > 0 THEN AVG(rating) * 2 ELSE 5.0 END FROM Reviews WHERE reviewDate >= CURRENT_DATE - INTERVAL '7 days'),
         'Average user satisfaction (1-10 scale)')
    ON CONFLICT (stat_date, stat_type) 
    DO UPDATE SET 
        stat_value = EXCLUDED.stat_value,
        stat_description = EXCLUDED.stat_description;
        
    RAISE NOTICE 'System statistics updated for %', CURRENT_DATE;
END;
$$;

-- ================================================
-- הרצת עדכון ראשוני של סטטיסטיקות
-- ================================================

SELECT update_system_statistics();

-- ================================================
-- סיכום השינויים שבוצעו
-- ================================================

SELECT 'AlterTable operations completed successfully. Added columns, constraints, indexes, and new tables for enhanced functionality.' AS status;

-- הצגת מבנה הטבלאות החדש
\d+ Profile;
\d+ WatchHistory;
\d+ Favorites;
\d+ Reviews;
