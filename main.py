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

load_dotenv()


# Authenticate the user and return the session object
def get_login_cookies(username, password):

    # setup Chrome session in headless mode
    options = Options()
    driver = webdriver.Chrome(options=options)

    # navigate to the LeetCode login page
    driver.get("https://leetcode.com/accounts/login/")

    # find the username and password input fields and submit button
    username_field = driver.find_element(By.ID, "id_login")
    password_field = driver.find_element(By.ID, "id_password")
    submit_button = driver.find_element(By.ID, "signin_btn")

    # enter the username and password
    username_field.send_keys(username)
    password_field.send_keys(password)

    # wait for 2 seconds
    time.sleep(2)

    # click the submit button to log in
    submit_button.click()

    # wait for the login process to complete
    WebDriverWait(driver, 5).until(EC.url_changes(driver.current_url))

    # check if the login was successful
    if "leetcode.com/accounts/login" not in driver.current_url:
        print("Login successful!")
    else:
        print("Login failed.")

    cookies = driver.get_cookies()

    driver.quit()

    # return cookies
    return cookies


def get_latest_submission(id, session):

    slug = fetch_problem_slug(id)

    submissions_url = f"https://leetcode.com/api/submissions/{slug}/"

    # send a GET request to the submission URL using the session object
    response = session.get(submissions_url)

    # check if the request was successful (status code 200)
    if response.status_code == 200:
        
        # extract the submission details from the API response
        submission_details = response.json()["submissions_dump"]

        # iterate through the submissions
        for submission in submission_details:

            # get only the latest accepted submission for a given problem
            if submission["status_display"] == "Accepted":
                return submission

        print("No accepted submissions found.")
        sys.exit(1)
    else:
        print("Error occurred:", response.status_code)
        sys.exit(1)


def fetch_problem_slug(problem_id):
    # LeetCode API endpoint to get problem details
    url = f"https://leetcode.com/api/problems/all/"

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:

        # Extract the problem details from the API response
        problem_details = response.json()["stat_status_pairs"]

        # Find the problem with the given ID
        for problem in problem_details:
            if problem["stat"]["question_id"] == int(problem_id):
                return problem["stat"]["question__title_slug"]

        print("Problem ID not found.")
        sys.exit(1)
    else:
        print("Error occurred:", response.status_code)
        sys.exit(1)


def get_problem_url(problem_id):
    # Get the problem slug
    problem_slug = fetch_problem_slug(problem_id)

    # Return the problem URL
    return f"https://leetcode.com/problems/{problem_slug}/"


def scrape_problem(session, problem_id, path):

    problem_url = get_problem_url(problem_id)

    # Send a GET request to the problem URL
    response = requests.get(problem_url)

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
        
        submission = get_latest_submission(problem_id, session)
        write_content(path, problem_description, submission)

    else:
        print("Error occurred:", response.status_code)
        sys.exit(1)

# Create a folder with the name of the problem if it doesn't exist
def create_folder(folder_name, path):
    if not os.path.exists(path):
        print(f"Path {path} does not exist")
        sys.exit(1)
    
    path_ = f"{path}{folder_name}"
    if not os.path.exists(path_):
        os.mkdir(path_)

# Write README.md file
def write_content(path, problem_description, submission):
    title = problem_description['title']
    difficulty = problem_description['difficulty']
    description_html = problem_description['description']
    folder_name = problem_description['folder']

    create_folder(folder_name, path)

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


if __name__ == "__main__":

    # get command line argument for problem id

    # check if problem id is provided
    if len(sys.argv) < 2:
        print("Problem ID not provided. Example usage:")
        print("python main.py <problem_id> <path>")
        sys.exit(1)

    problem_id = sys.argv[1]

    # get command line argument for path
    # set it default to current directory
    PATH = sys.argv[2] if len(sys.argv) > 2 else "./leetcode/"

    # check the validity of command line arguments
    if not problem_id.isdigit():
        print("Invalid problem ID.")
        sys.exit(1)

    if not os.path.exists(PATH):
        print("Invalid path.")
        sys.exit(1)

 
    username = os.environ.get("LEETCODE_USERNAME")
    password = os.environ.get("LEETCODE_PASSWORD")

    cookies = get_login_cookies(username, password)

    # transfer the cookies to requests
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    scrape_problem(session, problem_id, PATH)