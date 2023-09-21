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


def get_relevancy(role_name, job_skills, job_exp):
    openai.api_key = "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"
    result = f'''Analyze the Job details given below delimited by triple quotes and compare it with Requirements delimited by triple angle brackets 
                Answer me in YES, NO, and MAYBE (No Explanation) based on following conditions
                If all points match then YES
                If only 1st and 2nd point matches then MAYBE
                If no point matches then NO

            Requirements: <<<
            1. Job Roles: Front End Developer/Engineer, Back End Developer/Engineer, Software Engineer/Engineer, Java Developer/Engineer, and UI Developer/Engineer. 
            2. Tech Stack: HTML, CSS (Tailwind), Java/JavaScript, ReactJs, Google Sheets, Excel, SQL, Spring, and Springboot.
            3. Experience: Relevant Jobs is (0-1 Year, 0-2, 0-3, 0-4, 1-2, 1-3, 1-4, 1-5, 2-1, 2-2, 2-3, 2-4, 2-5, 2-6)
            4. Type: Full Time
            >>>

            Job details:""" 1, Job Role: {role_name}
                            2, Tech Stack: {job_skills}
                            3, Experience Requirement: {job_exp}
                        """
            '''

    msg = [{"role": "user", "content": result}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=msg,
        temperature=0.6,
    )
    return response.choices[0].message.content


