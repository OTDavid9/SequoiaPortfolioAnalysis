from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

options = Options()
options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
options.add_argument("--window-size=4000x100000")  # Set window size to a large value for scraping.

# Initialize the webdriver
driver = webdriver.Chrome(options=options)

try:
    # Load the webpage
    driver.get('https://www.sequoiacap.com/our-companies/#all-panel')

    # Function to wait until page is fully loaded
    def wait_until_page_loaded():
        # Wait for a specific element on the page to indicate loading is complete
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'company-listing__head'))
        )

    # Wait until the page is fully loaded
    wait_until_page_loaded()

    # Print the page content after fully loaded (optional)
    # print(driver.page_source)

    # Function to click the "Load More" button until all data is loaded
    def click_load_more():
        while True:
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'facetwp-load-more'))
                )
                load_more_button.click()
                time.sleep(15)  # Adjust sleep time as necessary
            except Exception as e:
                print(f"No more 'Load More' button found or unable to click: {e}")
                break

    # Click "Load More" until all data is loaded
    click_load_more()

    # Once the page is fully loaded, get the page source and create a BeautifulSoup object
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find the tbody element containing company listings
    tbody = soup.find('tbody', class_='facetwp-template')

    # Initialize an empty list to store company data
    company_data = []

    # Iterate over each company row (tr)
    for row in tbody.find_all('tr', class_='aos-init aos-animate'):
        company_name = row.find('th', class_='company-listing__head').get_text(strip=True)
        short_description = row.find('td', class_='company-listing__text').get_text(strip=True)
        current_stage = row.find('td', class_='u-lg-hide').get_text(strip=True)
        partners = ', '.join([li.get_text(strip=True) for li in row.find('td', class_='u-lg-hide company-listing__list').find_all('li')])
        first_partnered = row.find('td', class_='u-xl-hide').get_text(strip=True)

        # Create a dictionary for the company and append to company_data list
        company_dict = {
            "Company Name": company_name,
            "Short Description": short_description,
            "Current Stage": current_stage,
            "Partners": partners,
            "First Partnered": first_partnered
        }
        company_data.append(company_dict)

    # Create a pandas DataFrame from the list of dictionaries
    df = pd.DataFrame(company_data)

    # Save the DataFrame to a CSV file
    csv_filename = 'sequoia_companies.csv'
    df.to_csv(csv_filename, index=False)

    print(f"CSV file '{csv_filename}' has been saved successfully.")

finally:
    # Quit the driver
    driver.quit()
