CREATE DATABASE  Project;
USE Project;

CREATE TABLE Person (
    person_id INT PRIMARY KEY,
    name VARCHAR(100),
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    age INT,
    gender VARCHAR(10),
    address1 VARCHAR(255),
    address2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    zipcode VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE Phone (
    person_id INT,
    phone_number VARCHAR(20),
    PRIMARY KEY (person_id, phone_number),
    FOREIGN KEY (person_id) REFERENCES Person(person_id)
);

CREATE TABLE Employee (
    employee_id INT PRIMARY KEY,
    person_id INT,
    start_date DATE,
    end_date DATE,
    supervised_by INT,
    FOREIGN KEY (person_id) REFERENCES Person(person_id),
    FOREIGN KEY (supervised_by) REFERENCES Employee(employee_id)
);

-- Customers and Referrals
CREATE TABLE Customer (
    customer_id INT PRIMARY KEY,
    person_id INT,
    referred_by INT,
    FOREIGN KEY (person_id) REFERENCES Person(person_id),
    FOREIGN KEY (referred_by) REFERENCES Customer(customer_id)
);

-- Potential Employees
CREATE TABLE Potential_Employee (
    potential_employee_id INT PRIMARY KEY,
    person_id INT,
    FOREIGN KEY (person_id) REFERENCES Person(person_id)
);

-- Job Positions
CREATE TABLE Job_Position (
    jobID INT PRIMARY KEY,
    description TEXT,
    postedDate DATE
);

-- Job Applications
CREATE TABLE Job_Application (
    applicationID INT PRIMARY KEY,
    jobID INT,
    person_id INT,
    description TEXT,
    FOREIGN KEY (jobID) REFERENCES Job_Position(jobID),
    FOREIGN KEY (person_id) REFERENCES Person(person_id)
);

-- Interviews
CREATE TABLE Interview (
    interviewID INT PRIMARY KEY,
    applicationID INT,
    grade VARCHAR(5),
    date_time DATETIME,
    FOREIGN KEY (applicationID) REFERENCES Job_Application(applicationID)
);

-- Interviewers
CREATE TABLE Interviewer (
    interviewer_id INT PRIMARY KEY,
    employee_id INT,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- Mapping Interviewers to Interviews
CREATE TABLE Interview_Interviewer (
    interview_id INT,
    interviewer_id INT,
    PRIMARY KEY (interview_id, interviewer_id),
    FOREIGN KEY (interview_id) REFERENCES Interview(interviewID),
    FOREIGN KEY (interviewer_id) REFERENCES Interviewer(interviewer_id)
);

-- Departments
CREATE TABLE Department (
    departmentID INT PRIMARY KEY,
    name VARCHAR(100)
);

-- Employee-Department Assignments
CREATE TABLE Employee_Department (
    employee_id INT,
    departmentID INT,
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (employee_id, departmentID),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (departmentID) REFERENCES Department(departmentID)
);

-- Performance Reviews
CREATE TABLE Performance_Review (
    reviewID INT PRIMARY KEY,
    employee_id INT,
    reviewDate DATE,
    score INT,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- Salaries
CREATE TABLE Employee_Salary (
    transaction_number INT PRIMARY KEY,
    employee_id INT,
    payDate DATE,
    amount DECIMAL(10, 2),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- Marketing Sites
CREATE TABLE Marketing_Site (
    siteID INT PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(255)
);

-- Employee assignments to sites
CREATE TABLE Employee_Marketing_Site (
    employee_id INT,
    siteID INT,
    PRIMARY KEY (employee_id, siteID),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (siteID) REFERENCES Marketing_Site(siteID)
);

-- Products
CREATE TABLE Product (
    product_id INT PRIMARY KEY,
    productType VARCHAR(50),
    size VARCHAR(10),
    weight DECIMAL(10, 2),
    style VARCHAR(50),
    listPrice DECIMAL(10, 2)
);

-- Parts
CREATE TABLE Part (
    part_id INT PRIMARY KEY,
    partType VARCHAR(50),
    price DECIMAL(10, 2)
);

-- Product-Part Mapping
CREATE TABLE Product_Part (
    product_id INT,
    part_id INT,
    quantity INT,
    PRIMARY KEY (product_id, part_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    FOREIGN KEY (part_id) REFERENCES Part(part_id)
);

-- Vendors
CREATE TABLE Vendor (
    vendorID INT PRIMARY KEY,
    name VARCHAR(100),
    address VARCHAR(255),
    accountNumber VARCHAR(50),
    creditRating INT,
    webURL VARCHAR(255)
);

-- Vendor-Part Mapping
CREATE TABLE Vendor_Part (
    vendorID INT,
    part_id INT,
    PRIMARY KEY (vendorID, part_id),
    FOREIGN KEY (vendorID) REFERENCES Vendor(vendorID),
    FOREIGN KEY (part_id) REFERENCES Part(part_id)
);

CREATE TABLE Sales_History (
    sale_id INT PRIMARY KEY,
    customer_id INT,
    employee_id INT,
    sale_date DATE,
    total_amount DECIMAL(10, 2),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

CREATE TABLE Sale_Product (
    sale_id INT,
    product_id INT,
    quantity INT,
    unitPrice DECIMAL(10, 2),
    PRIMARY KEY (sale_id, product_id),
    FOREIGN KEY (sale_id) REFERENCES Sales_History(sale_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);



INSERT INTO Person VALUES
(1, 'John Smith', 'John', 'Smith', 35, 'Male', '123 Main St', '', 'New York', 'NY', '10001', 'john.smith@example.com'),
(2, 'Alice Johnson', 'Alice', 'Johnson', 29, 'Female', '456 Oak Ave', '', 'Chicago', 'IL', '60616', 'alice.johnson@example.com'),
(3, 'Bob Williams', 'Bob', 'Williams', 40, 'Male', '789 Pine Rd', '', 'Dallas', 'TX', '75201', 'bob.williams@example.com'),
(4, 'Carol Davis', 'Carol', 'Davis', 33, 'Female', '321 Elm St', '', 'Miami', 'FL', '33101', 'carol.davis@example.com'),
(5, 'Ethan Brown', 'Ethan', 'Brown', 28, 'Male', '654 Cedar Blvd', '', 'Seattle', 'WA', '98101', 'ethan.brown@example.com'),
(6, 'Hellen Cole', 'Hellen', 'Cole', 30, 'Female', '789 Sunset Blvd', '', 'Los Angeles', 'CA', '90001', 'hellen.cole@example.com');



INSERT INTO Phone VALUES
(1, '555-1111'),
(2, '555-2222'),
(3, '555-3333'),
(4, '555-4444'),
(5, '555-5555');


INSERT INTO Employee VALUES
(101, 1, '2020-01-10', NULL, NULL),
(102, 2, '2021-03-15', NULL, 101),
(103, 3, '2019-06-20', NULL, 101),
(104, 4, '2022-09-05', NULL, 102),
(105, 5, '2023-07-12', NULL, 102),
(106, 6, '2023-01-01', NULL, NULL);



INSERT INTO Employee_Salary VALUES
(1001, 101, '2024-01-30', 5000.00),
(1002, 102, '2024-01-30', 4500.00),
(1003, 103, '2024-01-30', 4800.00),
(1004, 104, '2024-01-30', 4600.00),
(1005, 105, '2024-01-30', 4700.00);


INSERT INTO Customer VALUES
(201, 1, NULL),
(202, 2, 201),
(203, 3, 201),
(204, 4, 202),
(205, 5, 203);

INSERT INTO Potential_Employee VALUES
(301, 1),
(302, 2),
(303, 3),
(304, 4),
(305, 5);


INSERT INTO Job_Position VALUES
(401, 'Software Developer', '2024-12-01'),
(402, 'Sales Associate', '2024-12-05'),
(403, 'Marketing Analyst', '2024-12-10'),
(11111, 'Senior Designer', '2025-01-01'),
(12345, 'Test Job', '2025-05-01');



INSERT INTO Job_Application VALUES
(501, 401, 1, 'Applied via portal'),
(502, 401, 2, 'Referred by employee'),
(503, 402, 3, 'Walk-in interview'),
(504, 403, 4, 'University job fair'),
(601, 11111, 1, 'Applied for Senior Designer'),
(999, 12345, 6, 'Testing employee as applicant');



INSERT INTO Interview VALUES
(601, 501, 'A+', '2025-01-10 10:00:00'),
(602, 502, 'B', '2025-01-12 14:00:00'),
(603, 503, 'A', '2025-01-15 11:00:00'),
(604, 504, 'C', '2025-01-20 13:00:00'),
(701, 601, 'A', '2025-05-06 10:00:00');


INSERT INTO Department VALUES
(701, 'IT'),
(702, 'Sales'),
(703, 'Marketing');


	INSERT INTO Employee_Department (employee_id, departmentID, start_date, end_date) VALUES
	(101, 701, '2020-01-10', NULL),
	(101, 702, '2020-01-10', NULL),
	(101, 703, '2020-01-10', NULL),
	(106, 703, '2025-05-01', NULL);


INSERT INTO Performance_Review VALUES
(801, 101, '2024-12-01', 90),
(802, 102, '2024-12-01', 85),
(803, 103, '2024-12-01', 88),
(804, 104, '2024-12-01', 75),
(805, 105, '2024-12-01', 80);


INSERT INTO Marketing_Site VALUES
(901, 'Site A', 'New York'),
(902, 'Site B', 'Chicago');


INSERT INTO Employee_Marketing_Site VALUES
(105, 901),
(104, 902);


INSERT INTO Product VALUES
(1001, 'Shirt', 'M', 0.5, 'Casual', 29.99),
(1002, 'Pants', 'L', 0.8, 'Formal', 49.99),
(1003, 'Jacket', 'XL', 1.2, 'Winter', 89.99);



INSERT INTO Part VALUES
(1101, 'Button', 0.10),
(1102, 'Zipper', 0.50),
(1103, 'Cloth Panel', 1.00),
(1201, 'Cup', 3.50);

INSERT INTO Product_Part VALUES
(1001, 1101, 5),
(1002, 1102, 1),
(1003, 1103, 3);


INSERT INTO Vendor VALUES
(1201, 'Best Parts Co.', '123 Supply Rd', 'ACC123', 5, 'http://bestparts.com'),
(1202, 'Zippers Inc.', '456 Fashion Ln', 'ACC456', 4, 'http://zippersinc.com');



INSERT INTO Vendor_Part VALUES
(1201, 1101),
(1202, 1102),
(1201, 1103),
(1201, 1201);  -- Assuming vendor 1201 supplies part 1201 (Cup)


INSERT INTO Sales_History VALUES
(1301, 201, 101, '2025-01-25', 129.97),
(1302, 202, 102, '2025-01-26', 89.99);


INSERT INTO Sale_Product VALUES
(1301, 1001, 1, 29.99),
(1301, 1002, 1, 49.99),
(1301, 1003, 1, 49.99),
(1302, 1003, 1, 89.99);

INSERT INTO Interviewer VALUES
(6, 106);

INSERT INTO Interview_Interviewer VALUES
(701, 6);



CREATE VIEW View1 AS
SELECT 
    e.employee_id,
    ROUND(AVG(s.amount), 2) AS avg_monthly_salary
FROM 
    Employee_Salary s
JOIN 
    Employee e ON e.employee_id = s.employee_id
GROUP BY 
    e.employee_id;
SELECT * FROM View1;


CREATE OR REPLACE VIEW View2 AS
SELECT 
    ja.applicationID,
    COUNT(*) AS passed_rounds
FROM 
    Interview i
JOIN 
    Job_Application ja ON ja.applicationID = i.applicationID
WHERE 
    i.grade IN ('A', 'A+')
GROUP BY 
    ja.applicationID;

SELECT * FROM View2;



CREATE VIEW View3 AS
SELECT 
    p.productType,
    SUM(sp.quantity) AS total_items_sold
FROM 
    Sale_Product sp
JOIN 
    Product p ON p.product_id = sp.product_id
GROUP BY 
    p.productType;
SELECT * FROM View3;



CREATE VIEW View4 AS
SELECT 
    pp.product_id,
    SUM(pp.quantity * pt.price) AS total_part_cost
FROM 
    Product_Part pp
JOIN 
    Part pt ON pt.part_id = pp.part_id
GROUP BY 
    pp.product_id;
    
SELECT * FROM View4;

 

SELECT e.employee_id, p.name
FROM Interview i
JOIN Interview_Interviewer ii ON i.interviewID = ii.interview_id
JOIN Interviewer ir ON ii.interviewer_id = ir.interviewer_id
JOIN Employee e ON ir.employee_id = e.employee_id
JOIN Person p ON e.person_id = p.person_id
JOIN Job_Application ja ON i.applicationID = ja.applicationID
JOIN Job_Position jp ON ja.jobID = jp.jobID
WHERE jp.jobID = 11111 AND p.name = 'Hellen Cole';



SELECT jobID
FROM Job_Position
WHERE MONTH(postedDate) = 12
  AND YEAR(postedDate) = 2024;


SELECT e1.employee_id, p.name
FROM Employee e1
JOIN Person p ON e1.person_id = p.person_id
WHERE e1.employee_id NOT IN (
    SELECT e2.supervised_by FROM Employee e2 WHERE e2.supervised_by IS NOT NULL
);
 

SELECT ms.siteID, ms.location
FROM Marketing_Site ms
WHERE ms.siteID NOT IN (
    SELECT DISTINCT siteID
    FROM Sales_History
    WHERE MONTH(sale_date) = 3 AND YEAR(sale_date) = 2011
);
 

SELECT jp.jobID, jp.description
FROM Job_Position jp
WHERE jp.jobID NOT IN (
    SELECT ja.jobID
    FROM Job_Application ja
    JOIN Interview i ON ja.applicationID = i.applicationID
    GROUP BY ja.jobID
    HAVING AVG(CAST(i.grade AS UNSIGNED)) > 70 AND COUNT(*) >= 5
)
AND jp.postedDate < DATE_SUB(CURDATE(), INTERVAL 1 MONTH);


SELECT DISTINCT e.employee_id, p.name
FROM Employee e
JOIN Person p ON e.person_id = p.person_id
WHERE NOT EXISTS (
    SELECT pt.productType
    FROM Product pt
    WHERE pt.listPrice > 200
    AND NOT EXISTS (
        SELECT p2.productType
        FROM Sales_History sh
        JOIN Sale_Product sp ON sh.sale_id = sp.sale_id
        JOIN Product p2 ON sp.product_id = p2.product_id
        WHERE sh.employee_id = e.employee_id AND p2.listPrice > 200
    )
);
 


SELECT d.departmentID, d.name
FROM Department d
WHERE d.departmentID NOT IN (
    SELECT departmentiD
    FROM Job_Position
    WHERE postedDate BETWEEN '2011-01-01' AND '2011-02-01'
);

SELECT DISTINCT p.name, e.employee_id, ed.departmentID
FROM Employee e
JOIN Person p ON e.person_id = p.person_id
JOIN Job_Application ja ON ja.person_id = p.person_id
JOIN Employee_Department ed ON e.employee_id = ed.employee_id
WHERE ja.jobID = 12345;



SELECT productType
FROM View3
ORDER BY total_items_sold DESC
LIMIT 1;

 
SELECT 
    p.productType,
    (SUM(sp.quantity * sp.unitPrice) - IFNULL(MAX(v.total_part_cost), 0)) AS profit
FROM Sale_Product sp
JOIN Product p ON sp.product_id = p.product_id
LEFT JOIN View4 v ON v.product_id = p.product_id
GROUP BY p.productType
ORDER BY profit DESC
LIMIT 1;

 

SELECT e.employee_id, p.name
FROM Employee e
JOIN Person p ON e.person_id = p.person_id
WHERE NOT EXISTS (
    SELECT 1
    FROM Department d
    WHERE NOT EXISTS (
        SELECT 1
        FROM Employee_Department ed
        WHERE ed.departmentID = d.departmentID
          AND ed.employee_id = e.employee_id
    )
);



SELECT p.name, p.person_id
FROM Interview i
JOIN Job_Application ja ON i.applicationID = ja.applicationID
JOIN Person p ON ja.person_id = p.person_id
GROUP BY p.person_id
HAVING AVG(
    CASE i.grade
        WHEN 'A+' THEN 95
        WHEN 'A' THEN 90
        WHEN 'B' THEN 80
        WHEN 'C' THEN 70
        ELSE 0
    END
) > 70 AND COUNT(*) >= 2;  



SELECT e.employee_id, p.name, AVG(s.amount) AS avg_salary
FROM Employee_Salary s
JOIN Employee e ON s.employee_id = e.employee_id
JOIN Person p ON e.person_id = p.person_id
GROUP BY e.employee_id
ORDER BY avg_salary DESC
LIMIT 1;

 
SELECT v.vendorID, v.name
FROM Vendor v
JOIN Vendor_Part vp ON v.vendorID = vp.vendorID
JOIN Part p ON vp.part_id = p.part_id
WHERE p.partType = 'Cup' AND p.price = (
    SELECT MIN(p2.price)
    FROM Part p2
    WHERE p2.partType = 'Cup' AND p2.price < 4
);



SELECT 
    per.name,
    ph.phone_number,
    per.email
FROM Interview i
JOIN Job_Application ja ON i.applicationID = ja.applicationID
JOIN Person per ON ja.person_id = per.person_id
LEFT JOIN Phone ph ON per.person_id = ph.person_id
WHERE i.grade IN ('A', 'A+');

