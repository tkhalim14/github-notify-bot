import json

def find_set_difference(new_json, old_json):
  
  difference = [entry for entry in new_json if entry not in old_json]

  return difference


lol1=[]
lol2=[]
with open('./lol.json', 'r') as f:
  lol1 = json.load(f)

with open('./lol2.json', 'r') as f:
  lol2 = json.load(f)

print(find_set_difference(lol1, lol2))