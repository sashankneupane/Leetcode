import os
import time
import sys
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LeetCodeScraper:

    def __init__(self, username, password, cookies=None):
        
        self.username = username
        self.password = password

        # load cookies from the selenium session
        cookies = cookies or self.get_login_cookies()
        # load a requests session with the cookies
        self.session = self.get_requests_session(cookies)

        # LeetCode API URLs
        self.problems_url = "https://leetcode.com/api/problems/all/"
        self.submissions_url = "https://leetcode.com/api/submissions/"

        # get the problems info
        self.problems_info = self.get_problems_info()


    # Returns the cookies from the selenium session
    def get_login_cookies(self):

        # setup Chrome session
        options = Options()
        driver = webdriver.Chrome(options=options)

        # navigate to the LeetCode login page
        driver.get("https://leetcode.com/accounts/login/")

        # find the username and password input fields and submit button
        username_field = driver.find_element(By.ID, "id_login")
        password_field = driver.find_element(By.ID, "id_password")
        submit_button = driver.find_element(By.ID, "signin_btn")

        # enter the username and password
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)

        # wait for 2 seconds
        time.sleep(2)

        # click the submit button to log in
        submit_button.click()

        # wait for the login process to complete
        WebDriverWait(driver, 60).until(EC.url_changes(driver.current_url))

        # check if the login was successful
        if "leetcode.com/accounts/login" not in driver.current_url:
            print("Login successful!")
        else:
            print("Login failed.")

        cookies = driver.get_cookies()
        driver.quit()

        # return cookies
        return cookies


    # Returns a requests session with the given cookies (from selenium)
    def get_requests_session(self, cookies):

        # transfer the cookies to requests
        session = requests.Session()
        session.cookies.update(cookies)

        return session


    # Returns the problems info from the LeetCode API
    def get_problems_info(self):

        data = self.session.get(self.problems_url)

        if data.status_code == 200:
            # sort the problems by id
            data = data.json()
            data['stat_status_pairs'].sort(key=lambda x: x['stat']['frontend_question_id'])
            return data
        else:
            print("Failed to fetch problem data from the LeetCode API")
            sys.exit(1)


    # Returns all problem ids that have been solved
    def get_solved_problem_ids(self):

        solved = []
        problem_list = self.problems_info['stat_status_pairs']
        for problem in problem_list:
            if problem['status'] == 'ac':
                solved.append(problem['stat']['question_id'])

        return solved

    # write the latest accepted submission for given problem ids into the given path 
    def write_submissions(self, path, ids, update=False):
        updated = 0
        for id in ids:
            updated += self.write_submission(path, id, update=update)
        return updated


    # write the latest accepted submission for all solved problems into the given path
    def write_all_submissions(self, path, update=False):
        return self.write_submissions(path, self.get_solved_problem_ids(), update)


    def get_slug(self, id):
        # get the problem slug
        for problem in self.problems_info['stat_status_pairs']:
            if problem['stat']['question_id'] == id:
                slug = problem['stat']['question__title_slug']
                break

        return slug
        

    # Returns the latest accepted submission for a given problem
    def get_latest_submission(self, slug):

        # send a GET request to the submission URL using the session object
        response = self.session.get(self.submissions_url + slug)

        # check if the request was successful (status code 200)
        if response.status_code == 200:
            
            # extract the submission details from the API response
            submission_details = response.json()["submissions_dump"]

            # iterate through the submissions
            for submission in submission_details:

                # get only the latest accepted submission for a given problem
                if submission["status_display"] == "Accepted":
                    return submission

            return None
        else:
            print("Error occurred:", response.status_code)
            sys.exit(1)


    # Returns the problem description
    def get_description(self, slug):

        problem_url = f"https://leetcode.com/problems/{slug}/"

        # Send a GET request to the problem URL
        response = self.session.get(problem_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            problem_description = {
                "title": soup.find('div', class_='h-full').find('span', class_='mr-2').text.strip(),
                "folder": soup.find('div', class_='h-full').find('span', class_='mr-2').text.strip(),
                "difficulty": soup.find('div', class_='mt-3').div.text.strip(),
                "description": soup.find('div', class_='_1l1MA').contents,
            }

            return problem_description
        else:
            print("Error occurred:", response.status_code)
            sys.exit(1)


    # Create folder for the problem in the given path if it doesn't exist
    def create_folder(self, folder_name, path):

        if not os.path.exists(path):
            print(f"Path {path} does not exist")
            sys.exit(1)
        
        path_ = f"{path}{folder_name}"
        if not os.path.exists(path_):
            os.mkdir(path_)
            return 0

        # check if folder contains both main.cpp and README.md
        if not os.path.exists(f"{path_}/main.cpp") or not os.path.exists(f"{path_}/README.md"):
            return 0
        
        return 1


    # write files into the folder
    def write_submission(self, path, id=None, slug=None, update=False):

        # check if id or slug is provided
        if id is None and slug is None:
            print("Error: either id or slug must be provided")
            sys.exit(1)
        
        # check if id and slug are provided together
        if id is not None and slug is not None:
            print("Error: use either id or slug")
            sys.exit(1)
        
        # get the slug
        slug = slug if slug is not None else self.get_slug(id)
    
        problem_description = self.get_description(slug)    
        submission = self.get_latest_submission(slug)

        if not submission:
            return 0

        title = problem_description['title']
        difficulty = problem_description['difficulty']
        description_html = problem_description['description']
        folder_name = problem_description['folder']

        # check if the folder and files exist
        folder_status = self.create_folder(folder_name, path)

        # if all files and folder exist and update is False, return
        if folder_status and not update:
            return 0

        # Create README.md file
        with open(f'{path}{folder_name}/README.md', 'w') as file:
            file.write(f"# {title}\n\n")
            file.write(f"Difficulty: {difficulty}\n")
            file.write(f"## Description\n")

            for line in description_html:
                if line != '\n':
                    file.write(f"{line}\n")

        # Create main.cpp file
        with open(f"{path}{folder_name}/main.cpp", 'w') as file:
            file.write(submission['code'])

        return 1