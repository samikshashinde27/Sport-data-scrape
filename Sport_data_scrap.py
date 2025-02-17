# Import necessary libraries
from selenium import webdriver  # Selenium for web scraping
from datetime import date, datetime, timedelta  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.common.by import By  
import re  
import json  
import logging  

# Set up logging configuration for the script to track events
logging.basicConfig(level=logging.INFO,  # Set the level of logging (INFO, DEBUG, etc.)
                    format='%(asctime)s - %(levelname)s - %(message)s',  
                    handlers=[logging.StreamHandler()])  

import time  

# Initialize the WebDriver for Chrome browser
driver = webdriver.Chrome()

# Function to extract and save information from the tender element
def extract_and_save_notice(tender_html_element):
    global data  # Use global data to append results

    # Try to extract title from the element
    try:
        title = tender_html_element.find_element(By.CSS_SELECTOR, 'div > p:nth-child(1)').text
    except Exception as e:
        logging.info("Exception in title: {}".format(type(e).__name__))  
        pass

    # Try to extract and format the date and time
    try:
        # Extract date and time using regex to match patterns like "Feb 18 • 7:00 PM"
        dates = tender_html_element.find_element(By.CSS_SELECTOR, 'div > p:nth-child(2)').text
        dates = re.findall(r'\w+ \d{1,2} • \d{1,2}:\d{2} [APM]+', dates)[-1].strip()
        year = str(date.today().year)  # Get the current year
        dates = f"{dates} {year}"  # Add the year to the date string
        date_time = datetime.strptime(dates, '%b %d • %I:%M %p %Y').strftime('%Y/%m/%d %H:%M:%S')  # Convert to desired format
        logging.info(date_time)
    except Exception as e:
        logging.info("Exception in date_time: {}".format(type(e).__name__))
        pass

    # Try to extract location from the element
    try:
        location = tender_html_element.find_element(By.CSS_SELECTOR, 'div > p:nth-child(3)').text
    except Exception as e:
        logging.info("Exception in location: {}".format(type(e).__name__))
        pass

    # Try to extract link (URL) from the element
    try:
        link = tender_html_element.get_attribute('href')
    except Exception as e:
        logging.info("Exception in link: {}".format(type(e).__name__))
        pass

    logging.info('----------------------------------------')

    # Append the extracted information into the global data list
    data.append({
        'title': title,
        'date_time': date_time,
        'location': location,
        'link': link
    })

# Main script starts here
try:
    # Define the list of URLs to scrape
    urls = ['https://www.stubhub.com/explore?lat=MjUuNDQ3ODg5OA%3D%3D&lon=LTgwLjQ3OTIyMzY5OTk5OTk5&to=253402300799999&tlcId=2'] 
    for url in urls:
        driver.get(url)  # Open each URL in the browser
        logging.info('----------------------------------')  
        logging.info(url)
        
        # Wait for the "Show More" button to appear and then scroll into view
        scroll_down = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(),"Show More")]')))
        driver.execute_script("arguments[0].scrollIntoView(true);", scroll_down)
        time.sleep(3)  
        
        # Click on the "Show More" button to load additional content
        show_more_click = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Show More")]')))
        driver.execute_script("arguments[0].click();", show_more_click)
        time.sleep(5) 
        
        # Wait for the list of event rows to be loaded
        rows = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.XPATH, '(//p[text()="Explore events near Florida City"])[1]/following::ul[1]/li//a')))
        length = len(rows)  
        logging.info(length) 

        # Initialize an empty list to store the scraped data
        data = []

        # Loop through each event element and extract the necessary data
        for records in range(0, length):
            tender_html_element = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.XPATH, '(//p[text()="Explore events near Florida City"])[1]/following::ul[1]/li//a')))[records]
            extract_and_save_notice(tender_html_element)  # Extract and save the data

except Exception as e:
    raise e
    logging.info("Exception:" + str(e))  
finally:
    driver.quit()

# Save the scraped data to a JSON file
with open('scraped_data.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)  # Write data to JSON file with indentation for readability
