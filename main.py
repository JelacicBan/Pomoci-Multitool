from src.webhook_sender import run_sender
from src.passwort_gen import pw_gen
from looks.look import display_banner
from src.brute import a
from src.scraper.scraper import launch_discord_tools
from usefull.clear import cl
import sys
import time
import os 
import shutil



def select():
    width = shutil.get_terminal_size().columns

    def center(text):
        return text.center(width)

    print()
    print(center("=" * 60))
    print(center("POMOCI MULTI-TOOLKIT MENU"))
    print(center("=" * 60))
    print()

    print(center("┌────────────────────────────┬────────────────────────────┐"))
    print(center("│      Messaging Tools       │     General Tools          │"))
    print(center("│                            │                            │"))
    print(center("│ [1] Send Webhook           │ [2] Password_Generator     |"))
    print(center("└────────────────────────────┴────────────────────────────┘"))
    print()

    print(center("┌────────────────────────────┬────────────────────────────┐"))
    print(center("│       Offensiv Tools       │     Information Tool       │"))
    print(center("│                            │                            │"))
    print(center("│ [3] Login Bruteforce       │ [4] Scraper                │"))
    print(center("└────────────────────────────┴────────────────────────────┘"))
    print()

    print(center("[0] Exit"))
    print()
    return input(center("Select an option > "))



def main():
    while True:
        display_banner()
        choice = select()

        if choice == "1":
            cl()
            print("\n[+] Starting Webhook Sender...\n")
            time.sleep(1)
            run_sender()

        elif choice == "2":
            cl()
            print("\n[+] Launching Password Generator...\n")
            time.sleep(1)
            pw_gen()

        elif choice == "3":
            cl()
            print("\n[+] Launching Bruteforce Tool... \n")
            time.sleep(1)
            a()

        elif choice == "4":
            cl()
            print("\n[+] Launching Scraping Tool... \n")
            time.sleep(1)
            launch_discord_tools()

        elif choice == "0":
            print("\n[!] Exiting GOATED Toolkit. Goodbye!\n")
            time.sleep(1)
            sys.exit(0)

        else:
            print("\n[!] Invalid selection. Try again.\n")
            time.sleep(1)

# Entry point
if __name__ == "__main__":
    main()
