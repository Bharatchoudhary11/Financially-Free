-- src/db/schema.sql

PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,               -- YYYY-MM-DD (month start)
    vehicle_category TEXT NOT NULL,   -- '2W','3W','4W', etc.
    maker TEXT NOT NULL,
    registrations INTEGER NOT NULL,
    year INTEGER,
    month INTEGER
);

DELETE FROM registrations;

INSERT INTO registrations (date, vehicle_category, maker, registrations, year, month) VALUES
('2024-01-01','2W','Honda',1200,2024,1),
('2024-01-01','2W','Yamaha',800,2024,1),
('2024-01-01','4W','Maruti',1500,2024,1),
('2024-02-01','2W','Honda',1350,2024,2),
('2024-02-01','2W','Yamaha',900,2024,2),
('2024-02-01','4W','Maruti',1600,2024,2),
('2024-03-01','2W','Honda',1400,2024,3),
('2024-03-01','2W','Yamaha',950,2024,3),
('2024-03-01','4W','Maruti',1700,2024,3),
('2025-01-01','2W','Honda',1600,2025,1),
('2025-01-01','2W','Yamaha',1100,2025,1),
('2025-01-01','4W','Maruti',1800,2025,1),
('2025-02-01','2W','Honda',1650,2025,2),
('2025-02-01','2W','Yamaha',1150,2025,2),
('2025-02-01','4W','Maruti',1900,2025,2),
('2025-03-01','2W','Honda',1700,2025,3),
('2025-03-01','2W','Yamaha',1200,2025,3),
('2025-03-01','4W','Maruti',2000,2025,3);

COMMIT;
