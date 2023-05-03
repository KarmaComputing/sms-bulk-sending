import os
from openpyxl import load_workbook
import requests


def extract_customer_numbers_from_spreadsheet(filename: str) -> list:
    """Extract customers numbers from spreadsheet
    retuns: list of numbers numbers_to_contact"""

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")

    wb = load_workbook(filename=f"{UPLOAD_FOLDER}/{filename}")

    rows = list(wb._sheets[0].rows)

    # Cut off row one with data, and row two with column headers
    rows = rows[2:-1]

    customer_ref_column_number = 2  # (Column C)

    customers_with_upcoming_jobs = []

    for row in rows:
        if row[customer_ref_column_number].value is None:
            print(
                "customer ref was None in Treatment Job Sheet, so stopping processing"  # noqa: E501
            )  # noqa: E501
            break
        customer_ref = row[customer_ref_column_number].value
        print(f"customer_ref {customer_ref}")
        customers_with_upcoming_jobs.append(customer_ref)

    # Locate customer PhoneNumber based on customer_ref number inside
    # customers_with_upcoming_jobs, get their phone number from sheet
    # called 'Contacts_Prices_Comments' column 'PhoneNumber'
    # (column 6 / column 'G')
    # TODO we're **assumming** 'PhoneNumber' is a mobile, which is obviously
    # wrong.

    sheet_customer_list_contacts_prices_comments = list(wb._sheets[4].rows)
    PhoneNumberColumn = 6

    sheet_customer_list_contacts_prices_comments[1:-1]  # cut off heading

    # Find the contact number for a given customer
    numbers_to_contact = []

    # Loop customers with upcoming jobs
    for customer_ref in customers_with_upcoming_jobs:
        for row in sheet_customer_list_contacts_prices_comments:
            if customer_ref == row[0].value:
                # Locate customers phone number
                numbers_to_contact.append(row[PhoneNumberColumn].value)

    return numbers_to_contact


def send_sms(to_number: str, msg: str):
    print("About to send sms")
    # Send the message to each mobile number
    url = "https://api.budgetsms.net/sendsms/"
    breakpoint()
    BUDGETSMS_API_KEY = os.getenv("BUDGETSMS_API_KEY")
    BUDGETSMS_USER_ID = os.getenv("BUDGETSMS_USER_ID")
    BUDGETSMS_SENDER_ID = os.getenv("BUDGETSMS_SENDER_ID")
    BUDGETSMS_USERNAME = os.getenv("BUDGETSMS_USERNAME")

    params = {
        "username": BUDGETSMS_USERNAME,
        "userid": BUDGETSMS_USER_ID,
        "handle": BUDGETSMS_API_KEY,
        "from": BUDGETSMS_SENDER_ID,
        "to": to_number,
        "msg": msg,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200 and response.text != "ERR 1001":
        print(f"Message successfully sent to {to_number}.")
    else:
        print(
            f"Failed to send message to {to_number}. Response code: {response.status_code} Response text: {response.text}."  # noqa: E501
        )
