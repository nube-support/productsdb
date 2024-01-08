from products import *

def retrieve_product():
    barcode = input('Insert product barcode to retrieve info...\n')

    try:
        product = get_product(barcode)

        if product:
            print(f"Product Info: {product}\n")
        else:
            print("Product not found in the database.\n")
    except Exception as e:
        print(f"An error occurred: {e}")

def remove_product():
    barcode = input('Insert product barcode to delete info...\n')

    try:
        response = delete_product(barcode)
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")

def retrieve_by_batch():
    batch_id = input('Insert batch id to retrieve products...\n')

    try:
        response = get_products_by_batch_id(batch_id)
        if len(response) == 0:
            print(f'No products found for {batch_id}')
        else:
            print(response)    
    except Exception as e:
        print(f"An error occurred: {e}")

def retrieve_by_word_order():
    work_order = input('Insert work/manufacturing order to retrieve products...\n').upper()

    try:
        response = get_products_by_work_order(work_order)
        if len(response) == 0:
            print(f'No products found for {work_order}')
        else:
            print(response)   
    except Exception as e:
        print(f"An error occurred: {e}")

def get_report_data_for_work_order():
    work_order = input('Insert work/manufacturing order to retrieve report data for products...\n').upper()

    try:
        response = get_report_data_by_work_order(work_order)
        if len(response) == 0:
            print(f'No products found for {work_order}')
        else:
            print('***********************************')
            print(f'File with above info saved under: barcodes_{work_order}.txt in this directory.')
    except Exception as e:
        print(f"An error occurred: {e}")


def retrieve_by_technician():
    technician = input('Insert technician name to retrieve products...\n')

    try:
        response = get_products_by_technician(technician)

        if len(response) == 0:
            print(f'No products found for {technician}')
        else:
            print(response)
    except Exception as e:
        print(f"An error occurred: {e}")

def quit_function():
    print('Quitting the program...\n')
    exit()

def main():
    options = {
        '1': retrieve_product,
        '2': retrieve_by_batch,
        '3': retrieve_by_word_order,
        '4': retrieve_by_technician,
        '5': get_report_data_for_work_order,
        '6': remove_product,
        '7': quit_function
    }

    while True:
        print('Choose an option:')
        for key, value in options.items():
            print(f'{key}. {value.__name__.replace("_", " ").capitalize()}')

        user_input = input('Enter your choice: ')

        selected_option = options.get(user_input)
        if selected_option:
            selected_option()
        else:
            print('Invalid choice. Please enter a valid option.\n')

if __name__ == '__main__':
    main()
