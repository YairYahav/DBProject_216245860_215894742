-- קובץ טריגרים מתקדמים למערכת Streaming Service
-- ======================================================

-- ================================================
-- טריגר 1: עדכון אוטומטי של טבלת Favorites
-- ================================================
-- מעדכן אוטומטית את totalTimeWatched כשמוסיפים או מעדכנים WatchHistory

-- פונקציה לטריגר עדכון Favorites
CREATE OR REPLACE FUNCTION update_favorites_on_watch()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_total_time FLOAT := 0;
    movie_duration FLOAT := 0;
    completion_percentage FLOAT := 0;
    profile_id INT;
    is_significant_watch BOOLEAN := FALSE;
    
    -- רשומה לאחסון נתוני הסרט
    movie_rec RECORD;
    
BEGIN
    -- בדיקה אם זו פעולה על WatchHistory
    IF TG_TABLE_NAME != 'watchhistory' THEN
        RETURN NULL;
    END IF;
    
    -- בדיקות תקינות
    IF NEW.movieID IS NULL OR NEW.durationWatched IS NULL THEN
        RAISE NOTICE 'Invalid watch data: movieID or duration is null';
        RETURN NEW;
    END IF;
    
    -- מציאת פרופיל המשוייך
    SELECT p.profileID INTO profile_id
    FROM Profile p
    WHERE p.WatchHistoryID = NEW.WatchHistoryID;
    
    IF profile_id IS NULL THEN
        RAISE NOTICE 'No profile found for WatchHistoryID: %', NEW.WatchHistoryID;
        RETURN NEW;
    END IF;
    
    -- קבלת פרטי הסרט למחישוב אחוז השלמה
    SELECT INTO movie_rec t.Title_Name, m.Duration
    FROM Title t
    LEFT JOIN Movie m ON t.Title_ID = m.Title_ID
    WHERE t.Title_ID = NEW.movieID;
    
    -- חישוב אחוז השלמה
    IF movie_rec.Duration IS NOT NULL AND movie_rec.Duration > 0 THEN
        completion_percentage := (NEW.durationWatched / movie_rec.Duration) * 100;
        RAISE NOTICE 'Watch completion: %.1f%% for "%"', 
                     completion_percentage, movie_rec.Title_Name;
    END IF;
    
    -- קביעה אם מדובר בצפייה משמעותית (מעל 20% או מעל 15 דקות)
    is_significant_watch := (completion_percentage >= 20.0) OR (NEW.durationWatched >= 15.0);
    
    IF NOT is_significant_watch THEN
        RAISE NOTICE 'Watch duration too short to update favorites';
        RETURN NEW;
    END IF;
    
    -- בדיקה אם הסרט כבר במועדפים
    SELECT totalTimeWatched INTO current_total_time
    FROM Favorites 
    WHERE movieID = NEW.movieID;
    
    IF FOUND THEN
        -- עדכון זמן צפייה קיים
        UPDATE Favorites 
        SET totalTimeWatched = totalTimeWatched + NEW.durationWatched,
            lastSeen = CURRENT_DATE
        WHERE movieID = NEW.movieID;
        
        RAISE NOTICE 'Updated total watch time for movie % to % minutes', 
                     NEW.movieID, current_total_time + NEW.durationWatched;
    ELSE
        -- הוספה חדשה למועדפים אם צפייה משמעותית
        IF NEW.durationWatched >= 30.0 OR completion_percentage >= 50.0 THEN
            INSERT INTO Favorites (movieID, lastSeen, totalTimeWatched)
            VALUES (NEW.movieID, CURRENT_DATE, NEW.durationWatched);
            
            RAISE NOTICE 'Added movie % to favorites with % minutes watch time', 
                         NEW.movieID, NEW.durationWatched;
            
            -- הוספה אוטומטית למועדפי הפרופיל אם צפייה מלאה
            IF completion_percentage >= 80.0 THEN
                INSERT INTO MarksAsFavorite (profileID, movieID)
                VALUES (profile_id, NEW.movieID)
                ON CONFLICT (profileID, movieID) DO NOTHING;
                
                RAISE NOTICE 'Auto-marked as favorite for profile % due to complete viewing', 
                             profile_id;
            END IF;
        END IF;
    END IF;
    
    RETURN NEW;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in update_favorites_on_watch: %', SQLERRM;
        RETURN NEW;
END;
$$;

-- יצירת הטריגר
DROP TRIGGER IF EXISTS trigger_update_favorites ON WatchHistory;

CREATE TRIGGER trigger_update_favorites
    AFTER INSERT OR UPDATE ON WatchHistory
    FOR EACH ROW
    EXECUTE FUNCTION update_favorites_on_watch();

-- ================================================
-- טריגר 2: ניהול סטטוס פרופיל ואבטחה
-- ================================================
-- מעדכן סטטוס פרופיל ובודק הרשאות בהתבסס על פעילות

-- פונקציה לטריגר ניהול פרופיל
CREATE OR REPLACE FUNCTION manage_profile_status_and_security()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    recent_activity_count INT := 0;
    last_activity_date DATE;
    profile_age_days INT := 0;
    customer_payment_status VARCHAR := 'Unknown';
    
    -- רשומות לנתונים נוספים
    customer_rec RECORD;
    activity_rec RECORD;
    
    -- משתנים לבדיקות אבטחה
    suspicious_activity BOOLEAN := FALSE;
    rapid_login_count INT := 0;
    
