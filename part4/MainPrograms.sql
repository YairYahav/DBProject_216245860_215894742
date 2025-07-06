-- קובץ תוכניות ראשיות למערכת Streaming Service
-- =====================================================

-- ================================================
-- תוכנית ראשית 1: ניהול המלצות וצפייה
-- ================================================
-- תוכנית המשלבת פונקציה לחישוב המלצות ופרוצדורה לעדכון נתוני צפייה

CREATE OR REPLACE PROCEDURE main_recommendation_and_viewing_management(
    p_profile_id INT,
    p_movie_id INT,
    p_duration_watched FLOAT,
    p_rating INT DEFAULT NULL,
    p_get_recommendations BOOLEAN DEFAULT TRUE
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- משתנים לתוצאות
    recommendation_score DECIMAL(5,2);
    viewing_stats_cursor REFCURSOR;
    stats_record RECORD;
    
    -- משתנים לבקרת זרימה
    operation_success BOOLEAN := TRUE;
    error_count INT := 0;
    
    -- משתנים לנתוני פרופיל
    profile_name VARCHAR;
    customer_name VARCHAR;
    
    -- משתנים לנתוני סרט
    movie_title VARCHAR;
    movie_genre VARCHAR;
    
    -- רשומה לאחסון נתונים זמניים
    temp_rec RECORD;
    
BEGIN
    RAISE NOTICE '=== Starting Recommendation and Viewing Management System ===';
    RAISE NOTICE 'Processing Profile ID: %, Movie ID: %, Duration: % minutes', 
                 p_profile_id, p_movie_id, p_duration_watched;
    
    -- בדיקות קלט ראשוניות
    IF p_profile_id IS NULL OR p_movie_id IS NULL OR p_duration_watched IS NULL THEN
        RAISE EXCEPTION 'Invalid input parameters';
    END IF;
    
    -- קבלת פרטי פרופיל ולקוח
    SELECT p.profileName, c.firstName || ' ' || c.lastName
    INTO profile_name, customer_name
    FROM Profile p
    JOIN Customer c ON p.customerID = c.customerID
    WHERE p.profileID = p_profile_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Profile not found for ID: %', p_profile_id;
    END IF;
    
    -- קבלת פרטי סרט
    SELECT t.Title_Name, COALESCE(g.Genre_Name, 'Unknown')
    INTO movie_title, movie_genre
    FROM Title t
    LEFT JOIN MovieGenre mg ON t.Title_ID = mg.Title_ID
    LEFT JOIN Genre g ON mg.Genre_ID = g.Genre_ID
    WHERE t.Title_ID = p_movie_id
    LIMIT 1;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Movie not found for ID: %', p_movie_id;
    END IF;
    
    RAISE NOTICE 'Processing viewing session:';
    RAISE NOTICE '- Customer: %', customer_name;
    RAISE NOTICE '- Profile: %', profile_name;
    RAISE NOTICE '- Movie: % (Genre: %)', movie_title, movie_genre;
    
    -- שלב 1: חישוב ציון המלצה לפני העדכון (קריאה לפונקציה)
    BEGIN
        SELECT calculate_recommendation_score(p_profile_id, p_movie_id) 
        INTO recommendation_score;
        
        RAISE NOTICE 'Initial recommendation score: %', recommendation_score;
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'Error calculating initial recommendation score: %', SQLERRM;
            recommendation_score := 0.0;
            error_count := error_count + 1;
    END;
    
    -- שלב 2: עדכון נתוני הצפייה (קריאה לפרוצדורה)
    BEGIN
        CALL update_viewing_data_and_recommendations(
            p_profile_id, 
            p_movie_id, 
            p_duration_watched, 
            p_rating
        );
        
        RAISE NOTICE 'Successfully updated viewing data';
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'Error updating viewing data: %', SQLERRM;
            operation_success := FALSE;
            error_count := error_count + 1;
    END;
    
    -- שלב 3: חישוב ציון המלצה מעודכן
    IF operation_success THEN
        BEGIN
            SELECT calculate_recommendation_score(p_profile_id, p_movie_id) 
            INTO temp_rec.new_score;
            
            RAISE NOTICE 'Updated recommendation score: % (Change: %)', 
                         temp_rec.new_score, 
                         temp_rec.new_score - recommendation_score;
            
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING 'Error calculating updated recommendation score: %', SQLERRM;
                error_count := error_count + 1;
        END;
    END IF;
    
    -- שלב 4: יצירת דוח המלצות (אם נתבקש)
    IF p_get_recommendations AND operation_success THEN
        BEGIN
            -- קריאה לפונקציה לקבלת סטטיסטיקות צפייה
            SELECT get_viewing_statistics_report(
                CURRENT_DATE - INTERVAL '30 days',
                CURRENT_DATE,
                movie_genre
            ) INTO viewing_stats_cursor;
            
            RAISE NOTICE 'Generating recommendations based on viewing patterns...';
            
            -- עיבוד תוצאות הסטטיסטיקות
            LOOP
                FETCH viewing_stats_cursor INTO stats_record;
                EXIT WHEN NOT FOUND;
                
                -- הצגת המלצות מובילות (רק 3 הראשונות)
                IF viewing_stats_cursor%ROWCOUNT <= 3 THEN
                    RAISE NOTICE 'Recommendation: % (Genre: %, Popularity: %)', 
                                 stats_record.title_name,
                                 stats_record.genre_name,
                                 stats_record.popularity_level;
                END IF;
            END LOOP;
            
            CLOSE viewing_stats_cursor;
            
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING 'Error generating recommendations: %', SQLERRM;
                error_count := error_count + 1;
        END;
    END IF;
    
    -- שלב 5: סיכום ותוצאות
    RAISE NOTICE '=== Operation Summary ===';
    IF operation_success AND error_count = 0 THEN
        RAISE NOTICE 'All operations completed successfully';
        RAISE NOTICE 'Profile % has new viewing data for "%"', profile_name, movie_title;
        
        -- עדכון נוסף - סימון פרופיל כפעיל
        UPDATE Profile 
        SET isOnline = TRUE 
        WHERE profileID = p_profile_id;
        
    ELSIF error_count > 0 THEN
        RAISE WARNING 'Operation completed with % errors', error_count;
    ELSE
        RAISE WARNING 'Operation failed to complete successfully';
    END IF;
    
    RAISE NOTICE '=== End of Recommendation and Viewing Management ===';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Critical error in main recommendation system: %', SQLERRM;
END;
$$;

-- ================================================
-- תוכנית ראשית 2: ניתוח נתונים וניקוי מערכת
-- ================================================
-- תוכנית המשלבת פונקציה לניתוח סטטיסטיקות ופרוצדורה לניקוי נתונים

CREATE OR REPLACE PROCEDURE main_analytics_and_system_cleanup(
    p_analysis_days INT DEFAULT 30,
    p_cleanup_days INT DEFAULT 180,
    p_cleanup_mode VARCHAR DEFAULT 'SOFT',
    p_genre_filter VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- משתנים לסטטיסטיקות
    stats_cursor REFCURSOR;
    stats_record RECORD;
    total_content_analyzed INT := 0;
    high_performing_content INT := 0;
    
    -- משתנים לניקוי
    cleanup_start_time TIMESTAMP;
    cleanup_end_time TIMESTAMP;
    cleanup_duration INTERVAL;
    
    -- משתנים לדוחות
    report_date DATE := CURRENT_DATE;
    system_health_score DECIMAL(5,2) := 0;
    
    -- רשומות לנתונים מצטברים
    summary_rec RECORD;
    performance_rec RECORD;
    
    -- משתנים לבקרת זרימה
    analysis_success BOOLEAN := TRUE;
    cleanup_success BOOLEAN := TRUE;
    
BEGIN
    RAISE NOTICE '=== Starting Analytics and System Cleanup Process ===';
    RAISE NOTICE 'Analysis Period: % days, Cleanup Threshold: % days, Mode: %', 
                 p_analysis_days, p_cleanup_days, p_cleanup_mode;
    
    cleanup_start_time := NOW();
    
    -- שלב 1: ניתוח סטטיסטיקות מערכת (קריאה לפונקציה)
    BEGIN
        RAISE NOTICE 'Phase 1: Generating viewing statistics report...';
        
        -- קריאה לפונקציה לקבלת דוח מפורט
        SELECT get_viewing_statistics_report(
            CURRENT_DATE - (p_analysis_days || ' days')::INTERVAL,
            CURRENT_DATE,
            p_genre_filter
        ) INTO stats_cursor;
        
        -- עיבוד וניתוח התוצאות
        LOOP
            FETCH stats_cursor INTO stats_record;
            EXIT WHEN NOT FOUND;
            
            total_content_analyzed := total_content_analyzed + 1;
            
            -- זיהוי תוכן בעל ביצועים גבוהים
            IF stats_record.popularity_level = 'High Popularity' 
               AND stats_record.avg_rating >= 4.0 THEN
                high_performing_content := high_performing_content + 1;
                
                RAISE NOTICE 'High-performing content identified: % (Rating: %, Views: %)', 
                             stats_record.title_name,
                             ROUND(stats_record.avg_rating, 2),
                             stats_record.total_views;
            END IF;
            
            -- ניתוח תוכן בעל ביצועים נמוכים
            IF stats_record.total_views < 5 AND stats_record.avg_rating < 2.5 THEN
                RAISE NOTICE 'Low-performing content detected: % (May need review)', 
                             stats_record.title_name;
            END IF;
        END LOOP;
        
        CLOSE stats_cursor;
        
        RAISE NOTICE 'Analysis complete: % content items analyzed, % high-performing', 
                     total_content_analyzed, high_performing_content;
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'Error during statistics analysis: %', SQLERRM;
            analysis_success := FALSE;
    END;
    
    -- שלב 2: חישוב ציון בריאות המערכת
    IF analysis_success THEN
        -- חישוב ציון מבוסס על יחס תוכן מצליח לכלל התוכן
        IF total_content_analyzed > 0 THEN
            system_health_score := (high_performing_content::DECIMAL / total_content_analyzed) * 10;
            
            RAISE NOTICE 'System Health Score: %.2f/10', system_health_score;
            
            -- הערכת מצב המערכת
            CASE 
                WHEN system_health_score >= 7.0 THEN
                    RAISE NOTICE 'System Status: EXCELLENT - High engagement content';
                WHEN system_health_score >= 5.0 THEN
                    RAISE NOTICE 'System Status: GOOD - Balanced content performance';
                WHEN system_health_score >= 3.0 THEN
                    RAISE NOTICE 'System Status: FAIR - Content optimization needed';
                ELSE
                    RAISE NOTICE 'System Status: POOR - Urgent content strategy review required';
            END CASE;
        END IF;
    END IF;
    
    -- שלב 3: ניקוי נתונים ותחזוקה (קריאה לפרוצדורה)
    BEGIN
        RAISE NOTICE 'Phase 2: Starting system cleanup and maintenance...';
        
        -- קריאה לפרוצדורת הניקוי
        CALL cleanup_old_data_and_update_stats(p_cleanup_days, p_cleanup_mode);
        
        cleanup_success := TRUE;
        RAISE NOTICE 'System cleanup completed successfully';
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'Error during system cleanup: %', SQLERRM;
            cleanup_success := FALSE;
    END;
    
    -- שלב 4: דוח מערכת מקיף
    cleanup_end_time := NOW();
    cleanup_duration := cleanup_end_time - cleanup_start_time;
    
    RAISE NOTICE '=== System Analytics and Cleanup Report ===';
    RAISE NOTICE 'Report Date: %', report_date;
    RAISE NOTICE 'Process Duration: %', cleanup_duration;
    RAISE NOTICE 'Analysis Status: %', 
                 CASE WHEN analysis_success THEN 'SUCCESS' ELSE 'FAILED' END;
    RAISE NOTICE 'Cleanup Status: %', 
                 CASE WHEN cleanup_success THEN 'SUCCESS' ELSE 'FAILED' END;
    
    -- סטטיסטיקות מערכת נוכחיות
    FOR summary_rec IN
        SELECT 
            (SELECT COUNT(*) FROM Customer) as total_customers,
            (SELECT COUNT(*) FROM Profile WHERE isOnline = TRUE) as active_profiles,
            (SELECT COUNT(*) FROM WatchHistory 
             WHERE watchDate >= CURRENT_DATE - INTERVAL '7 days') as recent_views,
            (SELECT COUNT(DISTINCT movieID) FROM WatchHistory 
             WHERE watchDate >= CURRENT_DATE - INTERVAL '30 days') as active_content
    LOOP
        RAISE NOTICE 'Current System Statistics:';
        RAISE NOTICE '- Total Customers: %', summary_rec.total_customers;
        RAISE NOTICE '- Active Profiles: %', summary_rec.active_profiles;
        RAISE NOTICE '- Views (Last 7 days): %', summary_rec.recent_views;
        RAISE NOTICE '- Active Content (Last 30 days): %', summary_rec.active_content;
    END LOOP;
    
    -- המלצות לפעולה
    RAISE NOTICE '=== Recommendations ===';
    IF system_health_score < 5.0 THEN
        RAISE NOTICE '- Consider reviewing content acquisition strategy';
        RAISE NOTICE '- Analyze user engagement patterns';
        RAISE NOTICE '- Implement content promotion campaigns';
    END IF;
    
    IF high_performing_content > 0 THEN
        RAISE NOTICE '- Leverage high-performing content for marketing';
        RAISE NOTICE '- Consider acquiring similar content';
    END IF;
    
    IF total_content_analyzed > 100 THEN
        RAISE NOTICE '- Large content catalog detected - consider personalization improvements';
    END IF;
    
    RAISE NOTICE '=== End of Analytics and Cleanup Process ===';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Critical error in analytics and cleanup system: %', SQLERRM;
END;
$$;

-- ================================================
-- דוגמאות לשימוש בתוכניות הראשיות
-- ================================================

-- דוגמה לתוכנית ראשית 1 - ניהול המלצות וצפייה
/*
CALL main_recommendation_and_viewing_management(
    p_profile_id := 1,
    p_movie_id := 101,
    p_duration_watched := 125.5,
    p_rating := 4,
    p_get_recommendations := TRUE
);
*/

-- דוגמה לתוכנית ראשית 2 - ניתוח וניקוי
/*
CALL main_analytics_and_system_cleanup(
    p_analysis_days := 30,
    p_cleanup_days := 180,
    p_cleanup_mode := 'SOFT',
    p_genre_filter := 'Action'
);
*/

-- הצגת כל הפונקציות והפרוצדורות במערכת
SELECT 
    routine_name,
    routine_type,
    data_type as return_type,
    routine_definition
FROM information_schema.routines 
WHERE routine_schema = current_schema()
AND routine_name LIKE '%recommendation%' 
   OR routine_name LIKE '%viewing%' 
   OR routine_name LIKE '%analytics%'
   OR routine_name LIKE '%cleanup%'
ORDER BY routine_type, routine_name;
