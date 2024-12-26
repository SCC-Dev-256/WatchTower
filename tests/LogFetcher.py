#import smtplib
#from email.mime.text import MIMEText

#def send_email_alert(subject, message, recipient_email):
#   msg = MIMEText(message)
#   msg['Subject'] = subject
#   msg['From'] = 'monitor@yourdomain.com'
#   msg['To'] = recipient_email

#   with smtplib.SMTP('smtp.yourdomain.com') as server:
#       server.login('username', 'password')
#        server.sendmail('monitor@yourdomain.com', recipient_email, msg.as_string())

#def on_alert_trigger(ip_addresses):
#    """Trigger log fetch for all IPs upon alert."""
#    for ip in ip_addresses:
#        log_data = fetch_log_data(ip)
#        log_to_file(ip, log_data)


import json
import requests
import logging
import time
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from collections import defaultdict

# Configuration file path
CONFIG_FILE = "config.json"
BASE_URL = "/logdata?format=csv&fields=seq+tmmsec+level+msg"

# Load configuration from file
def load_config():
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    return config

# Save configuration to file
def save_config(file_path, config):
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=4)
    logging.info("Configuration saved.")


# Add a new IP and associated description
def add_ip_with_description(config, new_ip, description):
    if new_ip not in config["ip_descriptions"]:
        config["ip_descriptions"][new_ip] = description
        save_config(config)
        print(f"IP {new_ip} with description '{description}' added.")
    else:
        print(f"IP {new_ip} already exists with description '{config['ip_descriptions'][new_ip]}'.")

# Remove an IP and its description
def remove_ip_with_description(config, ip_to_remove):
    if ip_to_remove in config["ip_descriptions"]:
        del config["ip_descriptions"][ip_to_remove]
        save_config(config)
        print(f"IP {ip_to_remove} and its description removed.")
    else:
        print(f"IP {ip_to_remove} not found.")

# Update an IP's description
def update_ip_description(config, ip, new_description):
    if ip in config["ip_descriptions"]:
        config["ip_descriptions"][ip] = new_description
        save_config(config)
        print(f"Description for IP {ip} updated to '{new_description}'.")
    else:
        print(f"IP {ip} not found.")


# Function to prompt user for IP management actions
def manage_ip_addresses(config):
    print("\nCurrent IP addresses with descriptions:")
    for ip, description in config["ip_descriptions"].items():
        print(f" - {ip}: {description}")

    choice = input("Do you want to add, remove, update, or keep the IP list as-is? (add/remove/update/keep): ").strip().lower()

    if choice == "add":
        new_ip = input("Enter the new IP address to add: ").strip()
        description = input(f"Enter a description for IP {new_ip}: ").strip()
        add_ip_with_description(config, new_ip, description)
    elif choice == "remove":
        ip_to_remove = input("Enter the IP address to remove: ").strip()
        remove_ip_with_description(config, ip_to_remove)
    elif choice == "update":
        ip_to_update = input("Enter the IP address to update: ").strip()
        if ip_to_update in config["ip_descriptions"]:
            new_description = input(f"Enter the new description for IP {ip_to_update}: ").strip()
            update_ip_description(config, ip_to_update, new_description)
        else:
            print(f"IP {ip_to_update} not found.")
    elif choice == "keep":
        print("IP list remains unchanged.")
    else:
        print("Invalid option. Keeping IP list as-is.")


#Updating IP status 
def update_ip_status(config, ip, status, error_count=0):
    current_time = datetime.now().isoformat()
    if ip not in config["ip_status"]:
        config["ip_status"][ip] = {}
    config["ip_status"][ip]["last_checked"] = current_time
    config["ip_status"][ip]["status"] = status
    config["ip_status"][ip]["error_count"] = error_count

# Save JSON configuration to a file
def save_config(file_path, config):
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=4)

