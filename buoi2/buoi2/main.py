def greet(name):
    """A simple function to greet someone."""
    print(f"[DEBUG] Entering greet function: name = '{name}'")
    # Introducing a TypeError by adding a string to an integer
    message = f"Hello, {name}!" + 1
    print(f"[DEBUG] Inside greet function: message = '{message}'")
    return message

if __name__ == "__main__":
    print("[INFO] Program starting.")
    greeting = greet("World")
    print(f"[INFO] Greet function returned: greeting = '{greeting}'")
    print("[INFO] Program finished.")