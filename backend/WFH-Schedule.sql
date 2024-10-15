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
(1, 'Test', 'CEO', 'CEO', 'MD', 'Singapore', 'ceo@test.com', NULL, 1, 'password'),
(2, 'Sales', 'Director', 'Sales', 'Director', 'Singapore', 'salesdirector@test.com', 1, 1, 'password'),
(3, 'Consultancy', 'Director', 'Consultancy', 'Director', 'Singapore', 'consultancydirector@test.com', 1, 1, 'password'),
(4, 'Solutioning', 'Director', 'Solutioning', 'Director', 'Singapore', 'solutioningdirector@test.com', 1, 1, 'password'),
(5, 'Engineering', 'Director', 'Engineering', 'Director', 'Singapore', 'engineeringdirector@test.com', 1, 1, 'password'),
(6, 'HR', 'Director', 'HR', 'Director', 'Singapore', 'hrdirector@test.com', 1, 1, 'password'),
(7, 'Finance', 'Director', 'Finance', 'Director', 'Singapore', 'financedirector@test.com', 1, 1, 'password'),
(8, 'IT', 'Director', 'IT', 'Director', 'Singapore', 'itdirector@test.com', 1, 1, 'password'),


-- Sales with 2 managers and 4 staff
(9, 'Sales', 'Manager1', 'Sales', 'Sales Manager', 'Singapore', 'salesmanager1@test.com', 2, 3, 'password'),
(10, 'Sales', 'Manager2', 'Sales', 'Sales Manager', 'Singapore', 'salesmanager2@test.com', 2, 3, 'password'),
(11, 'Sales', 'Staff1', 'Sales', 'Account Manager', 'Singapore', 'salesstaff1@test.com', 9, 2, 'password'),
(12, 'Sales', 'Staff2', 'Sales', 'Account Manager', 'Singapore', 'salesstaff2@test.com', 9, 2, 'password'),
(13, 'Sales', 'Staff3', 'Sales', 'Account Manager', 'Singapore', 'salesstaff3@test.com', 10, 2, 'password'),
(14, 'Sales', 'Staff4', 'Sales', 'Account Manager', 'Singapore', 'salesstaff4@test.com', 10, 2, 'password'),

-- Consultancy with 2 consultants
(15, 'Consultancy', 'Staff1', 'Consultancy', 'Consultant', 'Singapore', 'consultant1@test.com', 3, 2, 'password'),
(16, 'Consultancy', 'Staff2', 'Consultancy', 'Consultant', 'Singapore', 'consultant2@test.com', 3, 2, 'password'),

-- Solutioning with 2 developers and 2 support team staff
(17, 'Solutioning', 'Developer1', 'Solutioning', 'Developer', 'Singapore', 'developer1@test.com', 4, 2, 'password'),
(18, 'Solutioning', 'Developer2', 'Solutioning', 'Developer', 'Singapore', 'developer2@test.com', 4, 2, 'password'),
(19, 'Solutioning', 'Support1', 'Solutioning', 'Support', 'Singapore', 'support1@test.com', 4, 2, 'password'),
(20, 'Solutioning', 'Support2', 'Solutioning', 'Support', 'Singapore', 'support2@test.com', 4, 2, 'password'),

-- Engineering with 2 senior engineers, 2 junior engineers, 2 call centre, 2 operation planning team
(21, 'Engineering', 'SeniorEngineer1', 'Engineering', 'Senior Engineer', 'Singapore', 'se1@test.com', 5, 2, 'password'),
(22, 'Engineering', 'SeniorEngineer2', 'Engineering', 'Senior Engineer', 'Singapore', 'se2@test.com', 5, 2, 'password'),
(23, 'Engineering', 'JuniorEngineer1', 'Engineering', 'Junior Engineer', 'Singapore', 'je1@test.com', 5, 2, 'password'),
(24, 'Engineering', 'JuniorEngineer2', 'Engineering', 'Junior Engineer', 'Singapore', 'je2@test.com', 5, 2, 'password'),
(25, 'Engineering', 'CallCentre1', 'Engineering', 'Call Centre', 'Singapore', 'cc1@test.com', 5, 2, 'password'),
(26, 'Engineering', 'CallCentre2', 'Engineering', 'Call Centre', 'Singapore', 'cc2@test.com', 5, 2, 'password'),
(27, 'Engineering', 'OperationPlanning1', 'Engineering', 'Operation Planning', 'Singapore', 'op1@test.com', 5, 2, 'password'),
(28, 'Engineering', 'OperationPlanning2', 'Engineering', 'Operation Planning', 'Singapore', 'op2@test.com', 5, 2, 'password'),

-- HR with 2 HR Team, 2 LD Team, 2 Admin Team
(29, 'HR', 'HR1', 'HR', 'HR Team', 'Singapore', 'hr1@test.com', 6, 1, 'password'),
(30, 'HR', 'HR2', 'HR', 'HR Team', 'Singapore', 'hr2@test.com', 6, 1, 'password'),
(31, 'HR', 'LD1', 'HR', 'LD Team', 'Singapore', 'ld1@test.com', 6, 2, 'password'),
(32, 'HR', 'LD2', 'HR', 'LD Team', 'Singapore', 'ld2@test.com', 6, 2, 'password'),
(33, 'HR', 'Admin1', 'HR', 'Admin Team', 'Singapore', 'hradmin1@test.com', 6, 2, 'password'),
(34, 'HR', 'Admin2', 'HR', 'Admin Team', 'Singapore', 'hradmin2@test.com', 6, 2, 'password'),

-- Finance with 2 Finance Manager, 5 Finance Executive
(35, 'Finance', 'Manager1', 'Finance', 'Finance Manager', 'Singapore', 'financemanager1@test.com', 7, 3, 'password'),
(36, 'Finance', 'Manager2', 'Finance', 'Finance Manager', 'Singapore', 'financemanager2@test.com', 7, 3, 'password'),
(37, 'Finance', 'Staff1', 'Finance', 'Finance Executive', 'Singapore', 'financestaff1@test.com', 35, 2, 'password'),
(38, 'Finance', 'Staff2', 'Finance', 'Finance Executive', 'Singapore', 'financestaff2@test.com', 35, 2, 'password'),
(39, 'Finance', 'Staff3', 'Finance', 'Finance Executive', 'Singapore', 'financestaff3@test.com', 36, 2, 'password'),
(40, 'Finance', 'Staff4', 'Finance', 'Finance Executive', 'Singapore', 'financestaff4@test.com', 36, 2, 'password'),
(41, 'Finance', 'Staff5', 'Finance', 'Finance Executive', 'Singapore', 'financestaff5@test.com', 36, 2, 'password'),

-- IT with 2 IT Team, 2 IT Support Team
(42, 'IT', 'IT1', 'IT', 'IT Team', 'Singapore', 'it1@test.com', 8, 2, 'password'),
(43, 'IT', 'IT2', 'IT', 'IT Team', 'Singapore', 'it2@test.com', 8, 2, 'password');


-- DROP TABLE `wfh_scheduler`.`WFHSchedule`;
-- DROP TABLE `wfh_scheduler`.`WFHRequest`;

