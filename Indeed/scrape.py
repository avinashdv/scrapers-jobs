from selenium.webdriver.common.action_chains import ActionChains
from cmath import e
from selenium.webdriver.support.ui import WebDriverWait
from tkinter import E
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import date
from selenium.webdriver.chrome.service import Service
from re import match
import pandas as pd
from word2number import w2n
import time
import csv
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import openai


def get_relevancy(role_name):
    openai.api_key = "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"
    result = f'''Analyze the Job details given below delimited by triple quotes and compare it with Requirements delimited by triple angle brackets 
                Answer me in YES, NO, and MAYBE (No Explanation) based on following conditions
                If all points match then YES
                If only 1st and 2nd point matches then MAYBE
                If no point matches then NO

            Requirements: <<<
            Job Roles: Front End Developer/Engineer, Back End Developer/Engineer, Software Engineer/Engineer, Java Developer/Engineer, and UI Developer/Engineer.
            >>>

            Job details:""" Job Role: {role_name}
                        """
            '''

    msg = [{"role": "user", "content": result}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=msg,
        temperature=0.6,
    )
    return response.choices[0].message.content


with open('IndeedPostings.csv', 'w', newline='\n', encoding="utf-8") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["created_at", "course_type", "company_name", "job_link", "role_name",
                       "job_location", "experience", "Platform", "skills", "description", "Job_Activity", "role_relevancy" 'salary', 'phone_number', 'Email_id'])

    options = webdriver.ChromeOptions()
    s = Service(
        "C:/Users/91868/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=s,
                              options=options)

    roles = pd.read_csv(
        r"E:/The Office/scrappers/Indeed/roles.txt", sep=",", header=None)[0].tolist()
    job_links = []
    for role in roles:
        driver.get('https://in.indeed.com/')
        time.sleep(2)

        title = driver.find_element(By.ID, 'text-input-what')
        title.clear()
        time.sleep(1)
        title.send_keys(role)

        location = driver.find_element(By.ID, 'text-input-where')
        location.send_keys(Keys.CONTROL + "a")
        location.send_keys('India')

        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(2)

        duration = 'fromage=1'  # Past Day
        type = 'sc=0kf%3Ajt(fulltime)%3B'  # Full Time
        filters = f'&{duration}&{type}'
        url = driver.current_url

        redirect_url = f'{url}{filters}'

        i = 0
        count = 10
        next_page = 1
        initiate_url = ''
        while next_page:
            if (i <= 0):
                initiate_url = redirect_url
            else:
                initiate_url = f'{redirect_url}&start={count}'

            driver.get(initiate_url)
            time.sleep(2)

            if (len(driver.find_elements(By.CSS_SELECTOR, 'h3.DesktopJobAlertPopup-heading'))):
                close_element = driver.find_element(
                    By.XPATH, '//h3[@class="DesktopJobAlertPopup-heading"]/following-sibling::button')
                close_element.click()

            next_page = len(driver.find_elements(
                By.XPATH, '//a[@data-testid="pagination-page-next"]'))

            all_job_elements = driver.find_elements(
                By.XPATH, '//div[@id="mosaic-provider-jobcards"]/ul/*')

            try:
                for job_ele in all_job_elements:
                    if (len(job_ele.find_elements(By.TAG_NAME, 'a'))):
                        ActionChains(driver).move_to_element(
                            job_ele).click(job_ele).perform()
                        time.sleep(3)

                        job_exp = ''

                        job_link = initiate_url

                        job_activity = str(job_ele.find_element(
                            By.CSS_SELECTOR, 'span.date').text)

                        job_role_string = str(driver.find_element(By.CSS_SELECTOR,
                                                                  'h2.jobsearch-JobInfoHeader-title').text)

                        job_role = ''.join(
                            job_role_string.splitlines()).replace('- job post', '')

                        company_name = str(driver.find_element(
                            By.XPATH, '//div[@data-testid="inlineHeader-companyName"]').text)

                        job_location = str(driver.find_element(
                            By.XPATH, '//div[@data-testid="inlineHeader-companyLocation"]').text)

                        job_salary = ''
                        if (len(driver.find_elements(
                                By.ID, 'salaryInfoAndJobType'))):
                            job_salary = str(driver.find_element(
                                By.ID, 'salaryInfoAndJobType').text)

                        job_desc = str(driver.find_element(
                            By.ID, 'jobDescriptionText').text)

                        match3 = re.search(
                            r'[1-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', job_desc)

                        if match3:
                            phone_num = match3.group()
                        else:
                            match3 = re.search(
                                r'[1-9][0-9][0-9]([ ]|[-])[0-9][0-9][0-9]([-]|[ ])[0-9][0-9][0-9][0-9]', job_desc)
                            if match3:
                                phone_num = match3.group()
                            else:
                                phone_num = ""
                        match4 = re.search(
                            r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', job_desc.lower())
                        if match4:
                            email_id = match4.group()
                        else:
                            email_id = ""
                        today = date.today()
                        platform = 'Indeed Jobs'
                        course_type = "web development"
                        job_skills = ''

                        relevancy = get_relevancy(job_role)

                        csvwriter.writerow([today, course_type, company_name, job_link, job_role, job_location,
                                            job_exp, platform, job_skills, job_desc, job_activity, relevancy, job_salary, phone_num, email_id])
                count = count+10
                i = i + 1
            except:
                continue
