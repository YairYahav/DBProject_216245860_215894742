-- Insert_Sample_Data.sql - הכנסת נתונים משולבים לשתי המערכות
-- מערכת Streaming Service + מערכת ניהול תוכן עם יוצרים וסוכנים

-- ===========================
-- שלב 1: הכנסת נתונים בסיסיים - ז'אנרים וסוכנים
-- ===========================

-- הכנסת ז'אנרים
INSERT INTO Genre (Genre_ID, Genre_Name) VALUES
(1, 'אקשן'),
(2, 'קומדיה'),
(3, 'דרמה'),
(4, 'מדע בדיוני'),
(5, 'מותחן'),
(6, 'רומנטיקה'),
(7, 'אימה'),
(8, 'אנימציה'),
(9, 'תיעודי'),
(10, 'משפחתי'),
(11, 'פנטזיה'),
(12, 'פשע'),
(13, 'היסטוריה'),
(14, 'מוזיקה'),
(15, 'מערבון')
ON CONFLICT (Genre_ID) DO NOTHING;

-- הכנסת סוכנים
INSERT INTO Agent (AgentID, AgentFullName, AgencyName, PhoneNumber, Email) VALUES
(1, 'מיכאל כהן', 'כהן אנטרטיינמנט', '052-1234567', 'michael@cohen-ent.com'),
(2, 'שרה לוי', 'סוכנות הכוכבים', '053-2345678', 'sarah@stars-agency.com'),
(3, 'דוד ישראלי', 'ישראלי הפקות', '054-3456789', 'david@israeli-prod.com'),
(4, 'רחל אברמוביץ', 'אברמוביץ וחברים', '055-4567890', 'rachel@abramovich.com'),
(5, 'יוסי גולדשטין', 'גולד מדיה', '056-5678901', 'yossi@goldmedia.com'),
(6, 'אנה רוזנברג', 'רוזנברג אמנויות', '057-6789012', 'anna@rosenberg-arts.com'),
(7, 'תומר שחר', 'שחר סטודיו', '058-7890123', 'tomer@shahar-studio.com')
ON CONFLICT (AgentID) DO NOTHING;

-- ===========================
-- שלב 2: הכנסת יוצרי תוכן
-- ===========================

INSERT INTO Content_Creator (CreatorID, Content_CreatorFullName, BirthDate, Country, IsActive, JoinDate, AgentID) VALUES
(1, 'שי אבני', '1985-03-15', 'ישראל', TRUE, '2020-01-01', 1),
(2, 'מיה רוזן', '1990-07-22', 'ישראל', TRUE, '2019-06-15', 2),
(3, 'אלון גור', '1982-11-08', 'ישראל', TRUE, '2018-03-20', 3),
(4, 'נועה כץ', '1988-05-12', 'ישראל', TRUE, '2021-02-10', 4),
(5, 'רון אדלר', '1975-09-30', 'ישראל', FALSE, '2015-08-05', 5),
(6, 'כריסטופר נולן', '1970-07-30', 'בריטניה', TRUE, '2005-05-20', 6),
(7, 'גרטה גרוויג', '1983-08-04', 'ארצות הברית', TRUE, '2015-03-15', 7),
(8, 'קווין פייגי', '1973-06-02', 'ארצות הברית', TRUE, '2010-01-01', 1),
(9, 'וינס גיליגן', '1967-02-10', 'ארצות הברית', TRUE, '2008-01-01', 2),
(10, 'דנה ויט', '1975-12-25', 'ארצות הברית', TRUE, '2011-04-15', 3)
ON CONFLICT (CreatorID) DO NOTHING;

-- ===========================
-- שלב 3: הכנסת כותרות (Title)
-- ===========================

