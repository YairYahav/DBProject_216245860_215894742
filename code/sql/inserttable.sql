-- Customer
INSERT INTO Customer (firstName, lastName, customerID, dateOfBirth, customerSince) 
VALUES 
  ('Yair', 'Yahav', 1, DATE '2006-03-10', DATE '2023-01-01'),
  ('Dana', 'Cohen', 2, DATE '1998-12-05', DATE '2022-06-15'),
  ('Avi', 'Levi', 3, DATE '1992-07-23', DATE '2021-11-20');

-- Devices
INSERT INTO Devices (deviceName, deviceID, lastSeen, deviceType, customerID) 
VALUES 
  ('Phone', 1, DATE '2023-05-01', 'Smartphone', 1),
  ('Laptop', 2, DATE '2023-05-02', 'Laptop', 2),
  ('Tablet', 3, DATE '2023-05-03', 'Tablet', 3);

-- WatchHistory
INSERT INTO WatchHistory (movieID, watchDate, durationWatched, WatchHistoryID) 
VALUES 
  (101, DATE '2023-04-01', 120.5, 1),
  (102, DATE '2023-04-02', 150.0, 2),
  (103, DATE '2023-04-03', 90.0, 3);

-- Favorites
INSERT INTO Favorites (movieID, lastSeen, totalTimeWatched) 
VALUES 
  (101, DATE '2023-04-01', 120.5),
  (102, DATE '2023-04-02', 150.0),
  (103, DATE '2023-04-03', 90.0);

-- Payment
INSERT INTO Payment (paymentID, paymentDate, amount, currency, paymentMethod, status, customerID) 
VALUES 
  (1, DATE '2023-01-10', 99.99, 'USD', 'Credit Card', 'Completed', 1),
  (2, DATE '2023-01-12', 49.99, 'USD', 'PayPal', 'Pending', 2),
  (3, DATE '2023-01-15', 129.99, 'USD', 'Debit Card', 'Completed', 3);

-- Profile
INSERT INTO Profile (profileName, profilePicture, isOnline, profileID, WatchHistoryID, customerID) 
VALUES 
  ('Yair_Profile', 'image1.jpg', TRUE, 1, 1, 1),
  ('Dana_Profile', 'image2.jpg', FALSE, 2, 2, 2),
  ('Avi_Profile', 'image3.jpg', TRUE, 3, 3, 3);

-- Reviews
INSERT INTO Reviews (rating, movieID, comment, reviewDate, profileID) 
VALUES 
  (5, 101, 'Amazing movie!', DATE '2023-04-01', 1),
  (4, 102, 'Very good, but a bit long.', DATE '2023-04-02', 2),
  (3, 103, 'It was okay, not my favorite.', DATE '2023-04-03', 3);

-- MarksAsFavorite
INSERT INTO MarksAsFavorite (profileID, movieID) 
VALUES 
  (1, 101),
  (2, 102),
  (3, 103);
