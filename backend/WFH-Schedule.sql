CREATE DATABASE wfh_scheduler;
USE wfh_scheduler;
CREATE TABLE Staff (
    staff_id INT PRIMARY KEY,
    staff_fname VARCHAR(255),
    staff_lname VARCHAR(255),
    dept VARCHAR(255),
    position VARCHAR(255),
    country VARCHAR(255),
    email VARCHAR(255),
    reporting_manager INT,
    role INT,
    password VARCHAR(255),
    FOREIGN KEY (reporting_manager) REFERENCES Staff(staff_id)
);

CREATE TABLE WFHRequest (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    staff_id INT NOT NULL,
    manager_id INT NOT NULL,
    request_date DATE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE DEFAULT NULL,
    duration VARCHAR(20) NOT NULL, -- 'FULL_DAY', 'HALF_DAY_AM', 'HALF_DAY_PM'
    status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'REJECTED'
    reason_for_applying TEXT,
    reason_for_rejection TEXT DEFAULT NULL,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id),
    FOREIGN KEY (manager_id) REFERENCES Staff(staff_id)
);

CREATE TABLE WFHSchedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    request_id INT NOT NULL,
    staff_id INT NOT NULL,
    manager_id INT NOT NULL,
    date DATE NOT NULL,
    duration VARCHAR(20) NOT NULL, -- 'FULL_DAY', 'HALF_DAY_AM', 'HALF_DAY_PM'
    status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'WITHDRAWN', 'REJECTED'
    dept VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,    
    reason_for_withdrawing TEXT DEFAULT NULL,
    FOREIGN KEY (request_id) REFERENCES WFHRequest(request_id),
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id),
    FOREIGN KEY (manager_id) REFERENCES Staff(staff_id)
);


INSERT INTO Staff (staff_id, staff_fname, staff_lname, dept, position, country, email, reporting_manager, role, password)
VALUES 
-- CEO with 7 directors
(1, 'Jack', 'Sim', 'CEO', 'MD', 'Singapore', 'ceo@test.com', 1, 1, 'password'),
(2, 'Derek', 'Tan', 'Sales', 'Director', 'Singapore', 'salesdirector@test.com', 1, 1, 'password'),
(3, 'Ernst', 'Sim', 'Consultancy', 'Director', 'Singapore', 'consultancydirector@test.com', 1, 1, 'password'),
(4, 'Eric', 'Loh', 'Solutioning', 'Director', 'Singapore', 'solutioningdirector@test.com', 1, 1, 'password'),
(5, 'Philip', 'Lee', 'Engineering', 'Director', 'Singapore', 'engineeringdirector@test.com', 1, 1, 'password'),
(6, 'Sally', 'Loh', 'HR', 'Director', 'Singapore', 'hrdirector@test.com', 1, 1, 'password'),
(7, 'David', 'Yap', 'Finance', 'Director', 'Singapore', 'financedirector@test.com', 1, 1, 'password'),
(8, 'Peter', 'Yap', 'IT', 'Director', 'Singapore', 'itdirector@test.com', 1, 1, 'password'),


-- Sales with 2 managers and 4 staff
(9, 'Kai Xiang', 'Lee', 'Sales', 'Sales Manager', 'Singapore', 'salesmanager1@test.com', 2, 3, 'password'),
(10, 'Nurul', 'Binte Hassan', 'Sales', 'Sales Manager', 'Singapore', 'salesmanager2@test.com', 2, 3, 'password'),
(11, 'Arun', 'Pillai', 'Sales', 'Account Manager', 'Singapore', 'salesstaff1@test.com', 9, 2, 'password'),
(12, 'Yi Ling', 'Teo', 'Sales', 'Account Manager', 'Singapore', 'salesstaff2@test.com', 9, 2, 'password'),
(13, 'Ismail', 'Bin Rahman', 'Sales', 'Account Manager', 'Singapore', 'salesstaff3@test.com', 10, 2, 'password'),
(14, 'Hui Wen', 'Goh', 'Sales', 'Account Manager', 'Singapore', 'salesstaff4@test.com', 10, 2, 'password'),

-- Consultancy with 2 consultants
(15, 'Mei Ling', 'Wong', 'Consultancy', 'Consultant', 'Singapore', 'consultant1@test.com', 3, 2, 'password'),
(16, 'Rajesh', 'Sharma', 'Consultancy', 'Consultant', 'Singapore', 'consultant2@test.com', 3, 2, 'password'),

