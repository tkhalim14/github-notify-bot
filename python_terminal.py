import os

folder_path = './user_github_data'

github_ids = {}
filenames = [f[:-5] for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
filenames = [f.split('_') for f in filenames]
for key, value in filenames:
  github_ids[key] = value

print(github_ids)

