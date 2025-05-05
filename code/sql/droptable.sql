-- Disable foreign key checks to avoid dependency issues

SET FOREIGN_KEY_CHECKS = 0;



-- Drop tables in reverse order of dependencies

DROP TABLE IF EXISTS Favorites;

DROP TABLE IF EXISTS WatchHistory;

DROP TABLE IF EXISTS Reviews;

DROP TABLE IF EXISTS Profile;

DROP TABLE IF EXISTS Devices;

DROP TABLE IF EXISTS Payment;

DROP TABLE IF EXISTS Customer;



-- Re-enable foreign key checks

SET FOREIGN_KEY_CHECKS = 1;
