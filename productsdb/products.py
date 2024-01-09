import argparse
import sqlite3
from datetime import datetime
import os

db_path = ''  # Specify the full path to the database

PRODUCTS_WITH_OWN_LORAID = ['ME', 'THL', 'THLM', 'DL', 'TH']

def init_db_path(path):
    global db_path
    db_path = path

def get_next_serial(cursor):
    cursor.execute("SELECT LoraID FROM products WHERE MAKE = 'RC' ORDER BY LoraID DESC LIMIT 1;")
    row = cursor.fetchone()
    if row:
        serial = row[0] + 1
        if serial >= 4294967295:
            serial = 359956882
    else:
        serial = 359956882  # Set initial SerialID to 2024 if no records found
    return serial


def database_exists():
    global db_path
    return os.path.exists(db_path)


def create_db():
    global db_path
    if not database_exists():
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE products (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ManufacturingOrder TEXT,
            Make TEXT,
            Model TEXT,
            Variant TEXT,
            LoraID INTEGER,
            TestingDateCode TEXT,
            SerialNumber TEXT,
            HardwareVersion TEXT,
            HardwareBatch TEXT,
            SoftwareVersion TEXT,
            Technician TEXT,
            TestDate TEXT,
            PassedAllTests BOOLEAN,
            Comments LONGTEXT
        )''')
        conn.commit()
        conn.close()

def add_product(manufacturing_order, make, model, variant, lora_id, serial_number, hardware_version, hardware_batch,
                software_version, technician, passed_all_tests, comments):
    global db_path
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # if lora_id is none it means the product needs a serial number to be generated (ex: RC's)
    if(lora_id == None):
        lora_id_int = get_next_serial(c)
        lora_id_hex = format(lora_id_int, '08X')  # Convert serial_id to 8-digit hexadecimal

    current_date = datetime.now()
    testing_date_code = hardware_batch
    barcode_number = f'{make}-{model}-{lora_id_hex}'
        
    #barcode_number = f'{make}-{model}-{serial_number}'
    test_date = current_date.strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''
         INSERT INTO products (
             ManufacturingOrder,
             Make,
             Model,
             Variant,
             LoraID,
             TestingDateCode,
             SerialNumber,
             HardwareVersion,
             HardwareBatch,
             SoftwareVersion,
             Technician,
             TestDate,
             PassedAllTests,
             Comments
         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
     ''', (manufacturing_order, make, model, variant, lora_id_int, testing_date_code, serial_number, hardware_version, hardware_batch,
           software_version, technician, test_date, passed_all_tests, comments))

    conn.commit()
    conn.close()
    return barcode_number

def update_product(new_manufacturing_order, barcode, new_serial_number, new_hardware_version, new_hardware_batch, new_software_version, new_technician, new_passed_all_tests, new_comments):
    global db_path

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Split the barcode and extract the necessary fields to identify the record
    make, model, lora_id = barcode.split('-')
    if(make not in PRODUCTS_WITH_OWN_LORAID):
        lora_id = int(lora_id, 16)

    # Update the product in the database
    c.execute('''
        UPDATE products
        SET SerialNumber = ?,
            ManufacturingOrder = ?,
            HardwareVersion = ?,
            HardwareBatch = ?,
            SoftwareVersion = ?,
            Technician = ?,
            PassedAllTests = ?,
            Comments = ?
        WHERE Make = ? AND Model = ? AND LoraID = ?
    ''', (new_serial_number, new_manufacturing_order, new_hardware_version, new_hardware_batch, new_software_version, new_technician, new_passed_all_tests, new_comments, make, model, lora_id))

    conn.commit()
    conn.close()
    return barcode

def get_products_by_work_order(work_order):
    global db_path
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Query the database to find products with the specified TestingDateCode
    c.execute('''
        SELECT * FROM products
        WHERE ManufacturingOrder = ?
    ''', (work_order,))

    products = c.fetchall()
    conn.close()

    return products

def get_products_by_batch_id(date_code):
    global db_path
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Query the database to find products with the specified TestingDateCode
    c.execute('''
        SELECT * FROM products
        WHERE TestingDateCode = ?
    ''', (date_code,))

    products = c.fetchall()
    conn.close()

    return products

def get_serial_number_for_work_order(work_order):

    global db_path
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Query the database to find products with the specified TestingDateCode
    c.execute('''
        SELECT * FROM products
        WHERE ManufacturingOrder = ?
    ''', (work_order,))

    products = c.fetchall()
    conn.close()

    return products

