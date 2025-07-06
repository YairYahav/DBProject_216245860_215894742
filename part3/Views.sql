-- Views.sql - מבטים משולבים בין מערכת Streaming Service למערכת ניהול תוכן
-- מערכת שלי (Streaming) + מערכת החבר (Content Management)

-- ===========================
-- מבט 1: Customer Streaming Analytics - נקודת מבט של אגף הלקוחות המקורי
-- ===========================
-- מבט המשלב פעילות לקוחות עם מידע על יוצרי תוכן וסוכנים

CREATE OR REPLACE VIEW Customer_Streaming_Analytics AS
SELECT 
    c.customerID,
    c.firstName || ' ' || c.lastName AS fullName,
    c.UserType,
    c.customerSince,
    a.AgentFullName AS Agent_Name,
    a.AgencyName,
    
    -- סטטיסטיקות צפייה בסיסיות
    COUNT(DISTINCT w.WatchHistoryID) AS totalViews,
    AVG(w.durationWatched) AS avgWatchTime,
    COUNT(DISTINCT f.Title_ID) AS favoritesCount,
    COUNT(DISTINCT r.Title_ID) AS reviewsCount,
    AVG(r.rating) AS avgRating,
    
    -- מידע פיננסי ומכשירים
    COUNT(DISTINCT d.deviceID) AS devicesCount,
    SUM(p.amount) AS totalPayments,
    
    -- סטטיסטיקות תוכן מתקדמות
    COUNT(DISTINCT CASE WHEN t.Content_Type = 'Movie' THEN w.Title_ID END) AS moviesWatched,
    COUNT(DISTINCT CASE WHEN t.Content_Type != 'Movie' THEN w.Title_ID END) AS otherContentWatched,
    
    -- מידע על יוצרי תוכן שהלקוח צופה בהם
    COUNT(DISTINCT cc.CreatorID) AS uniqueCreatorsWatched,
    STRING_AGG(DISTINCT cc.Country, ', ') AS creatorsCountries,
    
    -- מידע על ז'אנרים
    STRING_AGG(DISTINCT g.Genre_Name, ', ') AS favoriteGenres
    
FROM Customer c
LEFT JOIN Agent a ON c.AgentID = a.AgentID
LEFT JOIN Profile pr ON c.customerID = pr.customerID
LEFT JOIN WatchHistory w ON pr.WatchHistoryID = w.WatchHistoryID
LEFT JOIN Title t ON w.Title_ID = t.Title_ID
LEFT JOIN Contract con ON t.Title_ID = con.Title_ID
LEFT JOIN Content_Creator cc ON con.CreatorID = cc.CreatorID
LEFT JOIN MarksAsFavorite mf ON pr.profileID = mf.profileID
LEFT JOIN Favorites f ON mf.Title_ID = f.Title_ID
LEFT JOIN Reviews r ON pr.profileID = r.profileID
LEFT JOIN Devices d ON c.customerID = d.customerID
LEFT JOIN Payment p ON c.customerID = p.customerID
LEFT JOIN MovieGenre mg ON t.Title_ID = mg.Title_ID
LEFT JOIN Genre g ON mg.Genre_ID = g.Genre_ID
GROUP BY 
    c.customerID, c.firstName, c.lastName, c.UserType, c.customerSince,
    a.AgentFullName, a.AgencyName;

-- ===========================
-- מבט 2: Content Performance Analytics - נקודת מבט של אגף ניהול התוכן החדש
-- ===========================
-- מבט המשלב ביצועי תוכן עם פעילות צפייה ויוצרי תוכן

