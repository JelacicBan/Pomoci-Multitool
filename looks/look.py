import colorama
from colorama import Fore, Style
import os
import shutil
import time

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)

def display_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    width = max(shutil.get_terminal_size().columns, 60)  # Ensure minimum width for small terminals
    red = Fore.RED + Style.BRIGHT
    white = Fore.WHITE + Style.BRIGHT
    dim = Fore.RED + Style.DIM
    green = Fore.GREEN + Style.BRIGHT
    reset = Style.RESET_ALL

    banner = [
        f"{red}                                                               ",
        f"{red}::::::::::.    ...     .        :       ...       .,-:::::  :::",
        f"{red} `;;;```.;;;.;;;;;;;.  ;;,.    ;;;   .;;;;;;;.  ,;;;'````'  ;;;",
        f"{red}  `]]nnn]]',[[     \\[[,[[[[, ,[[[[, ,[[     \\[[,[[[         [[[",
        f"{red}   $$$\"\"   $$$,     $$$$$$$$$$$\"$$$ $$$,     $$$$$$         $$$",
        f"{red}   888o    \"888,_ _,88P888 Y88\" 888o\"888,_ _,88P`88bo,__,o, 888",
        f"{red}   YMMMb     \"YMMMMMP\" MMM  M'  \"MMM  \"YMMMMMP\"   \"YUMMMMMP\"MMM",
        "",
        f"{dim}────────────────────────────────────────────────────────────",
        f"{white}:: POMOCI MULTI-TOOLKIT ::     {red}RED PROTOCOL ENGAGED",
        f"{dim}────────────────────────────────────────────────────────────{reset}",
        f"{red}[+] Core Modules        {green}ONLINE",
        f"{red}[+] Matrix Interface    {green}ACTIVE",
        f"{red}[+] Breach Protocols    {green}READY",
    ]

    for line in banner:
        print(line.center(width))
        time.sleep(0.03)  # Subtle delay for smooth display
