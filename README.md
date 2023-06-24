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

<!-- Explain all the command line arguments -->
## Usage
```
usage: main.py [--id] [--slug] [--ids] [--all] [--path] [--update]
```

### Arguments
```
--id, -i: Scrape a single problem by its id
--slug, -s: Scrape a single problem by its slug
--ids, -ids: Scrape multiple problems by their ids
--all, -a: Scrape all problems
--path, -p: Path to the directory where the problems will be saved
--update, -u: Update already existing submissions as well
```

### Examples
```bash
python main.py -i 1 -p ./leetcode/
python main.py -s two-sum -u
python main.py -ids 1 2 3 4 5
python main.py -a
```

This will create a folder with its id and name in the specified path and save the latest submission in it.