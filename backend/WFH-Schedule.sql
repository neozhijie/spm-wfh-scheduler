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
    status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'REJECTED'
    reason_for_applying TEXT,
    reason_for_rejection TEXT DEFAULT NULL,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id),
    FOREIGN KEY (manager_id) REFERENCES Staff(staff_id)
);

CREATE TABLE WFHSchedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    request_id INT NOT NULL,
    date DATE NOT NULL,
    duration VARCHAR(20) NOT NULL, -- 'FULL_DAY', 'HALF_DAY_AM', 'HALF_DAY_PM'
    status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'WITHDRAWN', 'REJECTED'
    reason_for_withdrawing TEXT DEFAULT NULL,
    FOREIGN KEY (request_id) REFERENCES WFHRequest(request_id)
);


INSERT INTO Staff (staff_id, staff_fname, staff_lname, dept, position, country, email, reporting_manager, role, password)
VALUES 
(1, 'Test', 'Director', 'Test Department', 'Director', 'Test Country', 'director@test.com', NULL, 1, 'testpassword1'),
(2, 'Test', 'Manager', 'Test Department', 'Manager', 'Test Country', 'manager@test.com', 1, 3, 'testpassword3'),
(3, 'Test', 'Staff', 'Test Department', 'Staff', 'Test Country', 'staff@test.com', 2, 2, 'testpassword2');

-- DROP TABLE `wfh_scheduler`.`WFHSchedule`;
-- DROP TABLE `wfh_scheduler`.`WFHApproval`;
-- DROP TABLE `wfh_scheduler`.`WFHRequest`;

