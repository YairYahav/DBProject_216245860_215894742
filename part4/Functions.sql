-- קובץ פונקציות מתקדמות למערכת Streaming Service
-- =====================================================

-- ================================================
-- פונקציה 1: חישוב ציון המלצה לפרופיל מסוים
-- ================================================
-- הפונקציה מחשבת ציון המלצה לכל תוכן עבור פרופיל נתון
-- מבוססת על: היסטוריית צפייה, ז'אנרים מועדפים, דירוגים וזמן צפייה

CREATE OR REPLACE FUNCTION calculate_recommendation_score(
    p_profile_id INT,
    p_title_id INT
) RETURNS DECIMAL(5,2)
LANGUAGE plpgsql
AS $$
DECLARE
    -- רשומות עבור נתונים
    profile_rec RECORD;
    title_rec RECORD;
    genre_rec RECORD;
    
    -- משתנים לחישובים
    base_score DECIMAL(5,2) := 0;
    genre_bonus DECIMAL(5,2) := 0;
    franchise_bonus DECIMAL(5,2) := 0;
    rating_bonus DECIMAL(5,2) := 0;
    final_score DECIMAL(5,2) := 0;
    
    -- Cursor עבור ז'אנרים שהפרופיל אוהב
    preferred_genres_cursor CURSOR FOR
        SELECT g.Genre_Name, COUNT(*) as preference_count
        FROM WatchHistory wh
        JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID
        JOIN Title t ON wh.movieID = t.Title_ID
        JOIN MovieGenre mg ON t.Title_ID = mg.Title_ID
        JOIN Genre g ON mg.Genre_ID = g.Genre_ID
        WHERE p.profileID = p_profile_id
        GROUP BY g.Genre_Name
        ORDER BY preference_count DESC;
        
    -- משתנים לטיפול בחריגים
    division_by_zero EXCEPTION;
    
BEGIN
    -- בדיקת קלט תקין
    IF p_profile_id IS NULL OR p_title_id IS NULL THEN
        RAISE EXCEPTION 'Profile ID and Title ID cannot be null';
    END IF;
    
    -- בדיקה שהפרופיל קיים
    SELECT INTO profile_rec profileID, profileName 
    FROM Profile 
    WHERE profileID = p_profile_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Profile with ID % not found', p_profile_id;
    END IF;
    
    -- בדיקה שהתוכן קיים
    SELECT INTO title_rec Title_ID, Title_Name, Age_Rating
    FROM Title 
    WHERE Title_ID = p_title_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Title with ID % not found', p_title_id;
    END IF;
    
    -- חישוב ציון בסיס על פי דירוג גיל
    CASE 
        WHEN title_rec.Age_Rating <= 13 THEN base_score := 3.0;
        WHEN title_rec.Age_Rating <= 16 THEN base_score := 3.5;
        ELSE base_score := 4.0;
    END CASE;
    
    -- בונוס לפי ז'אנרים מועדפים (Explicit Cursor)
    OPEN preferred_genres_cursor;
    LOOP
        FETCH preferred_genres_cursor INTO genre_rec;
        EXIT WHEN NOT FOUND;
        
        -- בדיקה אם התוכן שייך לז'אנר המועדף
        SELECT COUNT(*) INTO genre_bonus
        FROM MovieGenre mg
        JOIN Genre g ON mg.Genre_ID = g.Genre_ID
        WHERE mg.Title_ID = p_title_id 
        AND g.Genre_Name = genre_rec.Genre_Name;
        
        IF genre_bonus > 0 THEN
            -- הוספת בונוס לפי מידת ההעדפה
            base_score := base_score + (genre_rec.preference_count * 0.5);
            EXIT; -- יצאנו אחרי שמצאנו התאמה
        END IF;
    END LOOP;
    CLOSE preferred_genres_cursor;
    
    -- בונוס לפי פרנצ'ייז מועדף
    SELECT COUNT(*) INTO franchise_bonus
    FROM Belongs_to bt1
    JOIN Belongs_to bt2 ON bt1.Franchise_ID = bt2.Franchise_ID
    JOIN WatchHistory wh ON bt2.Title_ID = wh.movieID
    JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID
    WHERE bt1.Title_ID = p_title_id 
    AND p.profileID = p_profile_id;
    
    IF franchise_bonus > 0 THEN
        base_score := base_score + 2.0;
    END IF;
    
    -- בונוס לפי דירוג ממוצע של התוכן
    SELECT COALESCE(AVG(rating), 0) INTO rating_bonus
    FROM Reviews 
    WHERE movieID = p_title_id;
    
    base_score := base_score + (rating_bonus * 0.3);
    
    -- חישוב ציון סופי
    final_score := LEAST(base_score, 10.0); -- מקסימום 10
    
    RETURN final_score;
    
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE 'Division by zero detected in score calculation';
        RETURN 0.0;
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in recommendation calculation: %', SQLERRM;
        RETURN 0.0;