CREATE OR REPLACE VIEW Content_Performance_Analytics AS
SELECT 
    t.Title_ID,
    t.Title_Name,
    t.Age_Rating,
    t.Content_Type,
    
    -- פרטי סרטים/תוכן
    m.Release_Date,
    m.Duration,
    m.Movie_Type,
    
    -- מידע על יוצרי תוכן
    cc.Content_CreatorFullName AS Creator_Name,
    cc.Country AS Creator_Country,
    cc.IsActive AS Creator_Is_Active,
    a.AgencyName AS Creator_Agency,
    
    -- סטטיסטיקות חוזים ופרסים
    COUNT(DISTINCT con.ContractID) AS contractsCount,
    AVG(con.Payment) AS avgContractPayment,
    COUNT(DISTINCT caw.AwardID) AS creatorAwardsCount,
    COUNT(DISTINCT ca.AwardID) AS contentAwardsCount,
    
    -- סטטיסטיקות צפייה מהמערכת המקורית
    COUNT(DISTINCT w.WatchHistoryID) AS viewCount,
    AVG(w.durationWatched) AS avgWatchDuration,
    COUNT(DISTINCT w.Title_ID) / NULLIF(COUNT(DISTINCT pr.customerID), 0) AS viewsPerCustomer,
    
    -- מידע על ביקורות ומועדפים
    COUNT(DISTINCT fav.Title_ID) AS favoritesCount,
    COUNT(DISTINCT r.profileID) AS reviewsCount,
    AVG(r.rating) AS avgRating,
    
    -- מידע על ז'אנרים
    STRING_AGG(DISTINCT g.Genre_Name, ', ') AS genres,
    
    -- מידע פיננסי מהמערכת המקורית
    SUM(p.amount) / NULLIF(COUNT(DISTINCT w.WatchHistoryID), 0) AS revenuePerView
    
FROM Title t
LEFT JOIN Movie m ON t.Title_ID = m.Title_ID
LEFT JOIN Contract con ON t.Title_ID = con.Title_ID
LEFT JOIN Content_Creator cc ON con.CreatorID = cc.CreatorID
LEFT JOIN Agent a ON cc.AgentID = a.AgentID
LEFT JOIN Creator_Award caw ON cc.CreatorID = caw.CreatorID
LEFT JOIN Content_Award ca ON t.Title_ID = ca.Title_ID
LEFT JOIN WatchHistory w ON t.Title_ID = w.Title_ID
LEFT JOIN Profile pr ON w.WatchHistoryID = pr.WatchHistoryID
LEFT JOIN Customer c ON pr.customerID = c.customerID
LEFT JOIN Payment p ON c.customerID = p.customerID
LEFT JOIN Favorites fav ON t.Title_ID = fav.Title_ID
LEFT JOIN Reviews r ON t.Title_ID = r.Title_ID
LEFT JOIN MovieGenre mg ON t.Title_ID = mg.Title_ID
LEFT JOIN Genre g ON mg.Genre_ID = g.Genre_ID
GROUP BY 
    t.Title_ID, t.Title_Name, t.Age_Rating, t.Content_Type,
    m.Release_Date, m.Duration, m.Movie_Type,
    cc.Content_CreatorFullName, cc.Country, cc.IsActive, a.AgencyName;

-- ===========================
-- שאילתות על מבט Customer Analytics
-- ===========================

-- שאילתא 1.1: לקוחות VIP עם יותר מ-5 צפיות שצופים ביוצרים בינלאומיים
-- תיאור: מזהה לקוחות איכות שחשופים לתוכן בינלאומי
/*
SELECT 
    fullName,
    UserType,
    Agent_Name,
    totalViews,
    avgWatchTime,
    uniqueCreatorsWatched,
    creatorsCountries,
    totalPayments
FROM Customer_Streaming_Analytics 
WHERE UserType IN ('Premium', 'VIP')
  AND totalViews > 5
  AND uniqueCreatorsWatched > 0
  AND creatorsCountries IS NOT NULL
ORDER BY totalPayments DESC, uniqueCreatorsWatched DESC;
*/

