-- Queries.sql


-- Select:

-- 1. כל הפרופילים עם היסטוריית צפייה ב-2024, כולל שם הלקוח
SELECT p.profileName, p.isOnline, c.firstName, c.lastName, EXTRACT(YEAR FROM w.watchDate) AS watchYear
FROM Profile p
JOIN WatchHistory w ON p.WatchHistoryID = w.WatchHistoryID
JOIN Customer c ON p.customerID = c.customerID
WHERE EXTRACT(YEAR FROM w.watchDate) = 2024;

-- 2. ממוצע זמן צפייה לסרטים מועדפים (Favorites)
SELECT f.movieID, AVG(f.totalTimeWatched) AS avgTimeWatched
FROM Favorites f
GROUP BY f.movieID
ORDER BY avgTimeWatched DESC;

-- 3. פרטי תשלום של לקוחות ששילמו מעל 200 ש"ח בשנה האחרונה
SELECT c.firstName, c.lastName, p.paymentDate, p.amount, p.currency
FROM Payment p
JOIN Customer c ON p.customerID = c.customerID
WHERE p.amount > 200 AND EXTRACT(YEAR FROM p.paymentDate) = EXTRACT(YEAR FROM CURRENT_DATE);

-- 4. לקוחות עם יותר משני מכשירים רשומים
SELECT c.customerID, c.firstName, c.lastName, COUNT(d.deviceID) AS deviceCount
FROM Customer c
JOIN Devices d ON c.customerID = d.customerID
GROUP BY c.customerID
HAVING COUNT(d.deviceID) > 2;

-- 5. רשימת פרופילים שהוסיפו סרט מועדף שדורג פחות מ-3
SELECT p.profileName, r.rating, r.comment
FROM MarksAsFavorite m
JOIN Reviews r ON m.movieID = r.movieID
JOIN Profile p ON m.profileID = p.profileID
WHERE r.rating < 3;

-- 6. כל הסרטים שנצפו באוקטובר כולל כמה זמן נצפו
SELECT w.movieID, w.watchDate, w.durationWatched
FROM WatchHistory w
WHERE EXTRACT(MONTH FROM w.watchDate) = 10;

-- 7. פרטי לקוחות שלא ביצעו אף תשלום השנה
SELECT c.customerID, c.firstName, c.lastName
FROM Customer c
WHERE c.customerID NOT IN (
  SELECT p.customerID FROM Payment p WHERE EXTRACT(YEAR FROM p.paymentDate) = EXTRACT(YEAR FROM CURRENT_DATE)
);

-- 8. ממוצע זמני צפייה לפי חודש
SELECT EXTRACT(MONTH FROM w.watchDate) AS month, AVG(w.durationWatched) AS avgDuration
FROM WatchHistory w
GROUP BY month
ORDER BY month;



-- Delete:

-- 1. מחיקת פרופילים לא פעילים מעל שנה (לפי היסטוריית צפייה)
DELETE FROM Profile
WHERE WatchHistoryID IN (
  SELECT w.WatchHistoryID FROM WatchHistory w
  WHERE w.watchDate < CURRENT_DATE - INTERVAL '1 year'
);

-- 2. מחיקת מכשירים שלא נראו מעל שנתיים
DELETE FROM Devices
WHERE lastSeen < CURRENT_DATE - INTERVAL '2 years';

-- 3. מחיקת תשלומים שנכשלו
DELETE FROM Payment
WHERE status = 'Failed transaction';



--- Update:

-- 1. עדכון סטטוס תשלום ישן ל"הושלם"
UPDATE Payment
SET status = 'Payment succussed'
WHERE paymentDate < CURRENT_DATE - INTERVAL '6 months' AND status != 'Payment succussed';

-- 2. עדכון תמונת פרופיל למשתמשים שאין להם תמונה
UPDATE Profile
SET profilePicture = 'default.jpg'
WHERE profilePicture IS NULL OR profilePicture = '';

-- 3. העלאת דירוג ל-5 אם התגובה חיובית
UPDATE Reviews
SET rating = 5
WHERE comment ILIKE '%amazing%' AND rating < 5;


