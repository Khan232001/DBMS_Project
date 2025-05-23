import pymysql
import pymysql.cursors
import re

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Bangladesh1!',
    'database': 'project',
    'cursorclass': pymysql.cursors.DictCursor
}

def establish_db_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.Error as e:
        print(f"FATAL: Error connecting to the MySQL database: {e}")
        print("Please ensure MySQL server is running and configuration is correct.")
        return None

def display_results_as_table(query_results):
    if not query_results:
        print("No data to display or query returned no results.")
        return

    if not isinstance(query_results[0], dict):
        print("Error: Query results are not in the expected dictionary format.")
        return

    headers = query_results[0].keys()
    if not headers:
        print("Query returned rows with no columns.")
        return
        
    col_widths = {header: len(str(header)) for header in headers}
    for row_data in query_results:
        for header_name in headers:
            col_widths[header_name] = max(col_widths[header_name], len(str(row_data.get(header_name, ''))))

    header_separator_line = " | ".join(f"{'-' * col_widths[header_name]}" for header_name in headers)
    header_line_text = " | ".join(f"{str(header_name):<{col_widths[header_name]}}" for header_name in headers)
    
    print(f"\n{header_line_text}")
    print(header_separator_line)

    for row_data in query_results:
        row_line_text = " | ".join(f"{str(row_data.get(header_name, '')):<{col_widths[header_name]}}" for header_name in headers)
        print(row_line_text)
    print(header_separator_line)
    print(f"{len(query_results)} row(s) returned.\n")

def get_table_metadata(connection, table_name):
    column_details_list = []
    primary_key_columns = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DESCRIBE `{table_name}`;")
            columns_description = cursor.fetchall()
            if not columns_description:
                print(f"Warning: Could not retrieve description for table '{table_name}'. Does it exist?")
                return [], []
            for col_desc in columns_description:
                column_details_list.append({
                    'name': col_desc['Field'], 'type': col_desc['Type'],
                    'nullable': col_desc['Null'].upper() == 'YES', 'key_type': col_desc['Key'],
                    'default_value': col_desc['Default'], 'extra_info': col_desc['Extra']
                })
                if col_desc['Key'] == 'PRI':
                    primary_key_columns.append(col_desc['Field'])
            return column_details_list, primary_key_columns
    except pymysql.Error as e:
        handle_database_error(e, f"fetching metadata for table `{table_name}`")
        return [], []

def handle_database_error(db_error, operation_context="performing a database operation"):
    error_code = db_error.args[0] if len(db_error.args) > 0 else "N/A"
    error_message = db_error.args[1] if len(db_error.args) > 1 else str(db_error)
    
    print(f"\nDATABASE ERROR while {operation_context}:")

    if error_code == 1048:
        col_match = re.search(r"Column '(.*?)' cannot be null", error_message)
        column_name = col_match.group(1) if col_match else "a required field"
        print(f"  > Error: The column '{column_name}' cannot be left empty. It requires a value.")
    elif error_code == 1062:
        dup_match = re.search(r"Duplicate entry '(.*?)' for key '(.*?)'", error_message)
        if dup_match:
            value, key_name = dup_match.group(1), dup_match.group(2)
            print(f"  > Error: The value '{value}' already exists for the unique key '{key_name}'. Please provide a different value.")
        else:
            print("  > Error: A value you entered is a duplicate, but it must be unique.")
    elif error_code == 1451:
         print(f"  > Error: Cannot delete or update this record because other records depend on it (Foreign Key constraint: {error_message}).")
    elif error_code == 1452:
        fk_col_match = re.search(r"FOREIGN KEY \(`(.*?)`\) REFERENCES `(.*?)`", error_message)
        if fk_col_match:
            constrained_col, referenced_table = fk_col_match.group(1), fk_col_match.group(2)
            print(f"  > Error: A value for '{constrained_col}' does not exist in the referenced table '{referenced_table}'. Please check your input (Foreign Key constraint).")
        else:
            print(f"  > Error: A foreign key constraint failed. A related record in another table is missing ({error_message}).")
    elif error_code == 1146:
        tbl_match = re.search(r"Table '.*?\.?(.*?)' doesn't exist", error_message)
        table_name = tbl_match.group(1).strip('`') if tbl_match else "the specified table"
        print(f"  > Error: Table '{table_name}' does not exist. Please check the table name.")
    elif error_code == 1054:
        col_match = re.search(r"Unknown column '(.*?)' in", error_message)
        column_name = col_match.group(1).strip('`') if col_match else "an unknown column"
        print(f"  > Error: Column '{column_name}' is not found in the table or is misspelled.")
    else:
        print(f"  > SQL Error Code: {error_code}")
        print(f"  > Details: {error_message}")
    print("-" * 40)

