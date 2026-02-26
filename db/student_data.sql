-- SQL script to create and seed student_data table
DROP TABLE IF EXISTS student_marks;
DROP TABLE IF EXISTS student_data;

CREATE TABLE student_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    height REAL NOT NULL,
    weight REAL NOT NULL
);

INSERT INTO student_data (name, height, weight) VALUES
('Sujan Thapa', 168.2, 62.5),
('Aarati Gurung', 156.4, 50.8),
('Bikash Karki', 172.1, 68.3),
('Nirmala Rai', 160.7, 54.2),
('Prakash Magar', 175.0, 70.1),
('Sita Tamang', 158.9, 52.0),
('Ramesh Shrestha', 170.3, 65.4),
('Manisha Bhandari', 162.5, 56.7),
('Dipesh Adhikari', 169.8, 64.0),
('Kusum Koirala', 157.6, 51.3);

CREATE TABLE student_marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL UNIQUE,
    nepali INTEGER NOT NULL CHECK (nepali BETWEEN 0 AND 100),
    english INTEGER NOT NULL CHECK (english BETWEEN 0 AND 100),
    mathematics INTEGER NOT NULL CHECK (mathematics BETWEEN 0 AND 100),
    science INTEGER NOT NULL CHECK (science BETWEEN 0 AND 100),
    social_studies INTEGER NOT NULL CHECK (social_studies BETWEEN 0 AND 100),
    FOREIGN KEY (student_id) REFERENCES student_data(id)
);

INSERT INTO student_marks (student_id, nepali, english, mathematics, science, social_studies) VALUES
(1, 78, 82, 85, 80, 76),
(2, 88, 84, 90, 87, 83),
(3, 72, 75, 79, 74, 70),
(4, 91, 89, 93, 90, 88),
(5, 67, 71, 69, 73, 68),
(6, 81, 79, 84, 82, 80),
(7, 76, 78, 77, 75, 74),
(8, 85, 87, 88, 86, 84),
(9, 69, 73, 72, 70, 71),
(10, 92, 90, 94, 91, 89);
