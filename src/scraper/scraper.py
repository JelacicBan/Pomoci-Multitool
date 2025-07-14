import requests
import sys
import os
import zipfile
import tempfile
import datetime
from colorama import init, Fore, Style
from usefull.clear import cl
init()
SUCCESS = Fore.GREEN
ERROR = Fore.RED
WARNING = Fore.YELLOW
INFO = Fore.BLUE
HEADER = Fore.CYAN
RESET = Style.RESET_ALL
TOKEN = None
guild_cache = None

def ensure_token():
    global TOKEN
    if TOKEN is None:
        TOKEN = input(f"{INFO}Enter your Discord token: {RESET}").strip()
    return {"Authorization": TOKEN}

def api_request(method, endpoint, payload=None, params=None):
    base_url = "https://discord.com/api/v10"

    headers = ensure_token()
    try:
        response = requests.request(method, base_url + endpoint, headers=headers, json=payload, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"{ERROR}[!] Error: {e}{RESET}")
        if response.status_code == 400:
            print(f"{ERROR}[!] Bad Request: Invalid request format. Response: {response.text}{RESET}")
        elif response.status_code == 401:
            print(f"{ERROR}[!] Unauthorized: Invalid token. Please enter a new token.{RESET}")
            global TOKEN
            TOKEN = None
            ensure_token()
            return api_request(method, endpoint, payload, params)
        elif response.status_code == 403:
            print(f"{ERROR}[!] Forbidden: You lack the necessary permissions or scopes.{RESET}")
            print(f"{ERROR}[!] Response: {response.text}{RESET}")
        elif response.status_code == 404:
            print(f"{ERROR}[!] Not Found: The resource does not exist.{RESET}")
        else:
            print(f"{ERROR}[!] Response: {response.text}{RESET}")
        return None

def get_user_guilds():
    global guild_cache
    if guild_cache is None:
        print(f"{INFO}[+] Fetching guilds...{RESET}")
        guild_cache = api_request("GET", "/users/@me/guilds")
    return guild_cache if guild_cache else []

def list_guilds():
    guilds = get_user_guilds()
    if not guilds:
        print(f"{ERROR}[!] Failed to fetch guilds.{RESET}")
        return None
    print(f"{HEADER}\nAvailable Servers:{RESET}")
    for idx, guild in enumerate(guilds, 1):
        print(f"{SUCCESS}[{idx}] {guild['name']} (ID: {guild['id']}){RESET}")
    while True:
        choice = input(f"{INFO}\nSelect a server by number (or 'q' to quit): {RESET}").strip().lower()
        if choice == 'q':
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(guilds):
                return guilds[idx]['id']
            print(f"{ERROR}[!] Invalid selection. Try again.{RESET}")
        except ValueError:
            print(f"{ERROR}[!] Invalid input. Please enter a number or 'q'.{RESET}")

def list_channels(guild_id):
    print(f"{INFO}[+] Fetching channels for guild {guild_id}...{RESET}")
    channels = api_request("GET", f"/guilds/{guild_id}/channels")
    if not channels:
        print(f"{ERROR}[!] Failed to fetch channels.{RESET}")
        return None, None
    text_channels = [ch for ch in channels if ch["type"] == 0]
    if not text_channels:
        print(f"{WARNING}[!] No text channels found in this server.{RESET}")
        return None, None
    print(f"{HEADER}\nAvailable Channels:{RESET}")
    for idx, channel in enumerate(text_channels, 1):
        print(f"{SUCCESS}[{idx}] {channel['name']} (ID: {channel['id']}){RESET}")
    while True:
        choice = input(f"{INFO}\nSelect a channel by number (or 'q' to quit): {RESET}").strip().lower()
        if choice == 'q':
            return None, None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(text_channels):
                return text_channels[idx]['id'], text_channels[idx]['name']
            print(f"{ERROR}[!] Invalid selection. Try again.{RESET}")
        except ValueError:
            print(f"{ERROR}[!] Invalid input. Please enter a number or 'q'.{RESET}")

