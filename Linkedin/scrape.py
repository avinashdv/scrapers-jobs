from cmath import e
from tkinter import E
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import date
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
import csv
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
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
            3. Experience: Relevant Jobs is Entry level
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


def gather_urls():
    try:
        fBody = driver.find_element(
            By.XPATH, '//div[normalize-space(@class)="jobs-search-results-list"]')
        scroll = 0

        while scroll < 9:
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                                  fBody)
            scroll += 1
            time.sleep(2)

        all_jobs_parent = driver.find_elements(
            By.XPATH, '//ul[@class="scaffold-layout__list-container"]/*')

        jobs_length = len(all_jobs_parent)

        page_links = []
        for i in range(1, jobs_length + 1):
            job_link = str(driver.find_element(
                By.XPATH, f'//ul[@class="scaffold-layout__list-container"]/li[{i}]/div/div/div/div[2]/div/a').get_attribute('href'))
            page_links.append(job_link)
        return page_links
    except:
        print('missing element================')
        return False


with open('LinkedinPostings.csv', 'w', newline='\n', encoding="utf-8") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["created_at", "course_type", "company_name", "job_link", "role_name",
                       "job_location", "experience", "Platform", "skills", "description", "Job_Activity", "role_relevancy" 'salary', 'phone_number', 'Email_id'])
    options = webdriver.ChromeOptions()
    s = Service(
        "C:/Users/91868/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=s,
                              options=options)

    driver.get('https://www.linkedin.com/login')
    time.sleep(5)

    username = driver.find_element(By.ID, "username")
    username.send_keys("abitak1999@gmail.com")

    pword = driver.find_element(By.ID, "password")
    pword.send_keys("Shubhankar@3103")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    time.sleep(20)

    driver.get('https://www.linkedin.com/jobs/')

    all_roles = pd.read_csv(
        r"E:/The Office/scrappers/Linkedin/roles.txt", sep=",", header=None)[0].tolist()

    job_links = []
    time.sleep(2)
    for role in all_roles:
        job_search = driver.find_element(
            By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")
        job_search.clear()
        time.sleep(1)
        job_search.send_keys(role)

        time.sleep(1)

        job_location = driver.find_element(
            By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")
        job_location.clear()
        time.sleep(1)
        job_location.send_keys('India' + '\n')

        time.sleep(4)

        url = driver.current_url

        param = url.split('?')
        job_id = param[1].split('&')[0].split('=')[1]
        geo_loc = '102713980'
        duration = '86400'
        count = 25

        url.split('?')
        i = 0
        while i < 40:
            if (i <= 0):
                job_id = param[1].split('=')[1].split('&')[0]
                initial_url = f'https://www.linkedin.com/jobs/search/?currentJobId={str(job_id)}&f_TPR=r{duration}&geoId={geo_loc}&keywords={role}&location=India&refresh=true'
                driver.get(initial_url)
                time.sleep(2)
                urlsData = gather_urls()
                if (urlsData):
                    job_links = job_links + urlsData
            else:
                modified_url = f'https://www.linkedin.com/jobs/search/?currentJobId={str(job_id)}&f_TPR=r{duration}&geoId={geo_loc}&keywords={role}&location=India&refresh=true&start={count}'
                driver.get(modified_url)
                time.sleep(2)
                urlsData = gather_urls()
                if (urlsData):
                    job_links = job_links + urlsData
                    count = count+25
                else:
                    break
            i = i+1

    for job_link in job_links:
        driver.get(job_link)
        time.sleep(4)
        try:
            role_name = str(driver.find_element(By.CSS_SELECTOR, 'h1').text)

            company_name = str(driver.find_element(
                By.XPATH, '//div[@class="jobs-unified-top-card__primary-description"]/div/a').text)

            location_html = str(driver.find_element(
                By.XPATH, '//div[@class="jobs-unified-top-card__primary-description"]/div').get_attribute('innerHTML'))

            job_location = ''
            if (len(location_html)):
                job_location = location_html.split('·')[1].split('<')[0]

            exp_req_text = str(driver.find_element(
                By.XPATH, '//li[@class="jobs-unified-top-card__job-insight"]/span').text)

            exp_req_items = exp_req_text.split('·')
            exp_req = ''
            if (len(exp_req_items) > 1):
                exp_req = exp_req_items[1]

            job_desc = str(driver.find_element(
                By.ID, "job-details").text)

            job_activity = str(driver.find_element(
                By.XPATH, '//div[@class="jobs-unified-top-card__primary-description"]/div/span[3]/strong').get_attribute('innerText'))

            job_skills_element = driver.find_element(
                By.XPATH, '//span[text()="Show all skills"]')

            job_skills_element.click()
            time.sleep(3)

            parent = driver.find_elements(
                By.XPATH, '//ul[@class="job-details-skill-match-status-list"]/*')

            parent_length = len(parent)

            skills_length = parent_length

            job_skills = ''

            for i in range(1, skills_length + 1):
                skill = str(driver.find_element(
                    By.XPATH, f'//ul[@class="job-details-skill-match-status-list"]/li[{i}]/div/div[2]').text)
                if (i == 1):
                    job_skills = job_skills + skill
                else:
                    job_skills = job_skills + ", " + skill
        except:
            continue

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
        platform = 'Linkedin'
        course_type = "web development"
        salary = ''
        csvwriter.writerow([today, course_type, company_name, job_link, role_name, job_location,
                            exp_req, platform, job_skills, job_desc, job_activity, relevancy, salary, phone_num, email_id])