INSERT INTO Title (Title_ID, Title_Name, Age_Rating, Sequel_ID, Content_Type) VALUES
-- סרטים
(101, 'אוונג''רס: אינדגיים', 'PG-13', NULL, 'Movie'),
(102, 'דון קיחוטה', '12', NULL, 'Movie'),
(103, 'האביר האפל', 'PG-13', NULL, 'Movie'),
(104, 'טיטניק', 'PG-13', NULL, 'Movie'),
(105, 'מטריקס', 'R', NULL, 'Movie'),
(106, 'מטריקס 2', 'R', 105, 'Movie'),
(107, 'לה לה לנד', 'PG-13', NULL, 'Movie'),
(108, 'אווטר', 'PG-13', NULL, 'Movie'),
-- סדרות
(201, 'שבירת שורות', 'MA', NULL, 'TV Show'),
(202, 'משחקי הכס', 'MA', NULL, 'TV Show'),
(203, 'דבר מוזר', '14', NULL, 'TV Show'),
(204, 'החברים', 'PG', NULL, 'TV Show'),
(205, 'משרד הנייר', 'PG', NULL, 'TV Show'),
(206, 'שרלוק', '14', NULL, 'TV Show'),
(207, 'הכתר', 'MA', NULL, 'TV Show'),
(208, 'וסטוורלד', 'MA', NULL, 'TV Show')
ON CONFLICT (Title_ID) DO NOTHING;

-- ===========================
-- שלב 4: הכנסת פרטי סרטים
-- ===========================

INSERT INTO Movie (Title_ID, Release_Date, Duration, Movie_Type) VALUES
(101, '2019-04-26', 181, 'Superhero Action'),
(102, '2021-03-15', 142, 'Drama Comedy'),
(103, '2008-07-18', 152, 'Action Thriller'),
(104, '1997-12-19', 195, 'Romance Drama'),
(105, '1999-03-31', 136, 'Sci-Fi Action'),
(106, '2003-05-15', 138, 'Sci-Fi Action'),
(107, '2016-12-09', 128, 'Musical Romance'),
(108, '2009-12-18', 162, 'Sci-Fi Adventure')
ON CONFLICT (Title_ID) DO NOTHING;

-- ===========================
-- שלב 5: הכנסת חוזים
-- ===========================

INSERT INTO Contract (ContractID, StartDate, EndDate, Payment, RoleContract, Title_ID, CreatorID) VALUES
(1, '2019-01-01', '2019-12-31', 500000.00, 'Director', 101, 8),
(2, '2020-06-01', '2021-06-01', 300000.00, 'Director', 102, 1),
(3, '2008-01-01', '2008-12-31', 400000.00, 'Director', 103, 6),
(4, '1996-01-01', '1997-12-31', 600000.00, 'Director', 104, 6),
(5, '1999-01-01', '1999-12-31', 450000.00, 'Director', 105, 6),
(6, '2003-01-01', '2003-12-31', 475000.00, 'Director', 106, 6),
(7, '2016-01-01', '2016-12-31', 350000.00, 'Director', 107, 7),
(8, '2009-01-01', '2009-12-31', 550000.00, 'Director', 108, 6),
(9, '2008-01-01', '2013-12-31', 800000.00, 'Creator', 201, 9),
(10, '2011-01-01', '2019-12-31', 1200000.00, 'Creator', 202, 10),
(11, '2016-01-01', '2022-12-31', 600000.00, 'Creator', 203, 2),
(12, '1994-01-01', '2004-12-31', 400000.00, 'Creator', 204, 3),
(13, '2005-01-01', '2013-12-31', 300000.00, 'Creator', 205, 4),
(14, '2010-01-01', '2017-12-31', 450000.00, 'Creator', 206, 5),
(15, '2016-01-01', '2023-12-31', 700000.00, 'Creator', 207, 1),
(16, '2016-01-01', '2022-12-31', 900000.00, 'Creator', 208, 9)
ON CONFLICT (ContractID) DO NOTHING;

-- ===========================
-- שלב 6: הכנסת פרסים ליוצרים
-- ===========================