BEGIN
    -- בדיקה איזה סוג של פעילות הופעל
    CASE TG_OP
        WHEN 'INSERT' THEN
            RAISE NOTICE 'New profile created: %', NEW.profileName;
            
            -- בדיקת פרטי הלקוח
            SELECT INTO customer_rec c.*, 
                   EXTRACT(DAYS FROM (CURRENT_DATE - c.customerSince)) as customer_age_days
            FROM Customer c 
            WHERE c.customerID = NEW.customerID;
            
            IF customer_rec.customer_age_days < 1 THEN
                RAISE NOTICE 'New customer detected, setting up initial profile settings';
                NEW.isOnline := TRUE;
            END IF;
            
            -- בדיקת סטטוס תשלום
            SELECT INTO customer_payment_status 
                CASE 
                    WHEN COUNT(CASE WHEN status = 'Completed' THEN 1 END) > 0 THEN 'Paid'
                    WHEN COUNT(CASE WHEN status = 'Pending' THEN 1 END) > 0 THEN 'Pending'
                    ELSE 'No_Payment'
                END
            FROM Payment 
            WHERE customerID = NEW.customerID 
            AND paymentDate >= CURRENT_DATE - INTERVAL '30 days';
            
            IF customer_payment_status = 'No_Payment' THEN
                RAISE NOTICE 'Customer % has no recent payments - trial account', 
                             NEW.customerID;
            END IF;
            
        WHEN 'UPDATE' THEN
            -- בדיקה אם שונה הסטטוס לאונליין
            IF OLD.isOnline = FALSE AND NEW.isOnline = TRUE THEN
                RAISE NOTICE 'Profile % came online', NEW.profileName;
                
                -- בדיקת פעילות חשודה - התחברויות מהירות
                SELECT COUNT(*) INTO rapid_login_count
                FROM Profile p
                JOIN WatchHistory wh ON p.WatchHistoryID = wh.WatchHistoryID
                WHERE p.customerID = NEW.customerID 
                AND wh.watchDate = CURRENT_DATE;
                
                IF rapid_login_count > 10 THEN
                    suspicious_activity := TRUE;
                    RAISE WARNING 'Suspicious activity detected for customer %: % logins today', 
                                  NEW.customerID, rapid_login_count;
                END IF;
                
                -- עדכון זמן פעילות אחרון
                SELECT MAX(wh.watchDate) INTO last_activity_date
                FROM Profile p
                JOIN WatchHistory wh ON p.WatchHistoryID = wh.WatchHistoryID
                WHERE p.profileID = NEW.profileID;
                
                -- בדיקה אם הפרופיל לא היה פעיל זמן רב
                IF last_activity_date IS NOT NULL THEN
                    profile_age_days := EXTRACT(DAYS FROM (CURRENT_DATE - last_activity_date));
                    
                    IF profile_age_days > 90 THEN
                        RAISE NOTICE 'Welcome back! Profile was inactive for % days', 
                                     profile_age_days;
                        
                        -- איפוס הפרופיל אם לא היה פעיל יותר משנה
                        IF profile_age_days > 365 THEN
                            NEW.profileName := NEW.profileName || ' (Returning User)';
                            RAISE NOTICE 'Marked as returning user due to long inactivity';
                        END IF;
                    END IF;
                END IF;
            END IF;
            
            -- בדיקה אם שונה שם הפרופיל
            IF OLD.profileName != NEW.profileName THEN
                RAISE NOTICE 'Profile name changed from "%" to "%"', 
                             OLD.profileName, NEW.profileName;
                
                -- בדיקה לתוכן לא הולם בשם
                IF NEW.profileName ~* '(admin|root|test|delete)' THEN
                    RAISE WARNING 'Potentially inappropriate profile name: %', NEW.profileName;
                END IF;
            END IF;
            
        WHEN 'DELETE' THEN
            RAISE NOTICE 'Profile deleted: % (ID: %)', OLD.profileName, OLD.profileID;
            
            -- ניקוי נתונים קשורים (אם נדרש)
            DELETE FROM MarksAsFavorite WHERE profileID = OLD.profileID;
            DELETE FROM Reviews WHERE profileID = OLD.profileID;
            
            RAISE NOTICE 'Cleaned up related data for deleted profile %', OLD.profileID;
    END CASE;
    
    -- בדיקות אבטחה נוספות
    IF suspicious_activity THEN
        -- כאן יכולנו לשלוח התראה או לחסום זמנית
        RAISE NOTICE 'Security alert logged for profile %', 
                     COALESCE(NEW.profileID, OLD.profileID);
    END IF;
    
    -- החזרת הרשומה המתאימה בהתבסס על סוג הפעולה
    CASE TG_OP
        WHEN 'DELETE' THEN RETURN OLD;
        ELSE RETURN NEW;
    END CASE;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in profile management trigger: %', SQLERRM;
        CASE TG_OP
            WHEN 'DELETE' THEN RETURN OLD;
            ELSE RETURN NEW;
        END CASE;
END;
$$;

-- יצירת הטריגר
DROP TRIGGER IF EXISTS trigger_manage_profile ON Profile;

CREATE TRIGGER trigger_manage_profile
    BEFORE INSERT OR UPDATE OR DELETE ON Profile
    FOR EACH ROW
    EXECUTE FUNCTION manage_profile_status_and_security();

-- ================================================
-- בדיקות ובדיקת תקינות הטריגרים
-- ================================================

-- הצגת כל הטריגרים במערכת
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_timing,
    action_statement
FROM information_schema.triggers 
WHERE trigger_schema = current_schema()
ORDER BY event_object_table, trigger_name;

-- ================================================
-- דוגמאות לפעילויות שיפעילו את הטריגרים
-- ================================================

-- דוגמה להפעלת טריגר הצפייה:
-- INSERT INTO WatchHistory (WatchHistoryID, movieID, watchDate, durationWatched) 
-- VALUES (9999, 1, CURRENT_DATE, 95.5);

-- דוגמה להפעלת טריגר הפרופיל:
-- UPDATE Profile SET isOnline = TRUE WHERE profileID = 1;
