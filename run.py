import os
import sys
import subprocess
import platform

def check_env_file():
    """Check if the .env file exists and has a valid token."""
    if not os.path.exists(".env"):
        print("Error: .env file not found.")
        print("Please run 'python setup.py' to create the .env file.")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
    
    if "DISCORD_TOKEN=your_discord_bot_token" in content:
        print("Error: You need to set your Discord bot token in the .env file.")
        print("Please edit the .env file and replace 'your_discord_bot_token' with your actual Discord bot token.")
        return False
    
    if "DISCORD_TOKEN=" not in content:
        print("Error: DISCORD_TOKEN not found in .env file.")
        print("Please make sure your .env file contains the DISCORD_TOKEN variable.")
        return False
    
    return True

def check_dependencies():
    """Check if all dependencies are installed."""
    try:
        import discord
        import json
        import bs4
        import dotenv
        import undetected_chromedriver
        return True
    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Please run 'python setup.py' to install all dependencies.")
        return False

def check_chrome_installation():
    """Check if Chrome is installed on the system."""
    system = platform.system()
    
    if system == "Windows":
        # Common Chrome installation paths on Windows
        chrome_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Google\\Chrome\\Application\\chrome.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Google\\Chrome\\Application\\chrome.exe'),
            os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\' + os.getlogin() + '\\AppData\\Local'), 'Google\\Chrome\\Application\\chrome.exe')
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"Chrome found at: {path}")
                return True
        
        print("Warning: Chrome not found in common installation paths.")
        print("Please make sure Chrome is installed on your system.")
        print("You can download Chrome from: https://www.google.com/chrome/")
        return False
    
    elif system == "Darwin":  # macOS
        if os.path.exists("/Applications/Google Chrome.app"):
            return True
        print("Warning: Chrome not found in /Applications.")
        print("Please make sure Chrome is installed on your system.")
        return False
    
    elif system == "Linux":
        try:
            subprocess.run(["which", "google-chrome"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            print("Warning: Chrome not found in PATH.")
            print("Please make sure Chrome is installed on your system.")
            return False
    
    return True  # Default to True for other systems

def test_scraper():
    """Test if the scraper script works properly."""
    try:
        print("Testing scraper script...")
        # Run the scraper script with a test output file
        result = subprocess.run(
            [sys.executable, "scrape_bounties.py", "test_bounties.json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Scraper script is working properly!")
            # Clean up the test file
            if os.path.exists("test_bounties.json"):
                os.remove("test_bounties.json")
            return True
        else:
            print(f"Error testing scraper script: {result.stderr}")
            print("\nTroubleshooting tips:")
            print("1. Make sure you have Chrome browser installed")
            print("2. Try running: pip install --upgrade undetected-chromedriver")
            print("3. If you're on Windows, make sure your Chrome installation is in a standard location")
            return False
    except Exception as e:
        print(f"Error testing scraper script: {e}")
        return False

def run_bot():
    """Run the Discord bot."""
    try:
        subprocess.run([sys.executable, "bot.py"])
    except Exception as e:
        print(f"Error running the bot: {e}")

def main():
    """Main function to run the bot."""
    print("Starting Replit Bounty Discord Bot...")
    
    # Check if the .env file exists and has a valid token
    if not check_env_file():
        return
    
    # Check if all dependencies are installed
    if not check_dependencies():
        return
    
    # Check if Chrome is installed
    check_chrome_installation()
    
    # Test if the scraper script works properly
    test_scraper()
    
    # Run the bot
    run_bot()

if __name__ == "__main__":
    main() 