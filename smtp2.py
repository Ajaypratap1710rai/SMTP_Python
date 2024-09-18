import csv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Fixed recipient email address
smtp_server = 'smtp.gmail.com'
port = 587
RECIPIENT_EMAIL = '###########@gmail.com'        #Developer Mail ID
FIXED_PASSWORD = '################'              # 16 Digit Pass_Key

def send_email(subject, body, from_email, attachment_path=None):
    """Send an email notification with optional attachment."""
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment_path:
        try:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                msg.attach(part)
        except Exception as e:
            print(f"Error attaching file: {e}")

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(RECIPIENT_EMAIL, FIXED_PASSWORD)
            server.sendmail(RECIPIENT_EMAIL, from_email, msg.as_string())
        print(f"Notification email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"Error sending email: {e}")

def check_and_create_csv(file_path, headers):
    """Create a CSV file with given headers if it does not already exist."""
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
        print(f"{file_path} created with headers: {headers}")
        send_email(
            "CSV File Created",
            f"The CSV file {file_path} was created with headers: {headers}",
            from_email
        )
    else:
        print(f"{file_path} already exists.")

def write_record(file_path, record):
    """Append a record to the CSV file."""
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(record)
    print(f"Record {record} added to {file_path}.")
    send_email(
        "Record Added",
        f"A new record was added to {file_path}: {record}",
        from_email
    )

def update_record(file_path, old_record, new_record):
    """Update a specific record in the CSV file."""
    updated = False
    rows = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)

    for i, row in enumerate(rows):
        if row == old_record:
            rows[i] = new_record
            updated = True
            break
    if updated:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        print(f"Record {old_record} updated to {new_record}.")
        send_email(
            "Record Updated",
            f"The record {old_record} was updated to {new_record} in {file_path}.",
            from_email
        )
    else:
        print(f"Record {old_record} not found.")

def delete_record(file_path, record):
    """Delete a specific record from the CSV file."""
    rows = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = [row for row in reader if row != record]

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    print(f"Record {record} deleted.")
    send_email(
        "Record Deleted",
        f"The record {record} was deleted from {file_path}.",
        from_email
    )

def main():
    """Main function to interact with the user and perform operations."""
    global from_email
    from_email = input("Enter your email address: ").strip()
    
    if not from_email:
        print("Error: Email address is required.")
        return

    csv_file_path = input("Enter the path to the CSV file: ").strip()

    if not os.path.exists(csv_file_path):
        headers = input("Enter the headers for the CSV file (comma-separated): ").strip().split(',')
        headers = [header.strip() for header in headers]  # Clean up any extra spaces
        check_and_create_csv(csv_file_path, headers)
    else:
        print(f"{csv_file_path} already exists.")
        # Load headers from existing file
        with open(csv_file_path, mode='r', newline='') as file:
            headers = next(csv.reader(file))
    
    operations_log = []

    while True:
        operation = input("Choose operation: write, update, delete, or exit: ").strip().lower()

        if operation == 'write':
            record = input("Enter the record to write (comma-separated): ").strip().split(',')
            record = [field.strip() for field in record]  # Clean up any extra spaces
            if len(record) == len(headers):
                write_record(csv_file_path, record)
                operations_log.append(f"Added: {record}")
            else:
                print("Error: Record length does not match headers length.")
        elif operation == 'update':
            old_record = input("Enter the old record to update (comma-separated): ").strip().split(',')
            new_record = input("Enter the new record (comma-separated): ").strip().split(',')
            old_record = [field.strip() for field in old_record]
            new_record = [field.strip() for field in new_record]
            if len(new_record) == len(headers):
                update_record(csv_file_path, old_record, new_record)
                operations_log.append(f"Updated: {old_record} to {new_record}")
            else:
                print("Error: New record length does not match headers length.")
        elif operation == 'delete':
            record = input("Enter the record to delete (comma-separated): ").strip().split(',')
            record = [field.strip() for field in record]
            if len(record) == len(headers):
                delete_record(csv_file_path, record)
                operations_log.append(f"Deleted: {record}")
            else:
                print("Error: Record length does not match headers length.")
        elif operation == 'exit':
            print("Exiting.")
            break
        else:
            print("Invalid operation. Please choose 'write', 'update', 'delete', or 'exit'.")

    # Notify via email after completing CSV operations
    operations_summary = "\n".join(operations_log)
    send_email(
        "CSV Operations Completed",
        f"Operations on the CSV file {csv_file_path} have been completed:\n{operations_summary}",
        from_email,
        attachment_path=csv_file_path  # Attach the CSV file
    )

if __name__ == "__main__":
    main()