INSERT INTO Creator_Award (AwardID, AwardName, AwardYear, CreatorID) VALUES
(1, 'פרס האמי לבימוי', 2021, 1),
(2, 'פרס הגלובוס הזהב', 2020, 2),
(3, 'פרס אוסקר לתסריט', 2019, 3),
(4, 'פרס BAFTA', 2022, 6),
(5, 'פרס גילדת הבימאים', 2018, 8),
(6, 'פרס אמי לסדרה הטובה ביותר', 2014, 9),
(7, 'פרס אמי לסדרה הטובה ביותר', 2018, 10),
(8, 'פרס הבחירה של העם', 2017, 2),
(9, 'פרס אוסקר לבימוי', 2009, 6),
(10, 'פרס גלובוס זהב לבימוי', 2017, 7)
ON CONFLICT (AwardID) DO NOTHING;

-- ===========================
-- שלב 7: הכנסת פרסים לתוכן
-- ===========================

INSERT INTO Content_Award (AwardID, Award_Name, Given_By, Award_Year, Title_ID) VALUES
(1, 'Best Visual Effects', 'Academy Awards', 2019, 101),
(2, 'Best Picture', 'Academy Awards', 1997, 104),
(3, 'Best Cinematography', 'Academy Awards', 1999, 105),
(4, 'Best Original Score', 'Academy Awards', 2016, 107),
(5, 'Outstanding Drama Series', 'Emmy Awards', 2014, 201),
(6, 'Outstanding Drama Series', 'Emmy Awards', 2018, 202),
(7, 'Outstanding Science Fiction Series', 'Saturn Awards', 2017, 203),
(8, 'Outstanding Comedy Series', 'Emmy Awards', 2002, 204),
(9, 'Best Drama Series', 'Golden Globe Awards', 2021, 207),
(10, 'Outstanding Drama Series', 'Emmy Awards', 2018, 208)
ON CONFLICT (AwardID) DO NOTHING;

-- ===========================
-- שלב 8: הכנסת קשרי ז'אנרים
-- ===========================

INSERT INTO MovieGenre (Title_ID, Genre_ID) VALUES
-- אוונג'רס - אקשן + מדע בדיוני
(101, 1), (101, 4),
-- דון קיחוטה - דרמה + קומדיה
(102, 3), (102, 2),
-- האביר האפל - אקשן + פשע
(103, 1), (103, 12),
-- טיטניק - רומנטיקה + דרמה + היסטוריה
(104, 6), (104, 3), (104, 13),
-- מטריקס - מדע בדיוני + אקשן
(105, 4), (105, 1),
(106, 4), (106, 1),
-- לה לה לנד - מוזיקה + רומנטיקה
(107, 14), (107, 6),
-- אווטר - מדע בדיוני + פנטזיה
(108, 4), (108, 11),
-- שבירת שורות - דרמה + פשע + מותחן
(201, 3), (201, 12), (201, 5),
-- משחקי הכס - דרמה + פנטזיה + אקשן
(202, 3), (202, 11), (202, 1),
-- דבר מוזר - מדע בדיוני + מותחן + אימה
(203, 4), (203, 5), (203, 7),
-- החברים - קומדיה + רומנטיקה
(204, 2), (204, 6),
-- משרד הנייר - קומדיה
(205, 2),
-- שרלוק - מותחן + פשע + דרמה
(206, 5), (206, 12), (206, 3),
-- הכתר - דרמה + היסטוריה
(207, 3), (207, 13),
-- וסטוורלד - מדע בדיוני + מותחן + אקשן
(208, 4), (208, 5), (208, 1)
ON CONFLICT (Title_ID, Genre_ID) DO NOTHING;

-- ===========================
-- שלב 9: עדכון לקוחות קיימים עם סוכנים
-- ===========================

-- עדכון לקוחות קיימים עם סוגי משתמש וסוכנים
UPDATE Customer 
SET UserType = 'Premium', AgentID = 1
WHERE customerID IN (SELECT customerID FROM Customer LIMIT 3);

