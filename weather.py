# This little program is for the Waveshare 7.5
# inch Version 2 black and white only epaper display
# It uses OpenWeatherMap API to display weather info

import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font')

# Search lib folder for display driver modules
sys.path.append('lib')
from waveshare_epd import epd7in5_V2
epd = epd7in5_V2.EPD()

from datetime import datetime
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

import requests, json
from io import BytesIO

# define funciton for writing image and sleeping for 5 min.
def write_to_screen(image, sleep_seconds):
    print('Writing to screen.')
    # Write to screen
    h_image = Image.new('1', (epd.width, epd.height), 255)
    # Open the template
    screen_output_file = Image.open(os.path.join(picdir, image))
    # Initialize the drawing context with template as background
    h_image.paste(screen_output_file, (0, 0))
    epd.display(epd.getbuffer(h_image))
    # Sleep
    print('Sleeping for ' + str(sleep_seconds) +'.')
    time.sleep(sleep_seconds)

# Set the fonts
font22 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 22)
font30 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 30)
font50 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 50)
font100 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 100)
font150 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 150)
# Set the colors
black = 'rgb(0,0,0)'
white = 'rgb(255,255,255)'
grey = 'rgb(235,235,235)'

# Initiate and clear screen
epd.init()
epd.Clear()

API_KEY = '*****KEY HERE******'
LOCATION = '******Name of Location*****'
LATITUDE = '******'
LONGITUDE = '*********'
UNITS = 'imperial'
BASE_URL = 'http://api.openweathermap.org/data/2.5/onecall?' 
URL = BASE_URL + 'lat=' + LATITUDE + '&lon=' + LONGITUDE + '&units=' + UNITS +'&appid=' + API_KEY

while True:
    # HTTP request
    response = requests.get(URL)
    # check status of code of request
    
    error = None
    while error == None:
        if response.status_code == 200:
            print('Connection to Open Weather successful')
            # get data in jason format
            data = response.json()
            
            # get current dict block
            current = data['current']
            # get current
            temp_current = current['temp']
            # get feels like
            feels_like = current['feels_like']
            # get humidity
            humidity = current['humidity']
            # get pressure
            wind_speed = current['wind_speed']
            # get description
            weather = current['weather']
            report = weather[0]['description']
            # get icon url
            icon_code = weather[0]['icon']
            icon_URL = 'http://openweathermap.org/img/wn/'+ icon_code +'@4x.png'
            
            # get daily dict block
            daily = data['daily']
            # get daily precip
            daily_precip_float = daily[0]['pop']
            #format daily precip
            daily_precip_percent = daily_precip_float * 100
            # get min and max temp
            daily_temp = daily[0]['temp']
            temp_max = daily_temp['max']
            temp_min = daily_temp['min']
            
            # Set strings to be printed
            string_location = LOCATION
            string_temp_current = format(temp_current, '.0f') + u'\N{DEGREE SIGN}F'
            string_feels_like = 'Feels like: ' + format(feels_like, '.0f') +  u'\N{DEGREE SIGN}F'
            string_humidity = 'Humidity: ' + str(humidity) + '%'
            string_wind_speed = 'Wind Speed ' + format(wind_speed, '.1f') + ' MPH'
            string_report = 'Now: ' + report.title()
            string_temp_max = 'High: ' + format(temp_max, '>.0f') + u'\N{DEGREE SIGN}F'
            string_temp_min = 'Low:  ' + format(temp_min, '>.0f') + u'\N{DEGREE SIGN}F'
            string_precip_percent = 'Precip: ' + str(format(daily_precip_percent, '.0f'))  + '%'
            
            # Set error code to false
            error = False
            
            '''
            print('Location:', LOCATION)
            print('Temperature:', format(temp_current, '.0f'), u'\N{DEGREE SIGN}F') 
            print('Feels Like:', format(feels_like, '.0f'), 'F') 
            print('Humidity:', humidity)
            print('Wind Speed:', format(wind_speed, '.1f'), 'MPH')
            print('Report:', report.title())
            
            print('High:', format(temp_max, '.0f'), 'F')
            print('Low:', format(temp_min, '.0f'), 'F')
            print('Probabilty of Precipitation: ' + str(format(daily_precip_percent, '.0f'))  + '%')
            '''    
        else:
            # Display an error
            print('Error in the HTTP request.')
            # Initialize drawing
            error_image = Image.new('1', (epd.width, epd.height), 255)
            # Initialize the drawing
            draw = ImageDraw.Draw(error_image)
            draw.text((100, 150), 'CONNECTION ERROR', font=font50, fill=black)
            draw.text((100, 300), 'Retrying in 5 seconds', font=font22, fill=black)
            current_time = datetime.now().strftime('%H:%M')
            draw.text((300, 365), 'Last Refresh: ' + str(current_time), font = font50, fill=black)
            # Save the error image
            error_image_file = 'error.png'
            error_image.save(os.path.join(picdir, error_image_file))
            # Close error image
            error_image.close()
            # Write error to screen 
            write_to_screen(error_image_file, 30)

    # Open template file
    template = Image.open(os.path.join(picdir, 'template.png'))
    # Initialize the drawing context with template as background
    draw = ImageDraw.Draw(template)
    
    # Draw top left box
    ## First thing is to place the icon image
    ### Place a grey rectangle
    draw.rectangle((25, 25, 225, 180), outline=black)
    ### Place the image
    response = requests.get(icon_URL)
    icon_image = Image.open(BytesIO(response.content))
    template.paste(icon_image, (23, 3), mask=icon_image)
    # Next is drawing the text
    draw.text((30, 195), string_report, font=font22, fill=black)
    draw.text((30, 230), string_precip_percent, font=font30, fill=black)
    # Draw top right box
    draw.text((375, 35), string_temp_current, font=font150, fill=black)
    draw.text((350, 200), string_feels_like, font=font50, fill=black)
    # Draw bottom left box
    draw.text((35, 305), string_temp_max, font=font50, fill=black)
    draw.rectangle((170, 365, 265, 367), fill=black)
    draw.text((35, 370), string_temp_min, font=font50, fill=black)
    # Draw bottom right box
    draw.text((340, 325), string_humidity, font=font22, fill=black)
    draw.text((340, 380), string_wind_speed, font=font22, fill=black)
    # Draw bottom right box
    draw.text((635, 320), 'UPDATED', font=font30, fill=white)
    current_time = datetime.now().strftime('%H:%M')
    draw.text((636, 365), current_time, font = font50, fill=white)

    ## Add a reminder to take out trash on Mon and Thurs
    weekday = datetime.today().weekday()
    if weekday == 0 or weekday == 3:
        draw.rectangle((345, 13, 705, 55), fill =black)
        draw.text((355, 15), 'TAKE OUT TRASH TODAY!', font=font30, fill=white)
        
    # Save the image for display as PNG
    screen_output_file = os.path.join(picdir, 'screen_output.png')
    template.save(screen_output_file)
    # Close the template file
    template.close()
    
    # Write to screen
    write_to_screen(screen_output_file, 300)