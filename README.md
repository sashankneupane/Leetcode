Github repository that scrapes submissioms from Leetcode.

## Installation
1. Clone the repository
2. Install the requirements
```
pip install -r requirements.txt
```
3. Create a `.env` file in the root directory and add the following variables
```
LEETCODE_USERNAME=<your-leetcode-username>
LEETCODE_PASSWORD=<your-leetcode-password>
```
4. Add cookies as well if you want to use cookies to login
```
LEETCODE_COOKIES=<your-leetcode-cookies>
csrftoken=<your-csrftoken>
```
If you do not use cookies, the script will use your username and password to login. Leetcode might prompt you to solve a captcha. The script allows 60 seconds to solve the captcha. If you fail to solve the captcha in 60 seconds, the script will exit. Using cookies avoids this problem.

<!-- Explain all the command line arguments -->
## Usage
```
usage: python main.py [--cookies] [--id] [--slug] [--ids] [--all] [--path] [--update]
```

### Arguments
```
--cookies, -c: Use cookies to login
--id, -i: Scrape a single problem by its id
--slug, -s: Scrape a single problem by its slug
--ids, -ids: Scrape multiple problems by their ids
--all, -a: Scrape all problems
--path, -p: Path to the directory where the problems will be saved
--update, -u: Update already existing submissions as well
```

### Examples
```bash
python main.py -c -i 1 -p ./leetcode/
python main.py -c -s two-sum -u
python main.py -c -ids 1 2 3 4 5
python main.py -c -a
```

This will create a folder with its id and name in the specified path and save the latest submission in it.