UPDATE Customer 
SET UserType = 'VIP', AgentID = 2
WHERE customerID IN (
    SELECT customerID FROM Customer 
    WHERE UserType IS NULL OR UserType = 'Regular'
    LIMIT 2
);

UPDATE Customer 
SET UserType = COALESCE(UserType, 'Regular')
WHERE UserType IS NULL;

-- ===========================
-- שלב 10: עדכון היסטוריית צפייה עם Title_ID
-- ===========================

-- עדכון WatchHistory להתייחס לכותרות החדשות
UPDATE WatchHistory 
SET Title_ID = 101 
WHERE WatchHistoryID IN (
    SELECT WatchHistoryID FROM WatchHistory 
    WHERE Title_ID IS NULL OR Title_ID = 101
    LIMIT 3
);

UPDATE WatchHistory 
SET Title_ID = 201 
WHERE WatchHistoryID IN (
    SELECT WatchHistoryID FROM WatchHistory 
    WHERE Title_ID IS NULL OR Title_ID = 102
    LIMIT 2
);

UPDATE WatchHistory 
SET Title_ID = 203 
WHERE WatchHistoryID IN (
    SELECT WatchHistoryID FROM WatchHistory 
    WHERE Title_ID IS NULL OR Title_ID = 103
    LIMIT 2
);

-- הכנסת היסטוריית צפייה חדשה
INSERT INTO WatchHistory (WatchHistoryID, Title_ID, watchDate, durationWatched) 
SELECT 
    COALESCE(MAX(WatchHistoryID), 0) + ROW_NUMBER() OVER () AS WatchHistoryID,
    Title_ID,
    CURRENT_DATE - (random() * 365)::int AS watchDate,
    (random() * 120 + 30)::int AS durationWatched
FROM (
    SELECT UNNEST(ARRAY[101, 102, 103, 104, 105, 201, 202, 203, 204, 205]) AS Title_ID
) t
CROSS JOIN (SELECT MAX(WatchHistoryID) FROM WatchHistory) m;

-- ===========================
-- שלב 11: עדכון ביקורות ומועדפים
-- ===========================

-- עדכון Reviews עם Title_ID חדש
INSERT INTO Reviews (profileID, Title_ID, rating, comment, reviewDate) VALUES
(1, 101, 5, 'סרט מדהים! האקשן ברמה גבוהה והסיום מרגש', '2023-05-15'),
(2, 201, 5, 'הסדרה הטובה ביותר שראיתי! כתיבה מבריקה', '2023-06-20'),
(3, 203, 4, 'נוסטלגיה ל-80 במיטבה, מתח ופעילות מעולים', '2023-07-10'),
(1, 104, 4, 'קלאסיקה רומנטית, אם כי קצת ארוכה', '2023-08-05'),
(2, 105, 5, 'מהפכה קולנועית! השפיע על כל הסרטים שאחריו', '2023-09-12'),
(3, 202, 3, 'התחילה מעולה אבל הסוף מאכזב', '2023-10-01')
ON CONFLICT (profileID, Title_ID) DO NOTHING;

-- עדכון Favorites עם Title_ID
INSERT INTO Favorites (Title_ID, lastSeen, totalTimeWatched) VALUES
(101, '2023-11-01', 181.0),
(102, '2023-11-02', 142.0),
(103, '2023-11-03', 152.0),
(201, '2023-11-04', 2820.0), -- 60 פרקים * 47 דקות
(203, '2023-11-05', 1600.0)  -- 32 פרקים * 50 דקות
ON CONFLICT (Title_ID) DO NOTHING;

-- עדכון MarksAsFavorite
INSERT INTO MarksAsFavorite (profileID, Title_ID) VALUES
(1, 101), (1, 105), (1, 201),
(2, 102), (2, 104), (2, 203),
(3, 103), (3, 202), (3, 207)
ON CONFLICT (profileID, Title_ID) DO NOTHING;

