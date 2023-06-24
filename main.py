import os
import argparse
from dotenv import load_dotenv
from scraper import LeetCodeScraper


if __name__ == "__main__":

    # load leetcode credentials from .env file
    load_dotenv()

    username = os.environ.get("LEETCODE_USERNAME")
    password = os.environ.get("LEETCODE_PASSWORD")

    scrape_session = LeetCodeScraper(username, password)

    # create an ArgumentParser object
    parser = argparse.ArgumentParser(description="LeetCode Submissions Updater")

    # Add arguments for different functionalities
    parser.add_argument("--id", '-i', metavar="ID", type=int, help="Update submissions by its ID") # individual problem through its ID
    parser.add_argument("--update", '-u', action="store_true", help="Rewrite the existing submissions. Default: False") # whether to update the existing submissions
    parser.add_argument("--slug", '-s', metavar="SLUG", type=str, help="Update submissions by its slug") # individual problem through its slug
    parser.add_argument("--ids", '-ids', metavar="ID", nargs="+", type=int, help="Update a list of submissions by their IDs") # a list of problems through their IDs
    parser.add_argument("--all", '-a', action="store_true", help="Update all submissions") # all problems
    parser.add_argument("--path", '-p', metavar="PATH", type=str, default="./leetcode/", help="Path to the submissions folder") # path to the submissions folder

    # Parse the command-line arguments
    args = parser.parse_args()

    # check if all is true along with id, slug, ids
    if args.all and (args.id or args.slug or args.ids):
        print("Error: --all cannot be used with --id, --slug or --ids")
        sys.exit(1)
    
    # check if id and slug are provided together
    if args.id and args.slug:
        print("Error: use either --id or --slug")
        sys.exit(1)

    # check if id and ids are provided together
    if args.ids and (args.id or args.slug):
        print("Error: use --ids to update multiple submissions")
        sys.exit(1)


    # check the provided arguments and perform the corresponding actions
    if args.id:
        if scrape_session.write_submission(args.path, id=args.id, update=args.update):
            print("Submission updated successfully")

    if args.slug:
        if scrape_session.write_submission(args.path, slug=args.slug, update=args.update):
            print("Submission updated successfully")

    if args.ids:
        total = scrape_session.write_submissions(args.path, args.ids, update=args.update)
        print(f"{total} submissions updated successfully")

    if args.all:
        total = scrape_session.write_all_submissions(args.path, update=args.update)
        print(f"{total} submissions updated successfully")