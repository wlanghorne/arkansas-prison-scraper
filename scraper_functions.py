from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
import datetime
import csv
import os

# Scrapes inmate database for inmates at least or at most the age specified. At most is least_or_most == 2. At least is least_or_most == 3 
def scrape_inmates_of_age (outputs_path, driver_path, url, age):

    # Add header for the first row of data
    headers = ['Name', 'Race', 'Sex', 'DoB', 'Initial Receipt Date', 'Facility', 'PE/TE Date', 'Total Time','Currently sentenced on violent offense','Current prison sentence history', 'Sentences in county' 'Timestamp: ' + str(datetime.datetime.now())]

    with open(outputs_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        f.close()

    # List of violent offenses 
    violent_offenses = ['assault', 'murder', 'manslaughter' 'battery', 'kidnapping', 'aggravated robbery', 'terroristic', 'rape', 'causing a catastrophe', 'aggravated residential burglary', 'homicide', 'false imprisonment', 'endangering the welfare of a minor', 'cruelty to animals', 'harassment']

    # Initiate driver 
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    s = Service(driver_path)
    driver = webdriver.Chrome(service=s, options=chrome_options)
    driver.get(url)

    # Select 'age is at most'
    select_agetype = Select(driver.find_element(By.NAME,'agetype'))
    select_agetype.select_by_value('1')

    # Inmate age is at least 1 
    driver.find_element(By.NAME,'age').send_keys(age)

    # Agree to disclaimer
    disclaim_button = driver.find_element(By.NAME,'disclaimer')
    disclaim_button.click()

    # Submit search 
    submit_button = driver.find_element(By.NAME,'B1')
    submit_button.click()

    # Save the window opener 
    main_window = driver.current_window_handle

    # Set boolean for first and last pages 
    page_last = False

    inmate_counter = 0

    strong = str(driver.find_element(By.CSS_SELECTOR,'strong').get_attribute('innerHTML'))
    strong=strong.replace(" matches", "")
    matches = int(strong)
    matches_on_pg = 50

    print("Matches = " + strong)

    # Iterate through page series 
    while not page_last:

        if matches <=50:
            page_last = True
            matches_on_pg = matches
        else: 
            matches = matches-matches_on_pg

        # Get links on page 
        page_links = get_page_links(driver)

        # Get length of list and create a variable for the number of links to iterate through
        links_len = len(page_links)

        scrape_page(matches_on_pg, page_links[2:], violent_offenses, outputs_path, driver)

        inmate_counter += matches_on_pg
        print(inmate_counter)   

        # If it's not the last page, open the 'next page' link
        if not page_last: 
            driver.get(page_links[links_len-1])
        # If it's the last page, open the 'back to search link'
        else:
            driver.get(page_links[1])

        # Add delay to keep from crashing
        sleep(1)

    # Script ran successfully  
    print('Success! ' + str(datetime.datetime.now()))

# Function checks to see there are elements labeled with given class name. Returns error message and loads last page if not
def error_check(class_name, driver):
    class_container = driver.find_elements(By.CLASS_NAME,class_name)
    # Loop until the page loads correctly and elements with given class name show up
    while not class_container:
            # Close the window
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            # Print error message and sleep
            print('Page not loading properly...')
            sleep(60)

            # Try page again
            driver.execute_script('window.open('');')
            # Switch to the new window and open URL B
            driver.switch_to.window(driver.window_handles[1])
            driver.get(page_links[i])

            class_container = driver.find_elements(By.CLASS_NAME,class_name)

    return (class_container)

# Function gets all links on page 
def get_page_links (driver):
    page_links = []
    elems = driver.find_elements(By.CSS_SELECTOR,'a')
    for elem in elems:
        # remove 'send $' links
        link = elem.get_attribute('href')
        link_txt = str(link)
        if 'bank' not in link_txt:
            page_links.append(link)
    return(page_links)

# Function that scrapes data from current page 
def scrape_page(matches, page_links, violent_offenses, outputs_path, driver):
    # Iterate through links on page
    for i in range(matches):

        # Open a new window
        # Credit: https://paveltashev.medium.com/python-and-selenium-open-focus-and-close-a-new-tab-4cc606b73388
        driver.execute_script('window.open('');')

        # Switch to the new window and open URL B
        driver.switch_to.window(driver.window_handles[1])
        driver.get(page_links[i])

        # Scrape inmate information
        elements = error_check('col-xs-6', driver)

        # Get name, race, sex, DoB, initial receipt date, facility, total time 
        inmate_info =[elements[3].get_attribute('innerHTML'),
                      elements[5].get_attribute('innerHTML'), 
                      elements[7].get_attribute('innerHTML'), 
                      elements[17].get_attribute('innerHTML'), 
                      elements[19].get_attribute('innerHTML'), 
                      elements[21].get_attribute('innerHTML'),
                      elements[31].get_attribute('innerHTML'), 
                      elements[33].get_attribute('innerHTML')]

        # Get offenses
        tds = driver.find_elements(By.CSS_SELECTOR,'td')
        # Chop off column headers
        tds = tds[5:]

        tds_elements  = []
        offenses = []
        county_sentenced = []
        for td in tds:
            tds_elements.append(td.get_attribute('innerHTML'))

        # Iterate through table attributes to extract current offenses
        for i in range(len(tds_elements)):
            # When next attribute is 'Offense' you've reached prior prison sentence history
            if tds_elements[i] == 'Offense':
                break
            # If reached a new row, extract offense and append it to the list
            elif i % 5 == 0:
                offenses.append(tds_elements[i])
            # If reached new county sentenced 
            elif i % 5 == 2:
                county_sentenced.append(tds_elements[i])

        violent_offender = False
      
        # Check if violent offender 
        for offense in offenses: 
            for violent_offense in violent_offenses: 
                if violent_offense in offense.lower():
                    violent_offender = True 
                    break

        inmate_info = inmate_info + [violent_offender] + [offenses] + [county_sentenced]

        # Close tab and switch to main tab 
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # Add delay to keep from crashing 
        sleep(1.3)

        # Write to file  
        with open(outputs_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(inmate_info)
            f.close()


def find_csv_files(path_to_dir, file_type=".csv"):
  file_names = os.listdir(path_to_dir)
  return [file_name for file_name in file_names if file_name.endswith(file_type)]

def cat_outputs (outputs_path, final_path):

    # Get all csvs in the output folder
    csv_paths = find_csv_files(outputs_path)

    # Write headers 
    with open(final_path, 'w', newline='') as f_write:
        writer = csv.writer(f_write)
        with open(os.path.join(outputs_path,csv_paths[0]), 'r', newline='') as f_read:
            reader = csv.reader(f_read)
            writer.writerow(next(reader))
            f_read.close()
        f_write.close()

    # Read data for all ages events 
    for file_path in csv_paths: 
        with open(os.path.join(outputs_path,file_path), 'r', newline='') as f_read:
            reader = csv.reader(f_read)
            next(reader)
            with open(final_path, 'a', newline='') as f_append:
                appender = csv.writer(f_append)
                for row in reader:
                    appender.writerow(row)
                f_append.close()
        f_read.close()