def get_table_choice(connection, prompt_text="Select a table number or enter its name"):
    print("\n--- Available Tables ---")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            db_tables = cursor.fetchall()
            if not db_tables:
                print("No tables found in the database.")
                return None
            
            table_names_list = [list(tbl.values())[0] for tbl in db_tables]
            for i, tbl_name in enumerate(table_names_list):
                print(f"  {i + 1}. {tbl_name}")
            
            user_input = input(f"{prompt_text}: ").strip()
            if user_input.isdigit():
                choice_idx = int(user_input) - 1
                if 0 <= choice_idx < len(table_names_list):
                    return table_names_list[choice_idx]
                else:
                    print("Invalid table number selected.")
                    return None
            elif user_input in table_names_list:
                return user_input
            else:
                if user_input:
                    print(f"Warning: '{user_input}' was not in the listed tables. Attempting to use this name.")
                    return user_input
                print("No table selected or invalid input.")
                return None
    except pymysql.Error as e:
        handle_database_error(e, "listing tables")
        return None

def view_table_contents(connection):
    target_table = get_table_choice(connection, "Enter table number/name to view its contents")
    if not target_table:
        return

    print(f"\n--- Contents of table: `{target_table}` ---")
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{target_table}`;")
            table_data = cursor.fetchall()
            display_results_as_table(table_data)
    except pymysql.Error as e:
        handle_database_error(e, f"viewing data from `{target_table}`")

def insert_new_record(connection):
    target_table = get_table_choice(connection, "Enter table number/name to add a record to")
    if not target_table:
        return

    column_metadata, _ = get_table_metadata(connection, target_table)
    if not column_metadata:
        return

    print(f"\n--- Adding New Record to `{target_table}` ---")
    print("Enter values for each column. Type 'NULL' (case-insensitive) for SQL NULL if allowed.")
    
    insert_columns = []
    insert_values_placeholders = []
    actual_values_to_insert = []

    for col_meta in column_metadata:
        col_name = col_meta['name']
        col_type_info = col_meta['type']
        is_col_nullable = col_meta['nullable']
        is_auto_incremented = 'auto_increment' in col_meta.get('extra_info', '').lower()

        if is_auto_incremented:
            print(f"  Skipping '{col_name}' ({col_type_info}) - (auto-increment).")
            continue

        prompt_msg = f"  > {col_name} ({col_type_info})"
        if is_col_nullable:
            prompt_msg += " (optional, press Enter or type 'NULL' for NULL): "
        else:
            prompt_msg += " (required): "
        
        user_val_str = input(prompt_msg).strip()

        insert_columns.append(f"`{col_name}`")
        insert_values_placeholders.append('%s')

        if user_val_str.upper() == 'NULL':
            if is_col_nullable:
                actual_values_to_insert.append(None)
            else:
                print(f"    Warning: '{col_name}' is not nullable. 'NULL' string will be inserted if column type allows text, or might error.")
                actual_values_to_insert.append(user_val_str)
        elif not user_val_str and is_col_nullable:
            actual_values_to_insert.append(None)
        elif not user_val_str and not is_col_nullable:
            print(f"    Error: Value for '{col_name}' is required and cannot be empty. Aborting record addition.")
            return
        else:
            actual_values_to_insert.append(user_val_str)

    if not insert_columns:
        print("No columns are available for data insertion (e.g., table might only contain auto-increment columns).")
        return

    sql_insert_query = f"INSERT INTO `{target_table}` ({', '.join(insert_columns)}) VALUES ({', '.join(insert_values_placeholders)});"
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_insert_query, tuple(actual_values_to_insert))
        connection.commit()
        print(f"Record successfully added to `{target_table}`!")
    except pymysql.Error as e:
        handle_database_error(e, f"adding record to `{target_table}`")
        connection.rollback()

def modify_existing_record(connection):
    target_table = get_table_choice(connection, "Enter table number/name to update a record in")
    if not target_table:
        return

    column_metadata, pk_cols = get_table_metadata(connection, target_table)
    if not column_metadata: return

    if not pk_cols:
        print(f"Update Aborted: Table `{target_table}` does not have a defined primary key. Updates via this menu require a primary key.")
        print("You can use the 'Execute Custom SQL Query' option for tables without PKs or for complex updates.")
        return

    print(f"\n--- Updating Record in `{target_table}` ---")
    print(f"Primary Key column(s) for this table: {', '.join([f'`{pk}`' for pk in pk_cols])}")
    print("Please enter the current values for these primary key column(s) to identify the record:")

    pk_where_conditions = []
    pk_where_values = []
    for pk_col_name in pk_cols:
        pk_val = input(f"  Value for PK column '{pk_col_name}': ").strip()
        if not pk_val:
            print(f"Primary key value for '{pk_col_name}' cannot be empty. Update aborted.")
            return
        pk_where_conditions.append(f"`{pk_col_name}` = %s")
        pk_where_values.append(pk_val)
    
    sql_where_clause = " AND ".join(pk_where_conditions)

    print("\nWhich column(s) would you like to update? (Primary key columns cannot be updated here)")
    update_set_clauses = []
    update_set_values = []
    made_a_change = False

    for col_meta in column_metadata:
        col_name = col_meta['name']
        if col_name in pk_cols:
            continue

        user_choice = input(f"  Update column '{col_name}' ({col_meta['type']})? (y/N default is No): ").strip().lower()
        if user_choice == 'y':
            made_a_change = True
            new_val_str = input(f"    Enter new value for '{col_name}' (type 'NULL' for SQL NULL if allowed): ").strip()
            update_set_clauses.append(f"`{col_name}` = %s")
            if new_val_str.upper() == 'NULL' and col_meta['nullable']:
                update_set_values.append(None)
            elif new_val_str.upper() == 'NULL' and not col_meta['nullable']:
                print(f"    Warning: Column '{col_name}' is not nullable. 'NULL' string will be inserted or may cause an error.")
                update_set_values.append(new_val_str)
            else:
                update_set_values.append(new_val_str)
    
    if not made_a_change:
        print("No columns were selected for update. Operation cancelled.")
        return

    sql_update_query = f"UPDATE `{target_table}` SET {', '.join(update_set_clauses)} WHERE {sql_where_clause};"
    all_sql_values = tuple(update_set_values + pk_where_values)

    try:
        with connection.cursor() as cursor:
            rows_affected_count = cursor.execute(sql_update_query, all_sql_values)
        connection.commit()
        if rows_affected_count > 0:
            print(f"{rows_affected_count} record(s) in `{target_table}` updated successfully!")
        else:
            print("No records matched the primary key criteria, or the new data was identical to the existing data.")
    except pymysql.Error as e:
        handle_database_error(e, f"updating record in `{target_table}`")
        connection.rollback()

def remove_record(connection):
    target_table = get_table_choice(connection, "Enter table number/name to delete a record from")
    if not target_table:
        return

    column_metadata, pk_cols = get_table_metadata(connection, target_table)
    if not column_metadata: return

    if not pk_cols:
        print(f"Delete Aborted: Table `{target_table}` has no defined primary key. Deletions via this menu require a primary key.")
        return

    print(f"\n--- Deleting Record from `{target_table}` ---")
    print(f"Primary Key column(s): {', '.join([f'`{pk}`' for pk in pk_cols])}")
    print("Enter values for these primary key column(s) to identify the record for deletion:")

    pk_where_conditions_sql = []
    pk_where_values_sql = []
    pk_display_conditions = []

    for pk_col_name in pk_cols:
        pk_val = input(f"  Value for PK column '{pk_col_name}': ").strip()
        if not pk_val:
            print(f"Primary key value for '{pk_col_name}' cannot be empty. Delete aborted.")
            return
        pk_where_conditions_sql.append(f"`{pk_col_name}` = %s")
        pk_where_values_sql.append(pk_val)
        pk_display_conditions.append(f"`{pk_col_name}` = '{pk_val}'")
    
    sql_where_clause_for_delete = " AND ".join(pk_where_conditions_sql)
    display_where_clause = " AND ".join(pk_display_conditions)

    confirm_delete = input(f"Are you absolutely sure you want to delete record(s) from `{target_table}` WHERE {display_where_clause}? This cannot be undone. (yes/no): ").strip().lower()
    if confirm_delete != 'yes':
        print("Deletion operation cancelled by user.")
        return

    sql_delete_query = f"DELETE FROM `{target_table}` WHERE {sql_where_clause_for_delete};"
    
    try:
        with connection.cursor() as cursor:
            rows_affected_count = cursor.execute(sql_delete_query, tuple(pk_where_values_sql))
        connection.commit()
        if rows_affected_count > 0:
            print(f"{rows_affected_count} record(s) successfully deleted from `{target_table}`.")
        else:
            print("No records matched the primary key criteria for deletion.")
    except pymysql.Error as e:
        handle_database_error(e, f"deleting record from `{target_table}`")
        connection.rollback()

def run_user_custom_sql(connection):
    print("\n--- Execute Custom SQL Query ---")
    print("Enter your SQL query below. For DML (INSERT, UPDATE, DELETE), changes will be committed.")
    print("For SELECT queries, results will be displayed.")
    custom_query = input("SQL> ").strip()

    if not custom_query:
        print("No query entered. Returning to menu.")
        return

    is_data_returning_query = custom_query.strip().upper().startswith(("SELECT", "SHOW", "DESC", "EXPLAIN"))

    try:
        with connection.cursor() as cursor:
            if is_data_returning_query:
                cursor.execute(custom_query)
                query_data = cursor.fetchall()
                display_results_as_table(query_data)
            else:
                affected_rows = cursor.execute(custom_query)
                connection.commit()
                print(f"Query executed. {affected_rows if affected_rows is not None else 'Unknown'} row(s) affected. Commit successful.")
    except pymysql.Error as e:
        handle_database_error(e, f"executing custom query: {custom_query[:50]}...")
        if not is_data_returning_query:
            try:
                connection.rollback()
                print("Transaction rolled back due to error.")
            except pymysql.Error as rb_err:
                print(f"Error during rollback attempt: {rb_err}")
    except Exception as general_e:
        print(f"An unexpected error occurred: {general_e}")

YOUR_PROJECT_QUERIES = {
    "1": {
        "description": "Q1: Interviewers for 'Hellen Cole' and job '11111'.",
        "sql": """
            SELECT e.employee_id, interviewer_person.name AS interviewer_name
            FROM Interview i
            JOIN Job_Application ja ON i.applicationID = ja.applicationID
            JOIN Person applicant_person ON ja.person_id = applicant_person.person_id
            JOIN Job_Position jp ON ja.jobID = jp.jobID
            JOIN Interview_Interviewer ii ON i.interviewID = ii.interview_id
            JOIN Interviewer ir ON ii.interviewer_id = ir.interviewer_id
            JOIN Employee e ON ir.employee_id = e.employee_id
            JOIN Person interviewer_person ON e.person_id = interviewer_person.person_id
            WHERE jp.jobID = 11111 AND applicant_person.name = 'Hellen Cole';
        """
    },
    "2": {
        "description": "Q2: Jobs posted by 'Marketing' in Jan 2011.",
        "sql": """
            SELECT jp.jobID, jp.description
            FROM Job_Position jp
            JOIN Department d ON jp.departmentID = d.departmentID 
            WHERE d.name = 'Marketing'
              AND MONTH(jp.postedDate) = 1
              AND YEAR(jp.postedDate) = 2011;
        """
    },
    "3": {
        "description": "Q3: Employees with no supervisees.",
        "sql": """
            SELECT e1.employee_id, p.name AS employee_name
            FROM Employee e1
            JOIN Person p ON e1.person_id = p.person_id
            WHERE e1.employee_id NOT IN (
                SELECT DISTINCT e2.supervised_by 
                FROM Employee e2 
                WHERE e2.supervised_by IS NOT NULL
            );
        """
    },
    "4": {
        "description": "Q4: Marketing sites with no sales in March 2011.",
        "sql": """
            SELECT ms.siteID, ms.name AS site_name, ms.location
            FROM Marketing_Site ms
            WHERE ms.siteID NOT IN (
                SELECT DISTINCT sh.siteID 
                FROM Sales_History sh
                WHERE MONTH(sh.sale_date) = 3 AND YEAR(sh.sale_date) = 2011 AND sh.siteID IS NOT NULL
            );
        """
    },
    "5": {
        "description": "Q5: Jobs with no suitable hires one month after posting. (Handles text grades)",
        "sql": """
            SELECT jp.jobID, jp.description
            FROM Job_Position jp
            WHERE jp.jobID NOT IN (
                SELECT ja.jobID
                FROM Job_Application ja
                JOIN Interview i ON ja.applicationID = i.applicationID
                GROUP BY ja.jobID
                HAVING AVG(
                    CASE LCASE(i.grade)
                        WHEN 'a+' THEN 95 WHEN 'a' THEN 90
                        WHEN 'b+' THEN 85 WHEN 'b' THEN 80
                        WHEN 'c+' THEN 75 WHEN 'c' THEN 70
                        WHEN 'd' THEN 60 ELSE CAST(i.grade AS SIGNED)
                    END
                ) > 70 AND COUNT(DISTINCT i.interviewID) >= 5
            )
            AND jp.postedDate < DATE_SUB(CURDATE(), INTERVAL 1 MONTH);
        """
    },
    "6": {
        "description": "Q6: Salesmen who sold all product types priced > $200.",
        "sql": """
            SELECT DISTINCT e.employee_id, p.name AS salesman_name
            FROM Employee e
            JOIN Person p ON e.person_id = p.person_id
            WHERE e.employee_id IN (SELECT DISTINCT employee_id FROM Sales_History)
            AND NOT EXISTS (
                SELECT pt.productType
                FROM Product pt
                WHERE pt.listPrice > 200
                AND NOT EXISTS (
                    SELECT 1
                    FROM Sales_History sh
                    JOIN Sale_Product sp ON sh.sale_id = sp.sale_id
                    JOIN Product p_sold ON sp.product_id = p_sold.product_id
                    WHERE sh.employee_id = e.employee_id AND p_sold.productType = pt.productType AND p_sold.listPrice > 200
                )
            );
        """
    },
    "7": {
        "description": "Q7: Departments with no job posts in Jan-Feb 2011.",
        "sql": """
            SELECT d.departmentID, d.name AS department_name
            FROM Department d
            WHERE d.departmentID NOT IN (
                SELECT DISTINCT jp.departmentID
                FROM Job_Position jp
                WHERE jp.postedDate BETWEEN '2011-01-01' AND '2011-02-28'
                AND jp.departmentID IS NOT NULL
            );
        """
    },
    "8": {
        "description": "Q8: Existing employees who applied for job '12345'.",
        "sql": """
            SELECT DISTINCT p.name AS applicant_name, e.employee_id, ed.departmentID AS current_department_id
            FROM Employee e
            JOIN Person p ON e.person_id = p.person_id
            JOIN Job_Application ja ON ja.person_id = p.person_id
            LEFT JOIN Employee_Department ed ON e.employee_id = ed.employee_id 
            WHERE ja.jobID = 12345;
        """
    },
    "9": {
        "description": "Q9: Best selling product type (most items sold - uses View3).",
        "sql": "SELECT productType FROM View3 ORDER BY total_items_sold DESC LIMIT 1;"
    },
    "10": {
        "description": "Q10: Product type with highest net profit (uses View4).",
        "sql": """
            SELECT 
                p.productType,
                (SUM(sp.quantity * sp.unitPrice) - IFNULL(SUM(sp.quantity * v.total_part_cost), 0)) AS profit
            FROM Sale_Product sp
            JOIN Product p ON sp.product_id = p.product_id
            LEFT JOIN View4 v ON p.product_id = v.product_id
            GROUP BY p.productType
            ORDER BY profit DESC
            LIMIT 1;
        """
    },
    "11": {
        "description": "Q11: Employees who worked in all departments.",
        "sql": """
            SELECT e.employee_id, p.name AS employee_name
            FROM Employee e
            JOIN Person p ON e.person_id = p.person_id
            WHERE (
                SELECT COUNT(DISTINCT ed.departmentID) 
                FROM Employee_Department ed 
                WHERE ed.employee_id = e.employee_id
            ) = (
                SELECT COUNT(*) FROM Department
            );
        """
    },
    "12": {
        "description": "Q12: Name and email of selected interviewees (avg grade > 70, >= 5 rounds).",
        "sql": """
            SELECT p.name AS interviewee_name, p.email AS interviewee_email, p.person_id
            FROM Interview i
            JOIN Job_Application ja ON i.applicationID = ja.applicationID
            JOIN Person p ON ja.person_id = p.person_id
            GROUP BY p.person_id, p.name, p.email
            HAVING AVG(
                CASE LCASE(i.grade)
                    WHEN 'a+' THEN 95 WHEN 'a' THEN 90
                    WHEN 'b+' THEN 85 WHEN 'b' THEN 80
                    WHEN 'c+' THEN 75 WHEN 'c' THEN 70
                    WHEN 'd' THEN 60 ELSE CAST(i.grade AS SIGNED)
                END
            ) > 70 AND COUNT(DISTINCT i.interviewID) >= 5; 
        """
    },
    "13": {
        "description": "Q13: Name, phone, email of interviewees selected for ALL jobs they applied for.",
        "sql": """
            SELECT p.name, p.email, GROUP_CONCAT(DISTINCT ph.phone_number) AS phone_numbers
            FROM Person p
            JOIN Job_Application ja ON p.person_id = ja.person_id
            LEFT JOIN Phone ph ON p.person_id = ph.person_id
            WHERE NOT EXISTS (
                SELECT 1
                FROM Job_Application ja_check
                WHERE ja_check.person_id = p.person_id
                AND NOT EXISTS (
                    SELECT 1
                    FROM Interview i_check
                    WHERE i_check.applicationID = ja_check.applicationID
                    GROUP BY i_check.applicationID
                    HAVING AVG(
                        CASE LCASE(i_check.grade)
                            WHEN 'a+' THEN 95 WHEN 'a' THEN 90
                            WHEN 'b+' THEN 85 WHEN 'b' THEN 80
                            WHEN 'c+' THEN 75 WHEN 'c' THEN 70
                            WHEN 'd' THEN 60 ELSE CAST(i_check.grade AS SIGNED)
                        END
                    ) > 70 AND COUNT(DISTINCT i_check.interviewID) >= 5
                )
            )
            GROUP BY p.person_id, p.name, p.email
            HAVING COUNT(DISTINCT ja.jobID) > 0;
        """
    },
    "14": {
        "description": "Q14: Employee with highest average monthly salary (uses View1).",
        "sql": "SELECT e.employee_id, p.name AS employee_name, v1.avg_monthly_salary FROM View1 v1 JOIN Employee e ON v1.employee_id = e.employee_id JOIN Person p ON e.person_id = p.person_id ORDER BY v1.avg_monthly_salary DESC LIMIT 1;"
    },
    "15": {
        "description": "Q15: Vendor for 'Cup' < 4 lbs (part type) at lowest price.",
        "sql": """
            SELECT v.vendorID, v.name AS vendor_name, p.price
            FROM Vendor v
            JOIN Vendor_Part vp ON v.vendorID = vp.vendorID
            JOIN Part p ON vp.part_id = p.part_id
            WHERE p.partType = 'Cup' AND p.weight < 4.0
            AND p.price = (
                SELECT MIN(p2.price)
                FROM Part p2
                WHERE p2.partType = 'Cup' AND p2.weight < 4.0
            )
            ORDER BY v.vendorID
            LIMIT 1;
        """
    }
}

def execute_defined_project_queries(connection):
    print("\n--- Predefined Project SQL Queries ---")
    query_keys = list(YOUR_PROJECT_QUERIES.keys())
    for key_num_str in query_keys:
        print(f"  {key_num_str}. {YOUR_PROJECT_QUERIES[key_num_str]['description']}")
    
    user_choice = input("Select query number to execute (or 'm' for main menu): ").strip()
    if user_choice.lower() == 'm':
        return
    
    if user_choice in YOUR_PROJECT_QUERIES:
        selected_query_info = YOUR_PROJECT_QUERIES[user_choice]
        print(f"\nExecuting: {selected_query_info['description']}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(selected_query_info['sql'])
                query_data = cursor.fetchall()
                display_results_as_table(query_data)
        except pymysql.Error as e:
            handle_database_error(e, f"executing project query Q{user_choice}")
        except Exception as general_e:
            print(f"An unexpected error occurred: {general_e}")
    else:
        print("Invalid query number selected.")

def display_main_console_menu(connection):
    while True:
        print("\n M A I N   M E N U ")
        print("------------------------------------------")
        print("  1. View Table Contents")
        print("  2. Add New Record to Table")
        print("  3. Update Existing Record in Table (by PK)")
        print("  4. Delete Record from Table (by PK)")
        print("  5. Execute Custom SQL Query")
        print("  6. Run Predefined Project Queries")
        print("  7. List All Tables")
        print("  8. Describe a Table (Show Columns)")
        print("  0. Exit Application")
        print("------------------------------------------")
        
        user_selection = input("Enter your choice: ").strip()

        if user_selection == '1':
            view_table_contents(connection)
        elif user_selection == '2':
            insert_new_record(connection)
        elif user_selection == '3':
            modify_existing_record(connection)
        elif user_selection == '4':
            remove_record(connection)
        elif user_selection == '5':
            run_user_custom_sql(connection)
        elif user_selection == '6':
            execute_defined_project_queries(connection)
        elif user_selection == '7':
            get_table_choice(connection, "Tables are listed. Press Enter to return to menu or select a table to see its name again.")
        elif user_selection == '8':
            target_table = get_table_choice(connection, "Enter table number/name to describe")
            if target_table:
                column_meta, _ = get_table_metadata(connection, target_table)
                if column_meta:
                    print(f"\n--- Schema for Table: `{target_table}` ---")
                    headers = column_meta[0].keys()
                    col_widths = {h: len(str(h)) for h in headers}
                    for cm_row in column_meta:
                        for h in headers:
                            col_widths[h] = max(col_widths[h], len(str(cm_row.get(h, ''))))
                    
                    header_line = " | ".join(f"{str(h).upper():<{col_widths[h]}}" for h in headers)
                    print(header_line)
                    print("-|-".join(f"{'-'*col_widths[h]}" for h in headers))
                    for cm_row in column_meta:
                        print(" | ".join(f"{str(cm_row.get(h, '')):<{col_widths[h]}}" for h in headers))
                    print("-" * len(header_line.replace(" | ","-|-")))
        elif user_selection == '0':
            print("Exiting Database Console. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option from the menu.")

if __name__ == "__main__":
    print("--- Welcome to the XYZ Company Database Console ---")
    active_connection = establish_db_connection()
    
    if active_connection:
        try:
            display_main_console_menu(active_connection)
        except Exception as e:
            print(f"An unexpected critical error occurred in the main application: {e}")
        finally:
            active_connection.close()
            print("Database connection has been closed.")
    else:
        print("Application cannot start due to database connection failure.")

        