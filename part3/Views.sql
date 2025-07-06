-- קובץ מבטים ושאילתות למערכת המשולבת
-- ==========================================

-- מבט 1: מנקודת מבט של אגף Streaming Service
-- ==========================================
-- מבט המשלב היסטוריית צפייה עם פרטי התוכן

CREATE VIEW StreamingServiceView AS
SELECT 
    p.profileName,
    c.firstName,
    c.lastName,
    wh.watchDate,
    wh.durationWatched,
    t.Title_Name,
    t.Age_Rating,
    CASE 
        WHEN m.Title_ID IS NOT NULL THEN 'Movie'
        WHEN tv.Title_ID IS NOT NULL THEN 'TV Show'
        ELSE 'Unknown'
    END AS content_type,
    COALESCE(m.Duration, 0) AS movie_duration,
    COALESCE(tv.number_of_seasons, 0) AS tv_seasons,
    f.Franchise_Name,
    r.rating,
    r.comment
FROM Profile p
    JOIN Customer c ON p.customerID = c.customerID
    JOIN WatchHistory wh ON p.WatchHistoryID = wh.WatchHistoryID
    JOIN Title t ON wh.movieID = t.Title_ID
    LEFT JOIN Movie m ON t.Title_ID = m.Title_ID
    LEFT JOIN Tv_show tv ON t.Title_ID = tv.Title_ID
    LEFT JOIN Belongs_to bt ON t.Title_ID = bt.Title_ID
    LEFT JOIN Franchise f ON bt.Franchise_ID = f.Franchise_ID
    LEFT JOIN Reviews r ON t.Title_ID = r.movieID AND r.profileID = p.profileID;

-- מבט 2: מנקודת מבט של אגף ניהול התוכן
-- =====================================
-- מבט המראה ביצועי התוכן מבחינת צפיות ודירוגים

CREATE VIEW ContentManagementView AS
SELECT 
    t.Title_ID,
    t.Title_Name,
    t.Age_Rating,
    CASE 
        WHEN m.Title_ID IS NOT NULL THEN 'Movie'
        WHEN tv.Title_ID IS NOT NULL THEN 'TV Show'
        ELSE 'Unknown'
    END AS content_type,
    f.Franchise_Name,
    g.Genre_Name,
    COUNT(DISTINCT wh.WatchHistoryID) AS total_views,
    AVG(wh.durationWatched) AS avg_watch_duration,
    AVG(r.rating) AS avg_rating,
    COUNT(DISTINCT r.profileID) AS total_reviews,
    COUNT(DISTINCT maf.profileID) AS total_favorites,
    COALESCE(m.Release_Date, NULL) AS release_date,
    COALESCE(m.Duration, 0) AS movie_duration,
    COALESCE(tv.number_of_seasons, 0) AS tv_seasons
FROM Title t
    LEFT JOIN Movie m ON t.Title_ID = m.Title_ID
    LEFT JOIN Tv_show tv ON t.Title_ID = tv.Title_ID
    LEFT JOIN Belongs_to bt ON t.Title_ID = bt.Title_ID
    LEFT JOIN Franchise f ON bt.Franchise_ID = f.Franchise_ID
    LEFT JOIN MovieGenre mg ON t.Title_ID = mg.Title_ID
    LEFT JOIN Genre g ON mg.Genre_ID = g.Genre_ID
    LEFT JOIN WatchHistory wh ON t.Title_ID = wh.movieID
    LEFT JOIN Reviews r ON t.Title_ID = r.movieID
    LEFT JOIN MarksAsFavorite maf ON t.Title_ID = maf.movieID
GROUP BY 
    t.Title_ID, t.Title_Name, t.Age_Rating, content_type, 
    f.Franchise_Name, g.Genre_Name, m.Release_Date, 
    m.Duration, tv.number_of_seasons;

-- ===========================================
-- שאילתות על המבט הראשון (StreamingServiceView)
-- ===========================================

-- שאילתה 1.1: רשימת כל הפרופילים שצפו בתוכן בשנת 2023, כולל שם הלקוח
SELECT 
    profileName,
    firstName || ' ' || lastName AS customer_full_name,
    Title_Name,
    content_type,
    watchDate,
    durationWatched,
    rating
FROM StreamingServiceView 
WHERE EXTRACT(YEAR FROM watchDate) = 2023
ORDER BY watchDate DESC, customer_full_name;

-- שאילתה 1.2: זמן צפייה ממוצע לכל סוג תוכן לפי פרנצ'ייז
SELECT 
    Franchise_Name,
    content_type,
    COUNT(*) AS total_watches,
    AVG(durationWatched) AS avg_watch_time,
    AVG(rating) AS avg_rating
FROM StreamingServiceView 
WHERE Franchise_Name IS NOT NULL
GROUP BY Franchise_Name, content_type
HAVING COUNT(*) > 0
ORDER BY avg_rating DESC, avg_watch_time DESC;

-- ===========================================
-- שאילתות על המבט השני (ContentManagementView)
-- ===========================================

-- שאילתה 2.1: דירוג התוכן הפופולרי ביותר לפי ז'אנר
SELECT 
    Genre_Name,
    Title_Name,
    content_type,
    total_views,
    avg_rating,
    total_favorites,
    RANK() OVER (PARTITION BY Genre_Name ORDER BY total_views DESC, avg_rating DESC) as popularity_rank
FROM ContentManagementView 
WHERE Genre_Name IS NOT NULL AND total_views > 0
ORDER BY Genre_Name, popularity_rank;

-- שאילתה 2.2: ניתוח ביצועים של תוכן לפי פרנצ'ייז
SELECT 
    Franchise_Name,
    COUNT(DISTINCT Title_ID) AS titles_in_franchise,
    SUM(total_views) AS franchise_total_views,
    AVG(avg_rating) AS franchise_avg_rating,
    SUM(total_favorites) AS franchise_total_favorites,
    AVG(avg_watch_duration) AS franchise_avg_watch_duration
FROM ContentManagementView 
WHERE Franchise_Name IS NOT NULL
GROUP BY Franchise_Name
HAVING COUNT(DISTINCT Title_ID) > 0
ORDER BY franchise_total_views DESC, franchise_avg_rating DESC;
