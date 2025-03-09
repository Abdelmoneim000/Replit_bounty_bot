import subprocess
import sys
import os
import platform

def install_requirements():
    """Install the required packages."""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Required packages installed successfully!")

def setup_chrome():
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
            print("Chrome found in /Applications.")
            return True
        print("Warning: Chrome not found in /Applications.")
        print("Please make sure Chrome is installed on your system.")
        return False
    
    elif system == "Linux":
        try:
            subprocess.run(["which", "google-chrome"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Chrome found in PATH.")
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

def setup_env_file():
    """Set up the .env file if it doesn't exist."""
    if not os.path.exists(".env"):
        print("Creating .env file...")
        with open(".env", "w") as f:
            f.write("DISCORD_TOKEN=your_discord_bot_token")
        print(".env file created successfully!")
        print("Please edit the .env file and replace 'your_discord_bot_token' with your actual Discord bot token.")
    else:
        print(".env file already exists.")

def main():
    """Main setup function."""
    print("Setting up Replit Bounty Discord Bot...")
    install_requirements()
    setup_chrome()
    test_scraper()
    setup_env_file()
    print("\nSetup completed successfully!")
    print("\nTo run the bot, use the following command:")
    print("python run.py")

if __name__ == "__main__":
    main() 