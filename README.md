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
4. Run the script
```
python3 main.py <problem-id> <path/to/store/submission>
```
Example usage:
```
python3 main.py 1 ./
```

This will create a folder with the name of the problem and store the submission in it.