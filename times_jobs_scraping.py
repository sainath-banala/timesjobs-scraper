from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import sys

try:
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
    else:
        search_term = "Python Developer"
    job_postings = []
    chrome_options = Options()
    # stopping the flashing of terminal running chromedriver.exe
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])

    # passing the chromedriver executable path
    service = Service(r"C:\Users\TEST\External_downloaded_Executables\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.execute_cdp_cmd('Network.setUserAgentOverride', 
                        {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    ### going to the timesjobs website and clicking on the search box
    driver.get("https://m.timesjobs.com/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtKeywords')))
    search_element = driver.find_element(By.ID, "txtKeywords")
    search_element.send_keys(Keys.ENTER)

    ### entering the text in the skills section
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'skillSet')))
    skill_set_input_element = driver.find_element(By.ID, 'skillSet')
    skill_set_input_element.clear()
    skill_set_input_element.send_keys(search_term)

    ### clicking on submit button
    submit_button_element = driver.find_element(By.ID, 'submitBtn')
    submit_button_element.click()

    ### After the button clicked, waiting for 2 seconds to load the page
    time.sleep(2)

    ### Scroll down a few times to load more jobs (not all)
    for i in range(15):  # scrolling 15 times
        # Scroll a fixed amount (in pixels)
        driver.execute_script("window.scrollBy(0, 1000);")  # Scroll down 1000px
        time.sleep(1)

    ### getting the count of jobs available
    jobs_count_element = driver.find_element(By.ID, 'totalJobsCount').text.split(" ")[0]
    print(f"Total jobs available for {search_term} skill or role: {jobs_count_element}")

    ### getting the unordered list with ID, and iterating through the list of elements in it
    jobs_list_element = driver.find_element(By.ID, 'jobsListULid')

    jobs = jobs_list_element.find_elements(By.TAG_NAME, 'li')
    ### Raising an exception if no jobs found for that specific word:
    if len(jobs) == 0:
        raise Exception(f"No jobs found with the {search_term} role or skill")
    print(f"no of jobs in the list: {len(jobs)}")
    # fetching job details for each job
    for job in jobs:
        ### check whether that is, job element or space used for advertisement 
        try:
            job_element = job.find_element(By.CLASS_NAME, 'srp-job-bx')
        except NoSuchElementException:
            print("skipping the list element as it was not having job element")
            continue

        job_details = {}
        job_url_and_role_heading = job.find_element(By.CLASS_NAME, "srp-job-heading")
        job_details["role"] = job_url_and_role_heading.find_element(By.TAG_NAME, "h3").text
        job_details["job_url"] = job_url_and_role_heading.find_element(By.TAG_NAME, "a").get_attribute("href")
        job_details["company_name"] = job.find_element(By.CLASS_NAME, "srp-comp-name").text
        job_details["posting_time"] = job.find_element(By.CLASS_NAME, "posting-time").text
        job_details["skills"] = job.find_element(By.CLASS_NAME, "srp-keyskills").text.replace(" ", ", ")
        job_details["location"] = job.find_element(By.CLASS_NAME, "srp-loc").text
        job_details["experience"] = job.find_element(By.CLASS_NAME, "srp-exp").text
        job_details["salary"] = job.find_element(By.CLASS_NAME, "srp-sal").text

        job_postings.append(job_details)

    df = pd.DataFrame(job_postings)
    
    df['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output_filename = f'timesjobs_python_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    df.to_excel(output_filename, index=False, engine='openpyxl')
    print(f"\n SUCCESS! Data exported to: {output_filename}")
    print(f"Total jobs scraped: {len(df)}")

except Exception as e: 
    print(f"Error occurred: {e}")

finally:
    driver.quit()
    print("closed the driver")