-- שאילתא 1.2: ניתוח דפוסי צפייה לפי סוג משתמש
-- תיאור: השוואה בין סוגי משתמשים ברמת הפעילות והתשלום
/*
SELECT 
    UserType,
    COUNT(*) AS customers_count,
    AVG(totalViews) AS avg_views_per_customer,
    AVG(avgWatchTime) AS avg_watch_time,
    AVG(totalPayments) AS avg_payments,
    AVG(uniqueCreatorsWatched) AS avg_creators_per_customer,
    COUNT(DISTINCT CASE WHEN Agent_Name IS NOT NULL THEN fullName END) AS customers_with_agents
FROM Customer_Streaming_Analytics 
WHERE totalViews > 0
GROUP BY UserType
ORDER BY avg_payments DESC;
*/

-- ===========================
-- שאילתות על מבט Content Performance
-- ===========================

-- שאילתא 2.1: התוכן הכי מצליח מבחינת צפיות ורווחיות
-- תיאור: תוכן עם הכי הרבה צפיות ורווח גבוה לצפייה
/*
SELECT 
    Title_Name,
    Content_Type,
    Creator_Name,
    Creator_Country,
    viewCount,
    avgRating,
    revenuePerView,
    contractsCount,
    contentAwardsCount
FROM Content_Performance_Analytics 
WHERE viewCount > 0
ORDER BY viewCount DESC, revenuePerView DESC
LIMIT 10;
*/

-- שאילתא 2.2: ניתוח ביצועי יוצרי תוכן לפי מדינה
-- תיאור: השוואה בין יוצרי תוכן ממדינות שונות
/*
SELECT 
    Creator_Country,
    COUNT(DISTINCT Creator_Name) AS creators_count,
    COUNT(DISTINCT Title_ID) AS titles_count,
    AVG(viewCount) AS avg_views_per_title,
    AVG(avgRating) AS avg_rating,
    SUM(contentAwardsCount) AS total_awards,
    AVG(avgContractPayment) AS avg_contract_payment
FROM Content_Performance_Analytics 
WHERE Creator_Country IS NOT NULL
  AND viewCount > 0
GROUP BY Creator_Country
HAVING COUNT(DISTINCT Title_ID) >= 2
ORDER BY avg_views_per_title DESC, avg_rating DESC;
*/

-- ===========================
-- מבטים נוספים לניתוחים מתקדמים
-- ===========================

-- מבט זכיינות ופרסים
CREATE OR REPLACE VIEW Awards_And_Success_Analysis AS
SELECT 
    t.Title_ID,
    t.Title_Name,
    cc.Content_CreatorFullName,
    cc.Country,
    
    -- פרסים
    COUNT(DISTINCT caw.AwardID) AS creator_awards,
    COUNT(DISTINCT ca.AwardID) AS content_awards,
    STRING_AGG(DISTINCT caw.AwardName, ', ') AS creator_award_names,
    STRING_AGG(DISTINCT ca.Award_Name, ', ') AS content_award_names,
    
    -- ביצועי צפייה
    COUNT(DISTINCT w.WatchHistoryID) AS total_views,
    AVG(r.rating) AS avg_rating,
    
    -- רווחיות
    SUM(p.amount) AS total_revenue_generated
    
FROM Title t
LEFT JOIN Contract con ON t.Title_ID = con.Title_ID
LEFT JOIN Content_Creator cc ON con.CreatorID = cc.CreatorID
LEFT JOIN Creator_Award caw ON cc.CreatorID = caw.CreatorID
LEFT JOIN Content_Award ca ON t.Title_ID = ca.Title_ID
LEFT JOIN WatchHistory w ON t.Title_ID = w.Title_ID
LEFT JOIN Reviews r ON t.Title_ID = r.Title_ID
LEFT JOIN Profile pr ON w.WatchHistoryID = pr.WatchHistoryID
LEFT JOIN Customer c ON pr.customerID = c.customerID
LEFT JOIN Payment p ON c.customerID = p.customerID
GROUP BY t.Title_ID, t.Title_Name, cc.Content_CreatorFullName, cc.Country;

