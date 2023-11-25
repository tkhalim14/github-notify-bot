# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot
import discord
from discord.ext import commands, tasks
import requests, os, json, datetime
from dotenv import load_dotenv
import asyncio

load_dotenv()


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

GITHUB_API_BASE_URL = 'https://api.github.com'


folder_path = './user_github_data'

# Initialize the github ids from past history 
github_ids = {}


def format_time(input_time):
  # Parse the input time string
  parsed_time = datetime.datetime.strptime(input_time, '%Y-%m-%dT%H:%M:%SZ')

  # Format the time into a nice string
  formatted_time = parsed_time.strftime('%A, %B %d, %Y %I:%M %p UTC')

  return formatted_time


def get_github_events(GITHUB_USERNAME):
  url = f'{GITHUB_API_BASE_URL}/users/{GITHUB_USERNAME}/events/public'
  # print(url)
  response = requests.get(url)
  # print(response.json())
  json_data = response.json()

  s = "Data retrieval Failed"
  g = ""

  for i, event in enumerate(json_data):
    if i >= 5:
      break
    repo_name = event["repo"]["name"]
    repo_link = event["repo"]["url"]
    commit_type = event["type"]
    created_at = format_time(event["created_at"])

    if commit_type == "PushEvent":
      commit_info = event["payload"]["commits"][0]
      commit_author = commit_info["author"]["name"]
      commit_message = commit_info["message"]

      # s = "Repository: " + repo_name + "\nCommit Author: " + commit_author + "\nCommit Message: " + commit_message + "\n"

      message = (
          f"## :blue_circle: **Repository:** [{repo_name}]({repo_link})\n\n"
          f"> **Commit Type:** *{commit_type}*\n"
          f"> **Commit Author:** *{commit_author}*\n"
          f"> **Commit Message:** {commit_message}\n"
          f"> **Time:** {created_at}\n\n")
    else:
      # s = "Repository: " + repo_name + "\nCommit Type: " + commit_type + "\n"
      ref_info = event["payload"]["ref"]
      ref_type = event["payload"]["ref_type"]
      message = (
          f" \n## :blue_circle: **Repository:** [{repo_name}]({repo_link})\n\n"
          f"> **Commit Type:** *{commit_type}*\n"
          f"> **Reference Type:** *{ref_type}*\n"
          f"> **Reference Message:** {ref_info}\n"
          f"> **Time:** {created_at}\n\n")
    g += message
  return g if g != "" else s


def write_json_to_file(folder_path, user_id):

    url = f'{GITHUB_API_BASE_URL}/users/{github_ids[user_id]}/events/public'
    # print(url)
    response = requests.get(url)
    # print(response.json())
    json_data = response.json()

    # print(type(json_data))
    # print("hello")
    file_path = folder_path+f'/{user_id}_{github_ids[user_id]}.json'
    try:
        with open(file_path,'w') as file:
          json.dump(json_data, file)
        print(f'Successfully wrote JSON data to {file_path}')
    except Exception as e:
        print(f'Error writing JSON data to {file_path}: {e}')


def update_available(file_path, json_data):
    """
    Load a JSON file and compare it with another JSON variable.

    Parameters:
    - file_path (str): The path to the JSON file.
    - json_data (dict): The JSON data to compare.

    Returns:
    - bool: True if the JSON file matches the provided JSON data, False otherwise.
    """
    try:
        # Load JSON from file
        with open(file_path, 'r') as file:
            file_content = json.load(file)
        
        # Compare JSON data
        return file_content != json_data
    except FileNotFoundError:
        print(f'Error: File not found - {file_path}')
        return False
    except json.JSONDecodeError:
        print(f'Error: Unable to decode JSON in file - {file_path}')
        return False
    except Exception as e:
        print(f'Error comparing JSON file and variable: {e}')
        return False


def find_set_difference(new_json, old_json):
  
  difference = [entry for entry in new_json if entry not in old_json]

  return difference





last_checked_timestamp = datetime.datetime.utcnow()

