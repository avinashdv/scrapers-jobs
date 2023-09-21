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


with open('GooglePostings.csv', 'w', newline='\n', encoding="utf-8") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["created_at", "course_type", "company_name", "job_link", "role_name",
                       "job_location", "experience", "Platform", "skills", "description", "Job_Activity", "role_relevancy", 'salary', 'phone_number', 'Email_id'])

    options = webdriver.ChromeOptions()
    s = Service(
        "C:/Users/91868/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=s,
                              options=options)

    roles = pd.read_csv(
        r"E:/The Office/scrappers/Google/roles.txt", sep=",", header=None)[0].tolist()
    job_link_elements = []
    for role in roles:
        driver.get(f'https://www.google.com/search?q={role} Jobs')
        time.sleep(4)

        try:
            driver.find_element(By.TAG_NAME, 'g-tray-header').click()
            time.sleep(4)
            location = 'htilrad=-1.0'  # location anywhere
            duration = 'htischips=date_posted;today'  # past day
            type = 'employment_type;FULLTIME'  # Full Time
            filters = f'&{location}&{duration},{type}'
            url = driver.current_url

            redirect_url = f'{url}{filters}'

            driver.get(redirect_url)
            time.sleep(2)

            arg_one = driver.find_element(
                By.XPATH, '//div[@id="immersive_desktop_root"]/div/div[3]/div')

            arg_two = driver.find_element(
                By.XPATH, '//div[@id="immersive_desktop_root"]/div/div[3]/div/div')

            last_height = 0
            while True:
                new_height = driver.execute_script(
                    'return arguments[0].scrollTop = arguments[0].scrollTop + arguments[1].offsetHeight;', arg_one, arg_two)
                if new_height == last_height:
                    break
                last_height = new_height
                time.sleep(2)

            try:
                job_link_elements = driver.find_elements(
                    By.CLASS_NAME, 'gws-plugins-horizon-jobs__li-ed')

                for job_link_el in job_link_elements:
                    ActionChains(driver).move_to_element(
                        job_link_el).click(job_link_el).perform()

                    job_link_el.click()
                    time.sleep(2)

                    job_details_parent = driver.find_element(
                        By.XPATH, '//div[@id="tl_ditsc"]/div/div/div/div')

                    job_link = driver.current_url

                    role_name = str(job_details_parent.find_element(
                        By.TAG_NAME, 'h2').text)

                    company_name = str(job_details_parent.find_element(
                        By.XPATH, './div/div/div[2]/div[2]/div').text)

                    job_location = str(job_details_parent.find_element(
                        By.XPATH, './div/div/div[2]/div[2]/div[2]').text)

                    detail_one = ''
                    detail_two = ''
                    if (len(job_details_parent.find_elements(
                            By.XPATH, './div[3]'))):
                        if (len(job_details_parent.find_elements(
                                By.XPATH, './div[3]/div'))):
                            detail_one = job_details_parent.find_element(
                                By.XPATH, './div[3]/div/span[2]').text
                        if (len(job_details_parent.find_elements(
                                By.XPATH, './div[3]/div[2]'))):
                            detail_two = job_details_parent.find_element(
                                By.XPATH, './div[3]/div[2]/span[2]').text

                    job_activity = ''
                    job_salary = ''

                    if ("ago" in detail_one):
                        job_activity = detail_one
                    elif ("₹" in detail_one):
                        job_salary = detail_one

                    if ("ago" in detail_two):
                        job_activity = detail_two
                    elif ("₹" in detail_two):
                        job_salary = detail_two

                    job_desc = ''

                    if (len(job_details_parent.find_elements(
                            By.XPATH, './div[4]/span'))):
                        job_desc = str(job_details_parent.find_element(
                            By.XPATH, './div[4]/span').text)
                    elif (len(job_details_parent.find_elements(
                            By.XPATH, './div[4]/div/span'))):
                        job_desc_one = str(job_details_parent.find_element(
                            By.XPATH, './div[4]/div/span').text)
                        job_desc_two = str(job_details_parent.find_element(
                            By.XPATH, './div[4]/div/span/span[2]').text)
                        job_desc = job_desc_one + job_desc_two

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
                    date
                    platform = 'Google Jobs'
                    course_type = "web development"
                    exp_req = ''
                    job_skills = ''

                    relevancy = get_relevancy(role_name)
                    csvwriter.writerow([today, course_type, company_name, job_link, role_name, job_location,
                                        exp_req, platform, job_skills, job_desc, job_activity, relevancy, job_salary, phone_num, email_id])
            except:
                continue
        except:
            continue
