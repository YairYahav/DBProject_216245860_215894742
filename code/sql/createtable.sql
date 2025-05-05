CREATE TABLE customer
(
  firstName VARCHAR NOT NULL,
  lastName VARCHAR NOT NULL,
  customerID INT NOT NULL,
  dateOfBirth DATE NOT NULL,
  customerSince DATE NOT NULL,
  PRIMARY KEY (customerID)
);

CREATE TABLE Devices
(
  deviceName VARCHAR NOT NULL,
  deviceID INT NOT NULL,
  lastSeen DATE NOT NULL,
  deviceType VARCHAR NOT NULL,
  customerID INT NOT NULL,
  PRIMARY KEY (deviceID),
  FOREIGN KEY (customerID) REFERENCES customer(customerID)
);

CREATE TABLE WatchHistory
(
  movieID INT NOT NULL,
  watchDate DATE NOT NULL,
  durationWatched FLOAT NOT NULL,
  WatchHistoryID INT NOT NULL,
  PRIMARY KEY (WatchHistoryID)
);

CREATE TABLE Favorites
(
  movieID DATE NOT NULL,
  lastSeen DATE NOT NULL,
  totalTimeWatched FLOAT NOT NULL,
  PRIMARY KEY (movieID)
);

CREATE TABLE Payment
(
  paymentID INT NOT NULL,
  paymentDate DATE NOT NULL,
  amount FLOAT NOT NULL,
  currency VARCHAR NOT NULL,
  paymentMethod VARCHAR NOT NULL,
  status VARCHAR NOT NULL,
  customerID INT NOT NULL,
  PRIMARY KEY (paymentID),
  FOREIGN KEY (customerID) REFERENCES customer(customerID)
);

CREATE TABLE Profile
(
  profileName VARCHAR NOT NULL,
  profilePicture VARCHAR NOT NULL,
  isOnline BOOL NOT NULL,
  profileID INT NOT NULL,
  WatchHistoryID INT NOT NULL,
  customerID INT NOT NULL,
  PRIMARY KEY (profileID),
  FOREIGN KEY (WatchHistoryID) REFERENCES WatchHistory(WatchHistoryID),
  FOREIGN KEY (customerID) REFERENCES customer(customerID)
);

CREATE TABLE Reviews
(
  rating INT NOT NULL,
  movieID INT NOT NULL,
  comment VARCHAR NOT NULL,
  reviewDate DATE NOT NULL,
  profileID INT NOT NULL,
  PRIMARY KEY (movieID),
  FOREIGN KEY (profileID) REFERENCES Profile(profileID)
);

CREATE TABLE MarksAsFavorite
(
  profileID INT NOT NULL,
  movieID DATE NOT NULL,
  PRIMARY KEY (profileID, movieID),
  FOREIGN KEY (profileID) REFERENCES Profile(profileID),
  FOREIGN KEY (movieID) REFERENCES Favorites(movieID)
);