def get_unique_filename(dir_path, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(dir_path, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename

def scrape_files():
    guild_id = list_guilds()
    if guild_id:
        channel_id, channel_name = list_channels(guild_id)
        if channel_id:
            messages = []
            before = None
            total_messages = 0
            while True:
                params = {"limit": 100, "before": before} if before else {"limit": 100}
                data = api_request("GET", f"/channels/{channel_id}/messages", params=params)
                if not data:
                    break
                messages.extend(data)
                total_messages += len(data)
                print(f"{SUCCESS}[+] Loaded {total_messages} messages so far...{RESET}")
                if len(data) < 100:
                    break
                before = data[-1]['id']

            with tempfile.TemporaryDirectory() as temp_dir:
                downloaded_files = []
                for message in messages:
                    for attachment in message.get("attachments", []):
                        response = requests.get(attachment['url'])
                        if response.status_code == 200:
                            filename = get_unique_filename(temp_dir, attachment['filename'])
                            file_path = os.path.join(temp_dir, filename)
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                            downloaded_files.append(file_path)

                if not downloaded_files:
                    print(f"{WARNING}[!] No attachments found in this channel.{RESET}")
                else:
                    # 🔽 Step 1: Create a folder to save zips
                    zip_output_dir = "downloads"
                    os.makedirs(zip_output_dir, exist_ok=True)

                    # 🔽 Step 2: Generate zip path inside that folder
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    zip_filename = f"{channel_name}_{timestamp}.zip"
                    zip_path = os.path.join(zip_output_dir, zip_filename)

                    # 🔽 Step 3: Write the zip there
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for file_path in downloaded_files:
                            arcname = os.path.basename(file_path)
                            zipf.write(file_path, arcname)

                    print(f"{SUCCESS}[+] All files have been downloaded and zipped into {zip_path}{RESET}")

    input(f"{INFO}\nPress Enter to continue...{RESET}")
    
def scrape_friends():
    print(f"{INFO}[+] Fetching friends...{RESET}")
    data = api_request("GET", "/users/@me/relationships")
    if data:
        friends = [rel for rel in data if rel["type"] == 1]
        if not friends:
            print(f"{WARNING}[!] No friends found.{RESET}")
        else:
            print(f"{HEADER}\nFriends:{RESET}")
            for friend in friends:
                user = friend["user"]
                print(f"{SUCCESS}Friend: {user['username']}#{user['discriminator']} (ID: {user['id']}){RESET}")
    else:
        print(f"{ERROR}[!] Failed to fetch relationships.{RESET}")
    input(f"{INFO}\nPress Enter to continue...{RESET}")

def send_message():
    guild_id = list_guilds()
    if guild_id:
        channel_id, _ = list_channels(guild_id)
        if channel_id:
            content = input(f"{INFO}Enter message content: {RESET}").strip()
            if content:
                payload = {"content": content}
                result = api_request("POST", f"/channels/{channel_id}/messages", payload=payload)
                if result:
                    print(f"{SUCCESS}[+] Message sent successfully!{RESET}")
    input(f"{INFO}\nPress Enter to continue...{RESET}")

def get_dm_channel(user_id):
    payload = {"recipient_id": user_id}
    data = api_request("POST", "/users/@me/channels", payload=payload)
    if data:
        return data["id"]
    return None

def send_dm():
    user_id = input(f"{INFO}Enter the user ID to DM: {RESET}").strip()
    channel_id = get_dm_channel(user_id)
    if channel_id:
        content = input(f"{INFO}Enter message content: {RESET}").strip()
        if content:
            payload = {"content": content}
            result = api_request("POST", f"/channels/{channel_id}/messages", payload=payload)
            if result:
                print(f"{SUCCESS}[+] DM sent successfully!{RESET}")
    else:
        print(f"{ERROR}[!] Failed to create DM channel.{RESET}")
    input(f"{INFO}\nPress Enter to continue...{RESET}")

def launch_discord_tools():
    print(f"{WARNING}\n[!] Warning: Using a user account for automation may violate Discord's Terms of Service.{RESET}")
    print(f"{WARNING}    Use only with permission to avoid account bans.{RESET}")
    input(f"{INFO}\nPress Enter to continue...{RESET}")
    while True:
        cl()
        print(f"{HEADER}\n=== Discord Multitool Menu ==={RESET}")
        print(f"{SUCCESS}[1] Scrape Files{RESET}")
        print(f"{SUCCESS}[2] Scrape Friends{RESET}")
        print(f"{SUCCESS}[3] Send Channel Message{RESET}")
        print(f"{SUCCESS}[4] Send DM{RESET}")
        print(f"{SUCCESS}[q] Back to Main Menu{RESET}")
        choice = input(f"{INFO}\nSelect an option > {RESET}").strip().lower()
        if choice == "1":
            cl()
            scrape_files()
        elif choice == "2":
            cl()
            scrape_friends()
        elif choice == "3":
            cl()
            send_message()
        elif choice == "4":
            cl()
            send_dm()
        elif choice == "q":
            print(f"{SUCCESS}\n[+] Returning to main menu...{RESET}")
            return
        else:
            print(f"{ERROR}\n[!] Invalid option. Try again.{RESET}")
            input(f"{INFO}\nPress Enter to continue...{RESET}")