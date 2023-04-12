from openpyxl import load_workbook
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

FILENAME = os.getenv("FILENAME", None)
wb = load_workbook(filename=FILENAME)

rows = list(wb._sheets[0].rows)

treatment_jobsheet_date = wb._sheets[0]["B1"].value

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