# Log fetching function with retry mechanism
def fetch_log_data(ip, config):
    url = f"http://{ip}{BASE_URL}"
    retries = config.get("retry_attempts", 3)
    timeout = config.get("timeout_seconds", 5)
    
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            update_ip_status(config, ip, "Success")
            return response.text  # Return log data if successful
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt+1} failed for {ip}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logging.error(f"Failed to fetch logs from {ip} after {retries} attempts")
                update_ip_status(config, ip, "Failure", error_count=attempt + 1)
                return None



# Save fetched logs to individual CSV files for each IP
def save_log(ip, log_data, config):
    log_directory = config.get("log_directory", "logs/")
    os.makedirs(log_directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{log_directory}/fetched_logs_{ip}_{timestamp}.csv"
    
    with open(filename, 'w') as file:
        file.write(log_data)
    logging.info(f"Log data for IP {ip} saved to {filename}")

#Need to develop location variable to track 
anomalies = {
    "Critical": {
        "details": [],
        "count": 0,
        "location": []
    },
    "Warning": {
        "details": [],
        "count": 0,
        "location": []
    },
    "Info": {
        "details": [],
        "count": 0,
        "location": []
    }
}
#_____________________________________________________________________________________________________________________________________
def validate_ip_description(ip_description):
    return ip_description if ip_description else "Unknown Location"


# Detect Anomalies (Temp needs work) 
    #Needs more anomalies identified
    #Needs more classification
def detect_anomalies(log_data, ip_description):
    ip_description = validate_ip_description(ip_description)  # Ensure description is valid
    for line in log_data.splitlines():
        if "ERROR" in line.upper() or "FAIL" in line.upper():
            anomalies["Critical"]["details"].append(f"Error detected: {line}")
            anomalies["Critical"]["count"] += 1
            anomalies["Critical"]["location"].append(ip_description)

        if "temperature" in line.lower():
            try:
                temp_value = int(line.split()[-1])
                if temp_value >= 70:
                    anomalies["Warning"]["details"].append(f"High Temperature Detected: {line}")
                    anomalies["Warning"]["count"] += 1
                    anomalies["Warning"]["location"].append(ip_description)
            except ValueError:
                anomalies["Info"]["details"].append(f"Temperature value parsing error: {line}")
                anomalies["Info"]["count"] += 1
                anomalies["Info"]["location"].append(ip_description)




#Internet or network congestion
def detect_bandwidth_issues(log_data, ip_description):
    ip_description = validate_ip_description(ip_description)
    bandwidth_keywords = ["bandwidth error", "network congestion"]
    for line in log_data.splitlines():
        if any(keyword in line.lower() for keyword in bandwidth_keywords):
            anomalies["Warning"]["details"].append(f"Bandwidth issue detected: {line}")
            anomalies["Warning"]["count"] += 1
            anomalies["Warning"]["location"].append(ip_description)



#Missing Stream Key
def detect_missing_stream_key(log_data, ip_description):
    ip_description = validate_ip_description(ip_description)
    stream_key_keywords = ["missing stream key", "authentication failed"]
    for line in log_data.splitlines():
        if any(keyword in line.lower() for keyword in stream_key_keywords):
            anomalies["Warning"]["details"].append(f"Stream key issue detected: {line}")
            anomalies["Warning"]["count"] += 1
            anomalies["Warning"]["location"].append(ip_description)



#Storage corrupt reboot cycle
def detect_storage_restart_pattern(log_data, ip_description):
    ip_description = validate_ip_description(ip_description)
    restart_keywords = ["initialization", "assigning", "network access"]
    log_lines = log_data.splitlines()
    
    # Check for small log file (Resetting clears log file)
    if len(log_lines) <= 10:  # Threshold for limited log entries
        # Check for reset keywords in the limited log entries
        if any(keyword in line.lower() for line in log_lines for keyword in restart_keywords):
            anomalies["Critical"]["details"].append("Storage corrupt reboot cycle detected.")
            anomalies["Critical"]["count"] += 1
            anomalies["Critical"]["location"].append(ip_description)

    # Call each individual detection function
def detect_and_group_anomalies(log_data, ip_description):
    detect_anomalies(log_data, ip_description)
    detect_bandwidth_issues(log_data, ip_description)
    detect_missing_stream_key(log_data, ip_description)
    detect_storage_restart_pattern(log_data, ip_description)


def validate_anomalies():
    for severity, data in anomalies.items():
        details_length = len(data["details"])
        location_length = len(data["location"])
        if details_length != location_length:
            raise ValueError(
                f"Mismatch in {severity}: {details_length} details but {location_length} locations"
            )


#Save after identifying Anomalies
def save_anomalies_with_description(ip, anomalies, config):
    anomaly_directory = config.get("anomaly_directory", "anomalies/")
    os.makedirs(anomaly_directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    description = config["ip_descriptions"].get(ip, "Unknown Location")
    filename = f"{anomaly_directory}/anomalies_{ip}_{timestamp}.txt"

    with open(filename, 'w') as file:
        file.write(f"IP: {ip}\nDescription: {description}\n\n")
        for anomaly in anomalies:
            file.write(anomaly + "\n")
    logging.info(f"Anomalies for IP {ip} ({description}) saved to {filename}")


#Send Email after Saving Identified anomalies
    #NEEDS Classification of anomalies for subject line
def send_email_notification(anomalies, recipient_email):
    smtp_server = "smtp.scctv.org"
    sender_email = "utility@scctv.org"
    subject = "Critical Anomalies Detected"
    body = "\n".join(anomalies)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(sender_email, "password")  # Replace with secure credentials
        server.sendmail(sender_email, recipient_email, msg.as_string())

    logging.info("Email notification sent.")


# Function to handle the daily log pull for all configured IPs
def daily_pull(config):
    ip_addresses = config["ip_descriptions"].keys()
    for ip in ip_addresses:
        # Check IP status
        status = config.get("ip_status", {}).get(ip, {}).get("status", "Unknown")
        error_count = config.get("ip_status", {}).get(ip, {}).get("error_count", 0)
        
        # Skip IP if it has persistent failures
        if status == "Failure" and error_count >= 3:
            logging.warning(f"Skipping IP {ip} due to repeated failures.")
            continue
        
        # Fetch logs
        log_data = fetch_log_data(ip, config)
        if log_data:
            save_log(ip, log_data, config)
            
            # Clear anomalies before processing
            for severity in anomalies.keys():
                anomalies[severity]["details"].clear()
                anomalies[severity]["count"] = 0
                anomalies[severity]["location"].clear()
            
            # Detect anomalies
            ip_description = config["ip_descriptions"].get(ip, "Unknown Location")
            detect_and_group_anomalies(log_data, ip_description)
            
            # Validate anomalies (check alignment)
            validate_anomalies()

            # Save anomalies with descriptions
            save_anomalies_with_description(ip, anomalies, config)
            
            # Send email if critical anomalies are detected
            if anomalies["Critical"]["count"] > 0:
                recipient_email = config.get("notification_email", "admin@example.com")
                email_body = generate_anomaly_report()
                send_email_notification(email_body, recipient_email)

            # Log detected anomalies
            logging.info(f"Anomalies detected for {ip}: {anomalies}")




#Generate report
def generate_anomaly_report():
    report = []
    for severity, details in anomalies.items():
        report.append(f"--- {severity.upper()} ---")
        report.append(f"Count: {details['count']}")
        for detail, location in zip(details["details"], details["location"]):
            report.append(f"{detail} (Location: {location})")
        report.append("\n")
    return "\n".join(report)


# Example call
report = generate_anomaly_report()
print(report)


# Main function to execute the process
def main():
    # Load configuration
    config = load_config()

    # Manage IP addresses
    manage_ip_addresses(config)

    # Perform daily log pulling and anomaly detection
    try:
        daily_pull(config)
    except Exception as e:
        logging.error(f"Unexpected error during execution: {e}")
        raise

    # Optional: Print anomaly report to console (or save it)
    report = generate_anomaly_report()
    print(report)

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
