-- אילוץ: סכום תשלום לא יכול להיות שלילי
ALTER TABLE Payment
ADD CONSTRAINT chk_amount_positive CHECK (amount >= 0);

-- אילוץ: סטטוס תשלום רק מתוך רשימה
ALTER TABLE Payment
ADD CONSTRAINT chk_status_values CHECK (status IN ('Waiting for payment', 'Payment succussed', 'Failed transaction', 'loading'));

-- אילוץ: ברירת מחדל לתמונה בפרופיל
ALTER TABLE Profile
ALTER COLUMN profilePicture SET DEFAULT 'default.jpg';

