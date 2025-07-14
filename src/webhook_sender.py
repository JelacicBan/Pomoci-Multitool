import requests
import os

def check():
    message_content = input("Welcome to the Webhook sender pls enter your message: ")
    os.system("clear")
    test_message = input(f"{message_content}\nis that correct ? (y/n): ")
    os.system("clear")
    if test_message.lower() == "y":
        webhook = input("Your Webhook: ")
        return message_content, webhook
    else:
        return check()  

def configure(message_content, webhook):
    webhook_url = webhook
    data = {
        'content': message_content,
        'username': 'pomoci'
    }
    return webhook_url, data

def send(webhook_url, data, message_content):
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print(f"--{message_content}-- was send succesfully to the Webhook\n")
    else:
        print(f'Failed to send message: {response.status_code} - {response.text}')

def run_sender():
    message_content, webhook = check()
    webhook_url, data = configure(message_content, webhook)
    send(webhook_url, data, message_content)
    skip = input("Press Enter to continue: ")