with open('NaukriPostings.csv', 'w', newline='\n', encoding="utf-8") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["created_at", "course_type", "company_name", "job_link", "role_name",
                       "job_location", "experience", "Platform", "skills", "description", "Job_Activity", 'role_relevancy', 'salary', 'phone_number', 'Email_id'])

    options = webdriver.ChromeOptions()
    s = Service(
        "C:/Users/91868/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")

    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=s,
                              options=options)

    roles = pd.read_csv(
        r"E:/The Office/scrappers/Naukri/roles.txt", sep=",", header=None)[0].tolist()

    job_link_elements = []
    job_age = 1
    location = 'india'

    for role in roles:
        x = str(role).lower().split(' ')
        y = '-'.join(x)
        job_path = y+'-jobs-in-india'

        url = f'https://www.naukri.com/{job_path}?k={role}&jobAge={job_age}'

        no_next_page = 0
        i = 0
        page = 1
        job_links = []
        initiate_url = ''

        while not no_next_page:
            if (i <= 0):
                initiate_url = url
            else:
                job_path = y+f'-jobs-in-india-{page}'
                page_url = f'https://www.naukri.com/{job_path}?k={role}&jobAge={job_age}'
                initiate_url = page_url

            try:
                driver.get(initiate_url)
                time.sleep(4)

                next_page_element = driver.find_element(
                    By.CLASS_NAME, 'pagination').find_element(By.XPATH, './a[2]')

                no_next_page = next_page_element.get_attribute('disabled')

                parent_element = driver.find_element(By.CLASS_NAME, 'list')

                all_children = parent_element.find_elements(
                    By.TAG_NAME, 'article')

                for child in all_children:
                    job_link = child.find_element(
                        By.CSS_SELECTOR, 'a.title').get_attribute('href')
                    job_links.append(job_link)
                page = page + 1
                i = i+1
            except:
                continue

        for job_link in job_links:
            driver.get(job_link)
            time.sleep(2)
            try:
                role_name = ''
                company_name = ''
                exp_req = ''
                job_location = ''
                job_activity = ''
                job_salary = ''
                job_desc = ''
                job_skills = ''

                if (len(driver.find_elements(By.CLASS_NAME, 'jdContainer'))):
                    parent_element = driver.find_element(
                        By.CLASS_NAME, 'jdContainer')
                    role_name = str(driver.find_element(
                        By.CSS_SELECTOR, 'h1.av-special-heading-tag').text)
                    company_parent_name = parent_element.find_element(
                        By.CSS_SELECTOR, 'section.getCompanyProfile')
                    company_name = str(company_parent_name.find_element(By.XPATH,
                                                                        './div[2]/p').text)
                    exp_req = str(parent_element.find_element(
                        By.CLASS_NAME, 'getExperience').get_attribute('innerText'))
                    job_location = str(driver.find_element(
                        By.CLASS_NAME, 'getCityLinks').get_attribute('innerText'))
                    job_salary = str(driver.find_element(
                        By.CLASS_NAME, 'getSalaryRange').get_attribute('innerText'))
                    job_activity = str(driver.find_element(
                        By.CLASS_NAME, 'sumFoot').find_element(By.XPATH, './span[1]/strong').text)
                    job_desc = str(driver.find_element(
                        By.CLASS_NAME, 'getJobDescription').find_element(By.XPATH, './div/div[2]').get_attribute('innerText'))

                    job_skills_element = driver.find_element(
                        By.CLASS_NAME, 'getJobKeySkillsSection')

                    if (len(job_skills_element.find_elements(
                        By.XPATH, './div[2]/*')) and len(job_skills_element.find_elements(
                            By.XPATH, './div[3]/*'))):
                        skilly_one = job_skills_element.find_elements(
                            By.XPATH, './div[2]/*')

                        skilly_two = job_skills_element.find_elements(
                            By.XPATH, './div[3]/*')

                        skills_one = []
                        skills_two = []

                        for el in skilly_one:
                            skill_one = el.get_attribute('innerText')
                            skills_one.append(skill_one)

                        for el in skilly_two:
                            skill_two = el.get_attribute('innerText')
                            skills_two.append(skill_two)

                        all_skills = skills_one + skills_two
                        job_skills = ' '.join(all_skills)

                elif (len(driver.find_elements(By.ID, 'jdDiv'))):
                    parent_el = driver.find_element(By.ID, 'jdDiv')
                    role_name = str(parent_el.find_element(
                        By.XPATH, './div/div/h1').text)

                    company_name = str(driver.find_element(By.CLASS_NAME, 'jobCompanyProfileHeading').find_element(
                        By.XPATH, '../following-sibling::div[1]').text)

                    exp_req = str(parent_el.find_element(
                        By.XPATH, '//div[@id="jdDiv"]/div/div[2]/p/span').get_attribute('innerText'))
                    job_location = str(parent_el.find_element(
                        By.XPATH, '//div[@id="jdDiv"]/div/div[2]/p[2]/span').get_attribute('innerText'))
                    job_salary = str(parent_el.find_element(
                        By.XPATH, '//div[@id="jdDiv"]/div/div[2]/p[3]/span').get_attribute('innerText'))
                    job_activity = str(parent_el.find_element(
                        By.XPATH, '//div[@id="jdDiv"]/div/div[4]/span[2]').text)
                    job_desc = str(driver.find_element(
                        By.XPATH, '//div[@id="apply_career"]/div/div[2]').get_attribute('innerHTML'))

                    if (len(driver.find_elements(By.CSS_SELECTOR, 'div.preferred-keyskills')) and
                            len(driver.find_elements(By.CSS_SELECTOR, 'div.other-keyskills'))):

                        job_skills_one = driver.find_element(
                            By.CSS_SELECTOR, 'div.preferred-keyskills').find_elements(By.XPATH, './div[2]/div/*')

                        job_skills_two = driver.find_element(
                            By.CSS_SELECTOR, 'div.other-keyskills').find_elements(By.XPATH, './div[2]/div/*')

                        all_job_one_skills = []
                        all_job_two_skills = []
                        for job_skil in job_skills_one:
                            all_job_one_skills.append(
                                job_skil.get_attribute('innerText'))
                        for job_skil in job_skills_two:
                            all_job_two_skills.append(
                                job_skil.get_attribute('innerText'))

                        all_job_skills = all_job_one_skills + all_job_two_skills
                        job_skills = ', '.join(all_job_skills)
                else:
                    role_name = str(driver.find_element(
                        By.XPATH, '//header/h1').text)
                    company_name = str(driver.find_element(
                        By.XPATH, '//section[@id="job_header"]/div/div/div[1]/a[1]').text)
                    exp_req = str(driver.find_element(
                        By.XPATH, '//section[@id="job_header"]/div/div[2]/div/div[1]/span').text)
                    job_location = str(driver.find_element(
                        By.XPATH, '//i[@class="ni-icon-location"][1]/following-sibling::span').text)
                    job_salary = str(driver.find_element(
                        By.XPATH, '//section[@id="job_header"]/div/div[2]/div/div[2]/span').text)
                    job_activity = str(driver.find_element(
                        By.XPATH, '//section[@id="job_header"]/div[2]/div/span[1]/span').text)
                    job_desc = str(driver.find_element(
                        By.XPATH, '//section[@id="job_header"]/following-sibling::section[1]/div[1]').text)
                    job_skills_element_one = driver.find_elements(
                        By.XPATH, '//section[@id="job_header"]/following-sibling::section[1]/div[4]/div[3]/*')

                    job_skills_element_two = driver.find_elements(
                        By.XPATH, '//section[@id="job_header"]/following-sibling::section[1]/div[4]/div[4]/*')

                    job_skills_element_other = driver.find_elements(
                        By.XPATH, '//section[@id="job_header"]/following-sibling::section[1]/div[4]')

                    if (len(job_skills_element_one) and len(job_skills_element_two)):
                        skills_one = []
                        skills_two = []

                        for el_one in job_skills_element_one:
                            skill_one = el_one.get_attribute('innerText')
                            skills_one.append(skill_one)

                        for el_two in job_skills_element_two:
                            skill_two = el_two.get_attribute('innerText')
                            skills_two.append(skill_two)

                        all_skills = skills_one + skills_two
                        job_skills = ' '.join(all_skills)

                    elif (len(job_skills_element_other)):
                        all_other_skills = driver.find_elements(
                            By.XPATH, '//section[@id="job_header"]/following-sibling::section[1]/div[4]/div[2]/*')
                        skills_other = []
                        for el_other in all_other_skills:
                            skill_other = el_other.get_attribute('innerText')
                            skills_other.append(skill_other)
                        job_skills = ' '.join(skills_other)

                relevancy = get_relevancy(
                    role_name, job_skills, exp_req)
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
                platform = 'Naukri Jobs'
                course_type = "web development"

                csvwriter.writerow([today, course_type, company_name, job_link, role_name, job_location,
                                    exp_req, platform, job_skills, job_desc, job_activity, relevancy, job_salary, phone_num, email_id])
            except:
                continue
