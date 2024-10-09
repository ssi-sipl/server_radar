import serial
import requests
import subprocess
import time
import re

def contains_numeric(data):
    """ Check if the data contains any numeric value. """
    return bool(re.search(r'\d', data))  # Regular expression to find any digit

def execute_rpi_client():
    """ Execute the rpi_client.py script located in the specified folder. """
    try:
        script_path = '/home/panther/Desktop/server_testing/https_server_03/https_server.py'
        subprocess.Popen(['python3', script_path])
        print("rpi_client.py executed.")
    except Exception as e:
        print(f"Error executing rpi_client.py: {e}")

def main():
    # UART setup
    port = '/dev/ttyS0'
    baud_rate = 115200
    server_url = 'http://192.168.1.5:3300'

    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            print(f"Connected to {port} at {baud_rate} baud")

            while True:
                # Read data from UART
                try:
                    uart_data = ser.readline().decode('utf-8').strip()
                    if uart_data:
                        print(f"Received from UART: {uart_data}")

                        # Check for numeric values and execute script if found
                        if contains_numeric(uart_data):
                            print("Numeric value detected. Executing rpi_client.py...")
                            execute_rpi_client()

                        # Send data to HTTP server
                        try:
                            response = requests.post(
                                server_url,
                                data={  "cameraId": "RD001",
                                        "eventTime": 1233232,
                                        "timestampStr": 787878,
                                        "eventType": "Sensor_Event",
                                        "eventTag": "PIR SENSOR"
                                       }
                            )
                            try:
                                print(f"Server response: {response.json()}")
                            except ValueError:
                                print(f"Unexpected response format: {response.text}")
                        except requests.exceptions.RequestException as e:
                            print(f"Error sending data to server: {e}")

                except Exception as e:
                    print(f"Error reading from UART: {e}")

                time.sleep(1)  # Wait for 1 second before reading again

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

if __name__ == "__main__":
    main()
