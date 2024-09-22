import requests
import json
import time
import datetime
from json_data_extractor import JSONDataExtractor
from dotenv import load_dotenv
import os

load_dotenv()

#define the base url
base_url = "https://api.github.com"
fine_grained_token = os.getenv("FINE_GRAINED_TOKEN")

# my endpoints 
all_endpoints = {
  "general": "/repos/boyter/scc",
  "issues": "/repos/boyter/scc/issues",
  "commits": "/repos/boyter/scc/commits"
}

print(time.time())

class SCCRepoMiner:
  def __init__(self) -> None:
    pass

  def get_commits_file(self):
    all_commits = []

    
    iterator = 1
    while True:
      project_commits = requests.get(
        f"{base_url}/{all_endpoints['commits']}?page={iterator}&per_page=100",
        headers = {
          "Accept": "application/vnd.github.v3+json",
          "Authorization": fine_grained_token,
          "User-Agent": "charlesgobina"
        },
      )

      project_commits_parsed = json.loads(project_commits.content)
      reset_time_stamp = project_commits.headers['X-RateLimit-Reset']
      formatted_reset_time = datetime.datetime.fromtimestamp(int(reset_time_stamp)).strftime('%Y-%m-%d %H:%M:%S')

      if project_commits.headers['X-RateLimit-Remaining'] == "0":
        # parse the formatted_reset_time back to a date
        datetime_object = datetime.datetime.strptime(formatted_reset_time, '%Y-%m-%d %H:%M:%S')
        current_time_object = datetime.datetime.now()

        # calculate the difference in time
        time_difference = datetime_object - current_time_object
        # convert the time difference to minutes
        time_difference_minutes = time_difference.total_seconds() / 60

        print(f"Rate limit exceeded. Resuming in {time_difference_minutes} minutes")

        time.sleep(time_difference_minutes)

        print("Waking up... Resuming")

      if project_commits.status_code == 200 and len(project_commits_parsed) == 0:
        # save the commits to a json file
        with open("commits.json", "w") as commits_file:
          json.dump(all_commits, commits_file)
        break
      else:
        print("Going through page: ", iterator)
        all_commits.append(project_commits_parsed)
        iterator += 1
    return all_commits

  def get_issues(self):
    all_issues = {
      "open": [],
      "closed": []
    }

    iterator = 1
    got_broken = False

    while True or got_broken  :
      got_broken = False
      project_issues = requests.get(
        f"{base_url}/{all_endpoints['issues']}?page={iterator}&per_page=100",
        headers = {
          "Accept": "application/vnd.github.v3+json",
          "Authorization": fine_grained_token,
          "User-Agent": "charlesgobina"
        },
      )


      reset_time_stamp = project_issues.headers['X-RateLimit-Reset']

      formatted_reset_time = datetime.datetime.fromtimestamp(int(reset_time_stamp)).strftime('%Y-%m-%d %H:%M:%S')  

      print(f"Rate limit remaining: {project_issues.headers['X-RateLimit-Remaining']}") 


      if project_issues.headers['X-RateLimit-Remaining'] == "0":
        print(project_issues.status_code)   
        # parse the formatted_reset_time back to a date
        datetime_object = datetime.datetime.strptime(formatted_reset_time, '%Y-%m-%d %H:%M:%S')
        current_time_object = datetime.datetime.now()

        # calculate the difference in time
        time_difference = datetime_object - current_time_object
        # convert the time difference to minutes
        time_difference_minutes = time_difference.total_seconds() / 60

        print(f"Rate limit exceeded. Resuming in {time_difference_minutes} minutes")

        time.sleep(time_difference_minutes)

        print("Waking up... Resuming")
        got_broken = True
        


      project_issues_parsed = json.loads(project_issues.content)

      if project_issues.status_code == 200 and len(project_issues_parsed) == 0:
        break
      elif project_issues.status_code == 200:
        for issue in project_issues_parsed:
          if issue["state"] == "open":
            all_issues["open"].append(issue)
          else:
            all_issues["closed"].append(issue)
      
      iterator += 1 if not got_broken else iterator

    
    return all_issues

  def get_creation_date(self):
    project_creation_date = requests.get(
        f"{base_url}/{all_endpoints['general']}",
        headers = {
          "Accept": "application/vnd.github.v3+json",
          "Authorization": fine_grained_token,
          "User-Agent": "charlesgobina"
        },
      )
    project_creation_date_parsed = json.loads(project_creation_date.content)

    date_object = datetime.datetime.strptime(project_creation_date_parsed["created_at"], '%Y-%m-%dT%H:%M:%SZ')
    formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_date

    

  def get_main_language(self):
    project_main_language = requests.get(
        f"{base_url}/{all_endpoints['general']}",
        headers = {
          "Accept": "application/vnd.github.v3+json",
          "Authorization": fine_grained_token,
          "User-Agent": "charlesgobina"
        },
      )
    project_main_language_parsed = json.loads(project_main_language.content)

    return project_main_language_parsed["language"]
  
  def get_repo_data_file(self, repo_data):
    with open("repo_data.json", "w") as repo_data_file:
      json.dump(repo_data, repo_data_file)
    


repo_miner = SCCRepoMiner()
json_data_extractor = JSONDataExtractor("commits.json")

all_issues = repo_miner.get_issues()

open_issues = all_issues["open"]

closed_issues = all_issues["closed"]

main_language = repo_miner.get_main_language()

creation_date = repo_miner.get_creation_date()

commits = json_data_extractor.extract_commit_data()

contributors = json_data_extractor.extract_collaborators(commits)



repo_info = {
  "main_language": main_language,
  "creation_date": creation_date,
  "number_of_contributors": len(contributors),
  "number_of_commits": len(commits),
  "open_issues": len(open_issues),
  "closed_issues": len(closed_issues)
}

repo_miner.get_repo_data_file(repo_info)

# print(repo_info)