import json

class JSONDataExtractor:
  def __init__(self, file_path):
    self.file_path = file_path

  def extract_commit_data(self):
    all_commits = []

    with open(self.file_path) as f:
      data = json.load(f)
      for commit in data:
        for inner_commit in commit:
          all_commits.append(inner_commit['commit'])

    return all_commits
  
  def extract_collaborators(self, all_commits):
    collaborators = []
    collaborators_full_info = []
    for commit in all_commits:
      if commit['author']['name'] not in collaborators:
        collaborators.append(commit['author']['name'])
        collaborators_full_info.append({
          "name": commit['author']['name'],
          "email": commit['author']['email']
        })

    # print(f"Collaborators: {len(set(collaborators))}")
    # print(f"Collaborators Full Info: {len(collaborators_full_info)}")

    return collaborators
    

json_extractor = JSONDataExtractor("commits.json")

all_commits = json_extractor.extract_commit_data()

collaborators = json_extractor.extract_collaborators(all_commits)

print(f"Collaborators: {len(collaborators)}")
print(f"Commits: {len(all_commits)}")