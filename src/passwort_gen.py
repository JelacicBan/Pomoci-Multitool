import random
import string

def ask():
    while True:
        try:
            a = int(input("How long should your password be: "))
            if a > 0:
                return a
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")

def one_char():
    z = string.ascii_letters + string.digits + string.punctuation
    return random.choice(z)

def generate(a):
    g = []
    for _ in range(a):
        f = one_char()
        g.append(f)
    return ''.join(g)

def pw_gen():
    a = ask()
    password = generate(a)
    print("Your password is:", password)
    skip = input("Press Enter to continue: ")
    


