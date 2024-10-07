import machine
import time
import urequests
import network
import random

# Wi-Fi configuration
SSID = "Wokwi-Guest"
PASSWORD = "-"

# ThingSpeak configuration
thingspeak_api_key = "0IXVESNSNEK5VFC3"
thingspeak_channel_id = "2684344"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

# Wait for the Wi-Fi connection to be established
while not wifi.isconnected():
    pass

print("Connected to Wi-Fi")

potentiometer_1_pin = machine.ADC(26)  # Analog pin for potentiometer 1 (heart rate)
potentiometer_2_pin = machine.ADC(27)  # Analog pin for potentiometer 2 (respiratory rate)
temperature_sensor_pin = machine.ADC(28)  # Analog pin for the NTC temperature sensor

# LED pins
led1_pin = machine.Pin(4, machine.Pin.OUT)  # GP4 - Heart rate
led2_pin = machine.Pin(5, machine.Pin.OUT)  # GP5 - Respiratory rate
led3_pin = machine.Pin(3, machine.Pin.OUT)  # GP3 - Temperature

# Moving Average Filter Parameters
filter_length = 5
heart_rate_history = []
respiratory_rate_history = []
temperature_history = []

# Flags for abnormal conditions
heart_rate_abnormal = False
respiratory_rate_abnormal = False
temperature_abnormal = False

# Function to apply moving average filter
def moving_average(data_history, new_value, filter_length):
    data_history.append(new_value)
    if len(data_history) > filter_length:
        data_history.pop(0)
    return sum(data_history) / len(data_history)

# Function to convert ADC value to temperature (randomize after every 5 times)
def convert_to_temperature(adc_value, reading_count):
 
    temperature = random.uniform(3.8, 60.2)

    return temperature

reading_count = 0  # Counter for the number of readings

while True:
    # Read normal values from potentiometers and temperature sensor
    potentiometer_1_value, potentiometer_2_value, temperature_sensor_value = potentiometer_1_pin.read_u16(), potentiometer_2_pin.read_u16(), temperature_sensor_pin.read_u16()

    # Apply variations to normal values
    heart_rate = (potentiometer_1_value / 65535) * 60 + 60  # Adjust the formula based on your sensor characteristics
    respiratory_rate = (potentiometer_2_value / 65535) * 10 + 10  # Adjust the formula based on your sensor characteristics
    temperature = convert_to_temperature(temperature_sensor_value, reading_count)  # Convert NTC temperature sensor value to temperature

    # Increment the reading count
    reading_count += 1

    # Check for abnormal conditions and blink LEDs accordingly
    if heart_rate > 110:
        heart_rate_abnormal = True
    elif heart_rate < 65:
        heart_rate_abnormal = True
    else:
        heart_rate_abnormal = False

    if respiratory_rate < 12:
        respiratory_rate_abnormal = True
    elif respiratory_rate > 18:
        respiratory_rate_abnormal = True
    else:
        respiratory_rate_abnormal = False

    if temperature > 38:
        temperature_abnormal = True
    elif temperature < 35:
        temperature_abnormal = True
    else:
        temperature_abnormal = False

    # Blink LEDs for abnormal conditions
    if heart_rate_abnormal:
        led1_pin.on()
    else:
        led1_pin.off()

    if respiratory_rate_abnormal:
        led2_pin.on()
    else:
        led2_pin.off()

    if temperature_abnormal:
        led3_pin.on()
    else:
        led3_pin.off()

    # Send data to ThingSpeak
    url = "https://api.thingspeak.com/update?api_key={}&field1={}&field2={}&field3={}".format(thingspeak_api_key, heart_rate, respiratory_rate, temperature)
    response = urequests.post(url)
    #print("ThingSpeak Response:", response.text)
    response.close()

    # Print readings to the serial monitor
    # print("Heart Rate:", int(heart_rate), "bpm")
    # print("Respiratory Rate:", int(respiratory_rate), "breaths per minute")
    # print("Temperature:", int(temperature), "degrees Celsius")

      # Print sensor data to console
    print(f"Heart Rate: {int(heart_rate)} bpm")
    print(f"Respiratory Rate: {int(respiratory_rate)} breaths/min")
    print(f"Temperature: {int(temperature)} °C")

    time.sleep(4)  # Send readings to ThingSpeak every 30 seconds