-- ===========================
-- שלב 12: הכנסת משוב (Feedback)
-- ===========================

INSERT INTO Feedback (FeedbackID, FeedbackDate, FeedbackRating, FeedbackComment, Title_ID, ProfileID) VALUES
(1, '2023-12-01', 5, 'תוכן מעולה! ממליץ בחום', 101, 1),
(2, '2023-12-02', 4, 'סדרה מרתקת עם עלילה מעולה', 201, 2),
(3, '2023-12-03', 5, 'יצירת מופת קולנועית', 104, 3),
(4, '2023-12-04', 3, 'בסדר אבל יכול היה להיות יותר טוב', 102, 1),
(5, '2023-12-05', 5, 'קלאסיקה שלא מזדקנת', 105, 2),
(6, '2023-12-06', 4, 'בידור משפחתי מעולה', 203, 3)
ON CONFLICT (FeedbackID) DO NOTHING;

-- ===========================
-- שלב 13: בדיקות לאחר הכנסת הנתונים
-- ===========================

-- בדיקת מספר רשומות בטבלאות עיקריות
SELECT 'Title' as table_name, COUNT(*) as row_count FROM Title
UNION ALL
SELECT 'Movie', COUNT(*) FROM Movie
UNION ALL
SELECT 'Content_Creator', COUNT(*) FROM Content_Creator
UNION ALL
SELECT 'Agent', COUNT(*) FROM Agent
UNION ALL
SELECT 'Contract', COUNT(*) FROM Contract
UNION ALL
SELECT 'Genre', COUNT(*) FROM Genre
UNION ALL
SELECT 'MovieGenre', COUNT(*) FROM MovieGenre
UNION ALL
SELECT 'Creator_Award', COUNT(*) FROM Creator_Award
UNION ALL
SELECT 'Content_Award', COUNT(*) FROM Content_Award
UNION ALL
SELECT 'WatchHistory', COUNT(*) FROM WatchHistory
UNION ALL
SELECT 'Reviews', COUNT(*) FROM Reviews
UNION ALL
SELECT 'Favorites', COUNT(*) FROM Favorites
UNION ALL
SELECT 'Customer', COUNT(*) FROM Customer
ORDER BY table_name;

-- בדיקת חיבורים והקשרים
SELECT 
    t.Title_Name,
    t.Content_Type,
    cc.Content_CreatorFullName AS Creator,
    a.AgentFullName AS Agent,
    STRING_AGG(g.Genre_Name, ', ') AS Genres
FROM Title t
LEFT JOIN Contract con ON t.Title_ID = con.Title_ID
LEFT JOIN Content_Creator cc ON con.CreatorID = cc.CreatorID
LEFT JOIN Agent a ON cc.AgentID = a.AgentID
LEFT JOIN MovieGenre mg ON t.Title_ID = mg.Title_ID
LEFT JOIN Genre g ON mg.Genre_ID = g.Genre_ID
GROUP BY t.Title_ID, t.Title_Name, t.Content_Type, cc.Content_CreatorFullName, a.AgentFullName
ORDER BY t.Title_Name;

-- בדיקת פעילות לקוחות
SELECT 
    c.firstName || ' ' || c.lastName AS customer,
    c.UserType,
    a.AgentFullName AS agent,
    COUNT(w.WatchHistoryID) AS total_views,
    COUNT(DISTINCT r.Title_ID) AS reviews_count
FROM Customer c
LEFT JOIN Agent a ON c.AgentID = a.AgentID
LEFT JOIN Profile p ON c.customerID = p.customerID
LEFT JOIN WatchHistory w ON p.WatchHistoryID = w.WatchHistoryID
LEFT JOIN Reviews r ON p.profileID = r.profileID
GROUP BY c.customerID, c.firstName, c.lastName, c.UserType, a.AgentFullName
ORDER BY total_views DESC;

-- הודעת סיום
SELECT 'Sample data integration completed successfully!' AS Status,
       'Database now contains data from both systems' AS Message;