-- מבט דפוסי צפייה לפי זמן
CREATE OR REPLACE VIEW Viewing_Patterns_Timeline AS
SELECT 
    DATE(w.watchDate) AS view_date,
    EXTRACT(DOW FROM w.watchDate) AS day_of_week,
    EXTRACT(HOUR FROM w.watchDate) AS hour_of_day,
    
    -- סטטיסטיקות צפייה
    COUNT(*) AS total_views,
    COUNT(DISTINCT w.Title_ID) AS unique_titles_watched,
    COUNT(DISTINCT pr.customerID) AS unique_viewers,
    AVG(w.durationWatched) AS avg_watch_duration,
    
    -- פילוח לפי סוג תוכן
    COUNT(CASE WHEN t.Content_Type = 'Movie' THEN 1 END) AS movie_views,
    COUNT(CASE WHEN t.Content_Type != 'Movie' THEN 1 END) AS other_content_views,
    
    -- מידע על יוצרי תוכן
    COUNT(DISTINCT cc.CreatorID) AS unique_creators,
    COUNT(DISTINCT cc.Country) AS unique_countries
    
FROM WatchHistory w
JOIN Profile pr ON w.WatchHistoryID = pr.WatchHistoryID
JOIN Title t ON w.Title_ID = t.Title_ID
LEFT JOIN Contract con ON t.Title_ID = con.Title_ID
LEFT JOIN Content_Creator cc ON con.CreatorID = cc.CreatorID
GROUP BY DATE(w.watchDate), EXTRACT(DOW FROM w.watchDate), EXTRACT(HOUR FROM w.watchDate)
ORDER BY view_date DESC, hour_of_day;

-- ===========================
-- שאילתות בדיקה נוספות
-- ===========================

-- בדיקת המבטים החדשים
/*
-- בדיקת מבט פרסים והצלחה
SELECT * FROM Awards_And_Success_Analysis 
WHERE creator_awards > 0 OR content_awards > 0
ORDER BY total_views DESC 
LIMIT 5;

-- בדיקת דפוסי צפייה
SELECT 
    day_of_week,
    CASE day_of_week
        WHEN 0 THEN 'ראשון'
        WHEN 1 THEN 'שני'
        WHEN 2 THEN 'שלישי'
        WHEN 3 THEN 'רביעי'
        WHEN 4 THEN 'חמישי'
        WHEN 5 THEN 'שישי'
        WHEN 6 THEN 'שבת'
    END AS day_name,
    AVG(total_views) AS avg_daily_views,
    AVG(avg_watch_duration) AS avg_daily_watch_time
FROM Viewing_Patterns_Timeline 
GROUP BY day_of_week
ORDER BY day_of_week;
*/

-- ===========================
-- הערות ותיעוד
-- ===========================

COMMENT ON VIEW Customer_Streaming_Analytics IS 'מבט אנליטי של לקוחות - משלב מערכת streaming עם מידע על יוצרי תוכן וסוכנים';
COMMENT ON VIEW Content_Performance_Analytics IS 'מבט ביצועי תוכן - משלב נתוני צפייה עם מידע על יוצרים וחוזים';
COMMENT ON VIEW Awards_And_Success_Analysis IS 'מבט ניתוח פרסים והצלחה - קושר בין פרסים לביצועי צפייה';
COMMENT ON VIEW Viewing_Patterns_Timeline IS 'מבט דפוסי צפייה לפי זמן - ניתוח התנהגות צפייה';

-- הצגת רשימת כל המבטים החדשים
SELECT 
    schemaname,
    viewname,
    viewowner
FROM pg_views 
WHERE schemaname = 'public' 
    AND viewname IN (
        'customer_streaming_analytics',
        'content_performance_analytics', 
        'awards_and_success_analysis',
        'viewing_patterns_timeline'
    )
ORDER BY viewname;

-- הודעת סיום
SELECT 'Views integration completed successfully!' AS Status,
       'All views combine both streaming and content management systems' AS Message;