-- Solutioning with 2 developers and 2 support team staff
(17, 'Zhi Hao', 'Chen', 'Solutioning', 'Developer', 'Singapore', 'developer1@test.com', 4, 2, 'password'),
(18, 'Kartik', 'Patel', 'Solutioning', 'Developer', 'Singapore', 'developer2@test.com', 4, 2, 'password'),
(19, 'Farah', 'Binte Azman', 'Solutioning', 'Support', 'Singapore', 'support1@test.com', 4, 2, 'password'),
(20, 'Yu Xuan', 'Ng', 'Solutioning', 'Support', 'Singapore', 'support2@test.com', 4, 2, 'password'),

-- Engineering with 2 senior engineers, 2 junior engineers, 2 call centre, 2 operation planning team
(21, 'Wei Jie', 'Koh', 'Engineering', 'Senior Engineer', 'Singapore', 'se1@test.com', 5, 2, 'password'),
(22, 'Lakshmi', 'Menon', 'Engineering', 'Senior Engineer', 'Singapore', 'se2@test.com', 5, 2, 'password'),
(23, 'Muhammad', 'Bin Yusof', 'Engineering', 'Junior Engineer', 'Singapore', 'je1@test.com', 5, 2, 'password'),
(24, 'Xin Yi', 'Tan', 'Engineering', 'Junior Engineer', 'Singapore', 'je2@test.com', 5, 2, 'password'),
(25, 'Nadia', 'Binte Kamal', 'Engineering', 'Call Centre', 'Singapore', 'cc1@test.com', 5, 2, 'password'),
(26, 'Jia Jun', 'Lau', 'Engineering', 'Call Centre', 'Singapore', 'cc2@test.com', 5, 2, 'password'),
(27, 'Anita', 'Devi', 'Engineering', 'Operation Planning', 'Singapore', 'op1@test.com', 5, 2, 'password'),
(28, 'Zhi Ying', 'Yeo', 'Engineering', 'Operation Planning', 'Singapore', 'op2@test.com', 5, 2, 'password'),

-- HR with 2 HR Team, 2 LD Team, 2 Admin Team
(29, 'Hui Min', 'Chua', 'HR', 'HR Team', 'Singapore', 'hr1@test.com', 6, 1, 'password'),
(30, 'Rohan', 'Kapoor', 'HR', 'HR Team', 'Singapore', 'hr2@test.com', 6, 1, 'password'),
(31, 'Nur Aisyah', 'Binte Ibrahim', 'HR', 'LD Team', 'Singapore', 'ld1@test.com', 6, 2, 'password'),
(32, 'Wei Ling', 'Sim', 'HR', 'LD Team', 'Singapore', 'ld2@test.com', 6, 2, 'password'),
(33, 'Deepa', 'Krishnan', 'HR', 'Admin Team', 'Singapore', 'hradmin1@test.com', 6, 2, 'password'),
(34, 'Shu Hui', 'Low', 'HR', 'Admin Team', 'Singapore', 'hradmin2@test.com', 6, 2, 'password'),

-- Finance with 2 Finance Manager, 5 Finance Executive
(35, 'Choon Seng', 'Teo', 'Finance', 'Finance Manager', 'Singapore', 'financemanager1@test.com', 7, 3, 'password'),
(36, 'Hafiz', 'Bin Omar', 'Finance', 'Finance Manager', 'Singapore', 'financemanager2@test.com', 7, 3, 'password'),
(37, 'Ravi', 'Chandran', 'Finance', 'Finance Executive', 'Singapore', 'financestaff1@test.com', 35, 2, 'password'),
(38, 'Li Ying', 'Poh', 'Finance', 'Finance Executive', 'Singapore', 'financestaff2@test.com', 35, 2, 'password'),
(39, 'Nurul Ain', 'Binte Rashid', 'Finance', 'Finance Executive', 'Singapore', 'financestaff3@test.com', 36, 2, 'password'),
(40, 'Jun Wei', 'Ang', 'Finance', 'Finance Executive', 'Singapore', 'financestaff4@test.com', 36, 2, 'password'),
(41, 'Meenakshi', 'Sundaram', 'Finance', 'Finance Executive', 'Singapore', 'financestaff5@test.com', 36, 2, 'password'),

-- IT with 2 IT Team
(42, 'Yi Xuan', 'Khoo', 'IT', 'IT Team', 'Singapore', 'it1@test.com', 8, 2, 'password'),
(43, 'Arjun', 'Nair', 'IT', 'IT Team', 'Singapore', 'it2@test.com', 8, 2, 'password');