def get_products_barcode_by_work_order(work_order):
    global db_path
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Query the database to find products with the specified TestingDateCode
    c.execute('''
        SELECT * FROM products
        WHERE ManufacturingOrder = ?
    ''', (work_order,))

    products = c.fetchall()
    barcodes = []
    for product in products:
        make = product[2]
        model = product[3]
        serial_id_int = product[5]

        bar_code_id_hex = format(serial_id_int, '08X')  # Convert serial_id to 8-digit hexadecimal
        barcode_number = f'{make}-{model}-{bar_code_id_hex}'
        print(barcode_number)
        barcodes.append(barcode_number)

    # Create a file and write the processed data to it
    output_file_path = f"barcodes_{work_order}.txt"
    with open(output_file_path, "w") as output_file:
        for barcode_number in barcodes:
            output_file.write(barcode_number + "\n")
    conn.close()

    return products

def get_report_data_by_work_order(work_order):
    global db_path
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Query the database to find products with the specified TestingDateCode
    c.execute('''
        SELECT * FROM products
        WHERE ManufacturingOrder = ?
    ''', (work_order,))

    products = c.fetchall()
    lines = []
    for product in products:
        make = product[2]
        model = product[3]
        serial_id_int = product[5]
        comments = product[14]

        # check if product had a generated serial number and if we need to convert it to hex
        if(make not in PRODUCTS_WITH_OWN_LORAID):
            bar_code_id_hex = format(serial_id_int, '08X')  # Convert serial_id to 8-digit hexadecimal
            barcode_number_and_test_info = f'{make}-{model}-{bar_code_id_hex}\t{comments}\tTRUE'
        else:
            # product with a non generated serial (ex: microedge)
            barcode_number_and_test_info = f'{make}-{model}-{serial_id_int}\t{comments}\tTRUE'

        print(barcode_number_and_test_info)
        lines.append(barcode_number_and_test_info)

    # Create a file and write the processed data to it
    output_file_path = f"barcodes_{work_order}.txt"
    with open(output_file_path, "w") as output_file:
        for barcode_number_and_test_info in lines:
            output_file.write(barcode_number_and_test_info + "\n")
    conn.close()

    return products

def get_products_by_technician(technician):
    global db_path
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Query the database to find products with the specified TestingDateCode
    c.execute('''
        SELECT * FROM products
        WHERE Technician = ?
    ''', (technician,))

    products = c.fetchall()
    conn.close()

    return products


def get_product(barcode):
    global db_path
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Split the barcode and extract the necessary fields to identify the record
        make, model, lora_id = barcode.split('-')
        
        if(make not in PRODUCTS_WITH_OWN_LORAID):
            lora_id = int(lora_id, 16)  # Convert hex to int

        # Query the database to find the product
        c.execute('''
            SELECT * FROM products
            WHERE Make = ? AND Model = ? AND LoraID = ?
        ''', (make, model, lora_id))

        product = c.fetchone()
    finally:
        conn.close()

    return product

def delete_product(barcode):
    global db_path
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Split the barcode and extract the necessary fields to identify the record
        make, model, lora_id = barcode.split('-')
        if(make not in PRODUCTS_WITH_OWN_LORAID):
            lora_id = int(lora_id, 16)  # Convert hex to int

        # Delete the record from the database
        c.execute('''
            DELETE FROM products
            WHERE Make = ? AND Model = ? AND LoraID = ?
        ''', (make, model, lora_id))

        # Commit the changes
        conn.commit()

        # Check if any rows were affected (record deleted)
        if conn.total_changes > 0:
            return f"Record with barcode {barcode} deleted successfully."
        else:
            return f"No record found with barcode {barcode}. Nothing deleted."
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        conn.close()

# Usage:
#create_db()
#get_report_data_by_work_order('MO00000')
#get_products_barcode_by_work_order('MO00032')
# Example usage of the add_product function
# if __name__ == "__main__":
    # manufacturing_order = 'M00025'
    # make = "RC"
    # model = '0006'
    # serial_number = "SN123456"
    # hardware_version = "1.2"
    # hardware_batch = "2341"
    # software_version = "SW1.0.1"
    # technician = "John Doe"
    # passed_all_tests = True
    # comments = "All tests passed. Ready for shipping."

    # # Call the add_product function
    # barcode = add_product(manufacturing_order, make, model, serial_number, hardware_version, hardware_batch,
    #             software_version, technician, passed_all_tests, comments)
# update_product(barcode, 'CSN456', '00:AA:BB:CC:DD:EE', '11:22:33:44:55:66', True, 'All tests passed successfully')/
# print(barcode)
# product = get_product(barcode)
# if product:
#     print(product)
# else:
#     print(f"No product found for barcode: {barcode}")
# products = get_products('2344')
# for product in products:
#     print(product)