def discord_bot():

  async def check_for_updates(user_names, channel):
      print("Checking for updates...")
      global last_checked_timestamp

      # Get the current timestamp
      current_timestamp = datetime.datetime.utcnow()
      
      # print("huzzah")
      # print(user_names)
      for user in user_names:
        if user not in github_ids.keys():
          continue
        url = f'{GITHUB_API_BASE_URL}/users/{github_ids[user]}/events/public'
        response = requests.get(url)
        json_data = response.json()[:5]

        global folder_path
        file_path = folder_path + f'/{user}_{github_ids[user]}.json'

        # If an update is available, notify the Discord server
        
        try:

          if update_available(file_path, json_data):            
            
            with open(file_path, 'r') as file:
              old_data = json.load(file)

            difference = find_set_difference(json_data, old_data)

            # with open('./lol.json', 'r') as f:
            #   json.dump(difference, f)
            print(difference)

            with open(file_path, 'w') as f:
              json.dump(json_data, f)
            
            s = "Data retrieval Failed"
            g = ""

            for event in (difference):
              repo_name = event["repo"]["name"]
              repo_link = event["repo"]["url"]
              commit_type = event["type"]
              created_at = format_time(event["created_at"])

              if commit_type == "PushEvent":
                commit_info = event["payload"]["commits"][0]
                commit_author = commit_info["author"]["name"]
                commit_message = commit_info["message"]

                # s = "Repository: " + repo_name + "\nCommit Author: " + commit_author + "\nCommit Message: " + commit_message + "\n"

                message = (
                    f"## :blue_circle: **Repository:** [{repo_name}]({repo_link})\n\n"
                    f"> **Commit Type:** *{commit_type}*\n"
                    f"> **Commit Author:** *{commit_author}*\n"
                    f"> **Commit Message:** \n``` {commit_message} ```\n"
                    f"> **Time:** {created_at}\n\n")
              else:
                # s = "Repository: " + repo_name + "\nCommit Type: " + commit_type + "\n"
                ref_info = event["payload"]["ref"]
                ref_type = event["payload"]["ref_type"]
                message = (
                    f" \n## :blue_circle: **Repository:** [{repo_name}]({repo_link})\n\n"
                    f"> **Commit Type:** *{commit_type}*\n"
                    f"> **Reference Type:** *{ref_type}*\n"
                    f"> **Reference Message:** \n``` {ref_info} ```\n"
                    f"> **Time:** {created_at}\n\n")
              g += message
            if g!="":
              await channel.send(f'## Update: User {user} has put a new update.\n\n{g}')
        except Exception as e:
          print("Error while updating :", e)

      # Update the last checked timestamp
      last_checked_timestamp = current_timestamp

      


  async def task_init(client):

    while True:
      # task_list = []

      for guild in client.guilds:
          default_channel = guild.system_channel  # This is the default channel where system messages are sent
          # print(default_channel)
          member_list = []
          for member in guild.members:
            if member!= client.user:
              member_list.append(member.name)
          # print(member_list)
          if default_channel:
              print("Checking for server updates...")
              # await check_for_updates(list(github_ids.keys()), default_channel)
              await check_for_updates(member_list, default_channel)
      
      # await asyncio.gather(*task_list)
      await asyncio.sleep(900.0)

  @client.event
  async def on_ready():

    # Initialize the github_ids global set
    filenames = [f[:-5] for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    filenames = [f.split('_') for f in filenames]
    for key, value in filenames:
      github_ids[key] = value
    # print(github_ids)

    all_servers_task_list = [task_init(client)]
    await asyncio.gather(*all_servers_task_list)
    
    print('We have logged in as {0.user}'.format(client))

  @client.event
  async def on_message(message):
    # await bot.process_commands(message)
    if message.author == client.user:
      return

    # check_for_updates.start(list(github_ids.keys()), message)
    usr_msg = message.content

    if usr_msg!=None:
      if usr_msg[0] == '!':
        # add all commands here
        arguments = usr_msg.split(" ")
        if arguments[0]=='!github':
          if len(arguments) == 2 :
            await message.channel.send(get_github_events(arguments[1]))
          
          elif len(arguments) == 1:
            # need to implement logic to check update for every 15 minutes
            guild = message.guild
            member_list = guild.members
            user_names = [f"### -> `{member.id} #{member.discriminator}`" for member in member_list]
            user_names_string = '\n'.join(user_names)
            await message.channel.send(f'## **Users on the server:**\n{user_names_string}')

        elif arguments[0]=='!list':
            if len(arguments) == 1 :
              # fetch all users
              guild = message.guild
              member_list = guild.members
              user_names = [f"### -> `{member.name} #{member.discriminator}`" for member in member_list]
              user_names_string = '\n'.join(user_names)
              await message.channel.send(f'## **Users on the server:**\n{user_names_string}')
        
        elif arguments[0]=='!linkgithub':
          if len(arguments) == 2:
            """Set the GitHub ID for the calling user."""
            print("Linking to github")
            user = message.author
            github_id = arguments[1]
            github_ids[user.name] = github_id
            # print("hello")
            await message.channel.send(f"GitHub ID set for `{user.name}` as `{github_id}`")
            # create separate files for each of them on bot to store top 5 github repos
            # print(github_ids)
            write_json_to_file(folder_path, user.name)

        elif arguments[0]=='!viewgithub':
          if len(arguments) == 1:
            try:
              await message.channel.send(f"GitHub ID for {message.author.name}: {github_ids[message.author.name]}")
            except Exception as e:
              await message.channel.send(f"Error your GitHub ID is not linked. Use command `!linkgithub [github username]` to link your account.")
        else:
          await message.channel.send("Invalid request")
      else:
        return
        # await message.channel.send("You said : " + usr_msg)
    else: return

  try:
    token = os.getenv("TOKEN") or ""
    if token == "":
      raise Exception("Please add your token to the Secrets pane.")
    client.run(token)
  except Exception as e:
    raise e


discord_bot()

# if __name__ == "__main__":
#   asyncio.run(main())