END;
$$;

-- ================================================
-- פונקציה 2: דוח סטטיסטיקות צפייה מתקדם
-- ================================================
-- הפונקציה מחזירה Ref Cursor עם נתונים מפורטים על פעילות הצפייה

CREATE OR REPLACE FUNCTION get_viewing_statistics_report(
    p_start_date DATE DEFAULT NULL,
    p_end_date DATE DEFAULT NULL,
    p_genre_filter VARCHAR DEFAULT NULL
) RETURNS REFCURSOR
LANGUAGE plpgsql
AS $$
DECLARE
    stats_cursor REFCURSOR := 'viewing_stats_cursor';
    sql_query TEXT;
    where_clause TEXT := '';
    date_filter TEXT := '';
    genre_filter TEXT := '';
    
    -- משתנים לספירות
    total_views INTEGER := 0;
    total_customers INTEGER := 0;
    
    -- רשומה עבור נתונים זמניים
    temp_rec RECORD;
    
BEGIN
    -- הגדרת תאריכים ברירת מחדל
    IF p_start_date IS NULL THEN
        p_start_date := CURRENT_DATE - INTERVAL '30 days';
    END IF;
    
    IF p_end_date IS NULL THEN
        p_end_date := CURRENT_DATE;
    END IF;
    
    -- בדיקת תקינות תאריכים
    IF p_start_date > p_end_date THEN
        RAISE EXCEPTION 'Start date cannot be later than end date';
    END IF;
    
    -- בניית תנאי WHERE דינמי
    date_filter := FORMAT('wh.watchDate BETWEEN ''%s'' AND ''%s''', p_start_date, p_end_date);
    
    IF p_genre_filter IS NOT NULL THEN
        genre_filter := FORMAT(' AND g.Genre_Name = ''%s''', p_genre_filter);
    END IF;
    
    where_clause := 'WHERE ' || date_filter || genre_filter;
    
    -- בניית השאילתה הדינמית
    sql_query := '
        SELECT 
            g.Genre_Name,
            t.Title_Name,
            COUNT(DISTINCT p.profileID) as unique_viewers,
            COUNT(*) as total_views,
            AVG(wh.durationWatched) as avg_watch_duration,
            SUM(wh.durationWatched) as total_watch_time,
            AVG(r.rating) as avg_rating,
            CASE 
                WHEN COUNT(*) > 100 THEN ''High Popularity''
                WHEN COUNT(*) > 50 THEN ''Medium Popularity''
                ELSE ''Low Popularity''
            END as popularity_level
        FROM WatchHistory wh
        JOIN Profile p ON p.WatchHistoryID = wh.WatchHistoryID
        JOIN Title t ON wh.movieID = t.Title_ID
        LEFT JOIN MovieGenre mg ON t.Title_ID = mg.Title_ID
        LEFT JOIN Genre g ON mg.Genre_ID = g.Genre_ID
        LEFT JOIN Reviews r ON t.Title_ID = r.movieID
        ' || where_clause || '
        GROUP BY g.Genre_Name, t.Title_Name, t.Title_ID
        ORDER BY total_views DESC, avg_rating DESC';
    
    -- פתיחת הקרסור
    OPEN stats_cursor FOR EXECUTE sql_query;
    
    -- לוג למעקב
    GET DIAGNOSTICS total_views = ROW_COUNT;
    RAISE NOTICE 'Generated viewing statistics report for period % to %, found % records', 
                 p_start_date, p_end_date, total_views;
    
    RETURN stats_cursor;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error generating viewing statistics: %', SQLERRM;
        -- החזרת קרסור ריק במקרה של שגיאה
        OPEN stats_cursor FOR SELECT NULL::TEXT as error_message;
        RETURN stats_cursor;
END;
$$;

-- ================================================
-- דוגמאות לשימוש בפונקציות
-- ================================================

-- דוגמה לשימוש בפונקציה 1
-- SELECT calculate_recommendation_score(1, 101) as recommendation_score;

-- דוגמה לשימוש בפונקציה 2
-- BEGIN;
-- SELECT get_viewing_statistics_report('2023-01-01', '2023-12-31', 'Action');
-- FETCH ALL FROM viewing_stats_cursor;
-- COMMIT;
