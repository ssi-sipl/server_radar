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

def check_and_execute(data):
    """ Check if the data is greater than '100' and execute rpi_client if true. """
    try:
        # Extract numeric value from the data
        numeric_value = re.search(r'\d+', data)
        if numeric_value:
            value = int(numeric_value.group())
            if value > 100:
                logger.info(f"Value {value} is greater than 100. Executing rpi_client.py...")
                execute_rpi_client()
            else:
                logger.info(f"Value {value} is not greater than 100.")
        else:
            logger.info("No numeric value found in the data.")
    except ValueError as e:
        logger.error(f"Error converting data to integer: {e}")

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

                        # Check if data is greater than 100 and execute script if true
                        check_and_execute(uart_data)

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
