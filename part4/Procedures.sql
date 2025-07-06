-- קובץ פרוצדורות מתקדמות למערכת Streaming Service
-- ========================================================

-- ================================================
-- פרוצדורה 1: עדכון נתוני צפייה וחישוב המלצות
-- ================================================
-- הפרוצדורה מבצעת עדכון מקיף של נתוני צפייה ומחשבת המלצות חדשות

CREATE OR REPLACE PROCEDURE update_viewing_data_and_recommendations(
    p_profile_id INT,
    p_movie_id INT,
    p_duration_watched FLOAT,
    p_rating INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- רשומות לאחסון נתונים
    profile_rec RECORD;
    title_rec RECORD;
    watch_rec RECORD;
    
    -- משתנים לחישובים
    new_watch_history_id INT;
    total_watch_time FLOAT := 0;
    recommendation_score DECIMAL(5,2);
    similar_titles_count INT := 0;
    
    -- Cursor למציאת תוכן דומה
    similar_content_cursor CURSOR FOR
        SELECT DISTINCT t2.Title_ID, t2.Title_Name
        FROM Title t1
        JOIN MovieGenre mg1 ON t1.Title_ID = mg1.Title_ID
        JOIN MovieGenre mg2 ON mg1.Genre_ID = mg2.Genre_ID
        JOIN Title t2 ON mg2.Title_ID = t2.Title_ID
        WHERE t1.Title_ID = p_movie_id 
        AND t2.Title_ID != p_movie_id
        LIMIT 5;
    
    -- משתנים לטיפול בחריגים
    invalid_rating EXCEPTION;
    profile_not_found EXCEPTION;
    content_not_found EXCEPTION;
    
BEGIN
    -- בדיקות תקינות קלט
    IF p_profile_id IS NULL OR p_movie_id IS NULL OR p_duration_watched IS NULL THEN
        RAISE EXCEPTION 'Profile ID, Movie ID and Duration cannot be null';
    END IF;
    
    IF p_duration_watched < 0 THEN
        RAISE EXCEPTION 'Duration watched cannot be negative';
    END IF;
    
    IF p_rating IS NOT NULL AND (p_rating < 1 OR p_rating > 5) THEN
        RAISE invalid_rating;
    END IF;
    
    -- בדיקה שהפרופיל קיים
    SELECT INTO profile_rec *
    FROM Profile 
    WHERE profileID = p_profile_id;
    
    IF NOT FOUND THEN
        RAISE profile_not_found;
    END IF;
    
    -- בדיקה שהתוכן קיים
    SELECT INTO title_rec *
    FROM Title 
    WHERE Title_ID = p_movie_id;
    
    IF NOT FOUND THEN
        RAISE content_not_found;
    END IF;
    
    RAISE NOTICE 'Starting viewing data update for Profile: %, Title: %', 
                 profile_rec.profileName, title_rec.Title_Name;
    
    -- 1. יצירת רשומת היסטוריית צפייה חדשה
    SELECT COALESCE(MAX(WatchHistoryID), 0) + 1 INTO new_watch_history_id 
    FROM WatchHistory;
    
    INSERT INTO WatchHistory (WatchHistoryID, movieID, watchDate, durationWatched)
    VALUES (new_watch_history_id, p_movie_id, CURRENT_DATE, p_duration_watched);
    
    RAISE NOTICE 'Inserted new watch history record with ID: %', new_watch_history_id;
    
    -- 2. עדכון טבלת Favorites
    -- בדיקה אם הסרט כבר במועדפים
    SELECT totalTimeWatched INTO total_watch_time
    FROM Favorites 
    WHERE movieID = p_movie_id;
    
    IF FOUND THEN
        -- עדכון זמן צפייה קיים
        UPDATE Favorites 
        SET totalTimeWatched = totalTimeWatched + p_duration_watched,
            lastSeen = CURRENT_DATE
        WHERE movieID = p_movie_id;
        RAISE NOTICE 'Updated existing favorite record for movie %', p_movie_id;
    ELSE
        -- הוספה למועדפים אם זמן הצפייה מעל 30 דקות
        IF p_duration_watched >= 30 THEN
            INSERT INTO Favorites (movieID, lastSeen, totalTimeWatched)
            VALUES (p_movie_id, CURRENT_DATE, p_duration_watched);
            RAISE NOTICE 'Added movie % to favorites', p_movie_id;
        END IF;
    END IF;
    
    -- 3. הוספת/עדכון דירוג אם סופק
    IF p_rating IS NOT NULL THEN
        -- בדיקה אם כבר קיים דירוג מהפרופיל הזה
        SELECT COUNT(*) INTO similar_titles_count
        FROM Reviews 
        WHERE movieID = p_movie_id AND profileID = p_profile_id;
        
        IF similar_titles_count > 0 THEN
            -- עדכון דירוג קיים
            UPDATE Reviews 
            SET rating = p_rating, 
                reviewDate = CURRENT_DATE,
                comment = 'Updated rating via viewing session'
            WHERE movieID = p_movie_id AND profileID = p_profile_id;
            RAISE NOTICE 'Updated existing rating to % for movie %', p_rating, p_movie_id;
        ELSE
            -- הוספת דירוג חדש
            INSERT INTO Reviews (movieID, rating, comment, reviewDate, profileID)
            VALUES (p_movie_id, p_rating, 'Rating from viewing session', CURRENT_DATE, p_profile_id);
            RAISE NOTICE 'Added new rating % for movie %', p_rating, p_movie_id;
        END IF;
    END IF;
    
    -- 4. חישוב וזמנת המלצות לתוכן דומה (לולאה עם Explicit Cursor)
    RAISE NOTICE 'Calculating recommendations for similar content...';
    
    OPEN similar_content_cursor;
    LOOP
        FETCH similar_content_cursor INTO watch_rec;
        EXIT WHEN NOT FOUND;
        
        -- חישוב ציון המלצה לכל תוכן דומה
        SELECT calculate_recommendation_score(p_profile_id, watch_rec.Title_ID) 
        INTO recommendation_score;
        
        RAISE NOTICE 'Recommendation score for "%" (ID: %): %', 
                     watch_rec.Title_Name, watch_rec.Title_ID, recommendation_score;
        
        similar_titles_count := similar_titles_count + 1;
    END LOOP;
    CLOSE similar_content_cursor;
    
    -- 5. עדכון סטטוס פרופיל לאונליין
    UPDATE Profile 
    SET isOnline = TRUE 
    WHERE profileID = p_profile_id;
    
    -- 6. עדכון טבלת MarksAsFavorite אם הדירוג גבוה
    IF p_rating IS NOT NULL AND p_rating >= 4 THEN
        -- בדיקה אם כבר מסומן כמועדף
        SELECT COUNT(*) INTO similar_titles_count
        FROM MarksAsFavorite 
        WHERE profileID = p_profile_id AND movieID = p_movie_id;
        
        IF similar_titles_count = 0 THEN
            INSERT INTO MarksAsFavorite (profileID, movieID)
            VALUES (p_profile_id, p_movie_id);
            RAISE NOTICE 'Marked movie % as favorite due to high rating', p_movie_id;
        END IF;
    END IF;
    
    RAISE NOTICE 'Viewing data update completed successfully';
    
EXCEPTION
    WHEN invalid_rating THEN
        RAISE EXCEPTION 'Rating must be between 1 and 5';
    WHEN profile_not_found THEN
        RAISE EXCEPTION 'Profile with ID % not found', p_profile_id;
    WHEN content_not_found THEN
        RAISE EXCEPTION 'Content with ID % not found', p_movie_id;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error updating viewing data: %', SQLERRM;
END;
$$;

-- ================================================
-- פרוצדורה 2: ניקוי נתונים ישנים ועדכון סטטיסטיקות
-- ================================================
-- הפרוצדורה מנקה נתונים ישנים ומעדכנת סטטיסטיקות מערכת

CREATE OR REPLACE PROCEDURE cleanup_old_data_and_update_stats(
    p_days_threshold INT DEFAULT 365,
    p_cleanup_mode VARCHAR DEFAULT 'SOFT'
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- רשומות לאחסון נתונים
    cleanup_rec RECORD;
    stats_rec RECORD;
    
    -- משתנים לספירות
    deleted_watch_records INT := 0;
    deleted_device_records INT := 0;
    updated_favorites INT := 0;
    inactive_profiles INT := 0;
    
    -- תאריך גבול לניקוי
    cutoff_date DATE;
    
    -- Cursor לפרופילים לא פעילים
    inactive_profiles_cursor CURSOR FOR
        SELECT p.profileID, p.profileName, c.firstName, c.lastName
        FROM Profile p
        JOIN Customer c ON p.customerID = c.customerID
        JOIN WatchHistory wh ON p.WatchHistoryID = wh.WatchHistoryID
        WHERE wh.watchDate < cutoff_date
        GROUP BY p.profileID, p.profileName, c.firstName, c.lastName
        HAVING MAX(wh.watchDate) < cutoff_date;
    
    -- Cursor למכשירים ישנים
    old_devices_cursor CURSOR FOR
        SELECT deviceID, deviceName, customerID, lastSeen
        FROM Devices
        WHERE lastSeen < cutoff_date;
    
    -- חריגים מותאמים אישית
    invalid_threshold EXCEPTION;
    invalid_mode EXCEPTION;
    
BEGIN
    -- בדיקות תקינות
    IF p_days_threshold <= 0 THEN
        RAISE invalid_threshold;
    END IF;
    
    IF p_cleanup_mode NOT IN ('SOFT', 'HARD', 'ARCHIVE') THEN
        RAISE invalid_mode;
    END IF;
    
    -- חישוב תאריך גבול
    cutoff_date := CURRENT_DATE - INTERVAL '%s days' DAY;
    cutoff_date := CURRENT_DATE - (p_days_threshold || ' days')::INTERVAL;
    
    RAISE NOTICE 'Starting data cleanup with mode: %, threshold: % days, cutoff date: %', 
                 p_cleanup_mode, p_days_threshold, cutoff_date;
    
    -- 1. ניקוי רשומות צפייה ישנות (רק במצב HARD)
    IF p_cleanup_mode = 'HARD' THEN
        DELETE FROM WatchHistory 
        WHERE watchDate < cutoff_date;
        GET DIAGNOSTICS deleted_watch_records = ROW_COUNT;
        RAISE NOTICE 'Deleted % old watch history records', deleted_watch_records;
    END IF;
    
    -- 2. טיפול במכשירים ישנים
    OPEN old_devices_cursor;
    LOOP
        FETCH old_devices_cursor INTO cleanup_rec;
        EXIT WHEN NOT FOUND;
        
        CASE p_cleanup_mode
            WHEN 'SOFT' THEN
                -- עדכון לסטטוס לא פעיל
                UPDATE Devices 
                SET deviceName = deviceName || ' (Inactive)'
                WHERE deviceID = cleanup_rec.deviceID
                AND deviceName NOT LIKE '%(Inactive)%';
                
            WHEN 'HARD' THEN
                -- מחיקה מלאה
                DELETE FROM Devices 
                WHERE deviceID = cleanup_rec.deviceID;
                deleted_device_records := deleted_device_records + 1;
                
            WHEN 'ARCHIVE' THEN
                -- כאן יכולנו להעביר לטבלת ארכיון
                RAISE NOTICE 'Would archive device: % (ID: %)', 
                             cleanup_rec.deviceName, cleanup_rec.deviceID;
        END CASE;
    END LOOP;
    CLOSE old_devices_cursor;
    
    RAISE NOTICE 'Processed % old device records', deleted_device_records;
    
    -- 3. עדכון טבלת Favorites - ניקוי רשומות עם זמן צפייה נמוך
    UPDATE Favorites 
    SET totalTimeWatched = 0
    WHERE totalTimeWatched < 10 
    AND lastSeen < cutoff_date;
    GET DIAGNOSTICS updated_favorites = ROW_COUNT;
    
    DELETE FROM Favorites 
    WHERE totalTimeWatched = 0 
    AND p_cleanup_mode = 'HARD';
    
    RAISE NOTICE 'Updated % favorite records with low watch time', updated_favorites;
    
    -- 4. זיהוי ועדכון פרופילים לא פעילים
    OPEN inactive_profiles_cursor;
    LOOP
        FETCH inactive_profiles_cursor INTO cleanup_rec;
        EXIT WHEN NOT FOUND;
        
        -- עדכון סטטוס פרופיל לא פעיל
        UPDATE Profile 
        SET isOnline = FALSE,
            profileName = profileName || ' (Inactive)'
        WHERE profileID = cleanup_rec.profileID
        AND profileName NOT LIKE '%(Inactive)%';
        
        inactive_profiles := inactive_profiles + 1;
        
        RAISE NOTICE 'Marked profile as inactive: % % (ID: %)', 
                     cleanup_rec.firstName, cleanup_rec.lastName, cleanup_rec.profileID;
    END LOOP;
    CLOSE inactive_profiles_cursor;
    
    -- 5. עדכון סטטיסטיקות מערכת - ספירת נתונים נוכחיים
    FOR stats_rec IN 
        SELECT 
            'WatchHistory' as table_name,
            COUNT(*) as record_count,
            MIN(watchDate) as earliest_date,
            MAX(watchDate) as latest_date
        FROM WatchHistory
        WHERE watchDate >= cutoff_date
        
        UNION ALL
        
        SELECT 
            'ActiveProfiles' as table_name,
            COUNT(*) as record_count,
            NULL as earliest_date,
            NULL as latest_date
        FROM Profile 
        WHERE isOnline = TRUE
        
        UNION ALL
        
        SELECT 
            'ActiveDevices' as table_name,
            COUNT(*) as record_count,
            MIN(lastSeen) as earliest_date,
            MAX(lastSeen) as latest_date
        FROM Devices 
        WHERE lastSeen >= cutoff_date
    LOOP
        RAISE NOTICE 'Statistics - %: % records (% to %)', 
                     stats_rec.table_name, stats_rec.record_count, 
                     stats_rec.earliest_date, stats_rec.latest_date;
    END LOOP;
    
    -- סיכום הניקוי
    RAISE NOTICE 'Data cleanup completed successfully:';
    RAISE NOTICE '- Watch records processed: %', deleted_watch_records;
    RAISE NOTICE '- Device records processed: %', deleted_device_records;
    RAISE NOTICE '- Favorites updated: %', updated_favorites;
    RAISE NOTICE '- Inactive profiles marked: %', inactive_profiles;
    
EXCEPTION
    WHEN invalid_threshold THEN
        RAISE EXCEPTION 'Days threshold must be positive';
    WHEN invalid_mode THEN
        RAISE EXCEPTION 'Cleanup mode must be SOFT, HARD, or ARCHIVE';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error during data cleanup: %', SQLERRM;
END;
$$;

-- ================================================
-- דוגמאות לשימוש בפרוצדורות
-- ================================================

-- דוגמה לשימוש בפרוצדורה 1
-- CALL update_viewing_data_and_recommendations(1, 101, 125.5, 4);

-- דוגמה לשימוש בפרוצדורה 2
-- CALL cleanup_old_data_and_update_stats(180, 'SOFT');
