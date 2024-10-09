import serial
import requests
import subprocess
import time
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='uart_server_communication.log',
                    filemode='a')

logger = logging.getLogger(__name__)

def contains_numeric(data):
    """ Check if the data contains any numeric value. """
    return bool(re.search(r'\d', data))  # Regular expression to find any digit

def execute_rpi_client():
    """ Execute the rpi_client.py script located in the specified folder. """
    try:
        script_path = '/home/panther/Desktop/server_testing/https_server_03/https_server.py'
        subprocess.Popen(['python3', script_path])
        logger.info("rpi_client.py executed.")
    except Exception as e:
        logger.error(f"Error executing rpi_client.py: {e}")

def main():
    # UART setup
    port = '/dev/ttyS0'
    baud_rate = 115200
    server_url = 'http://192.168.1.5:3300'

    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            logger.info(f"Connected to {port} at {baud_rate} baud")

            while True:
                # Read data from UART
                try:
                    uart_data = ser.readline().decode('utf-8').strip()
                    if uart_data:
                        logger.info(f"Received from UART: {uart_data}")

                        # Check for numeric values and execute script if found
                        if contains_numeric(uart_data):
                            logger.info("Numeric value detected. Executing rpi_client.py...")
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
                                logger.info(f"Server response: {response.json()}")
                            except ValueError:
                                logger.warning(f"Unexpected response format: {response.text}")
                        except requests.exceptions.RequestException as e:
                            logger.error(f"Error sending data to server: {e}")

                except Exception as e:
                    logger.error(f"Error reading from UART: {e}")

                # Wait for 3 seconds before reading again
                time.sleep(3)

    except serial.SerialException as e:
        logger.error(f"Error opening serial port: {e}")

if __name__ == "__main__":
    main()
