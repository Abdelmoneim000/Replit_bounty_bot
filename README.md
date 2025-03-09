# Replit Bounty Discord Bot

A Discord bot that scrapes bounty information from Replit's bounty page and saves it to a JSON file when triggered by a slash command.

## Features

- Scrapes bounty information from Replit's bounty page
- Saves bounty information to a JSON file
- Uses Discord's slash commands
- Uses undetected_chromedriver to bypass anti-bot detection
- Runs scraping in a separate process to avoid Cloudflare detection
- Periodic scraping every 10 minutes with activate/deactivate commands
- Sends notifications for new bounties to a "bounties" channel or via DM

## Setup

### Automatic Setup

1. Clone this repository
2. Run the setup script:
   ```
   python setup.py
   ```
3. Edit the `.env` file and replace `your_discord_bot_token` with your actual Discord bot token
4. Run the bot:
   ```
   python run.py
   ```

### Manual Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with the following content:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   ```
4. Replace `your_discord_bot_token` with your actual Discord bot token
5. Run the bot:
   ```
   python bot.py
   ```

## Usage

Once the bot is running and added to your server, you can use the following slash commands:

- `/scrape_bounties` - Scrapes bounty information from Replit's bounty page and saves it to a JSON file
- `/activate` - Activates periodic bounty scraping every 10 minutes
- `/deactivate` - Deactivates periodic bounty scraping

## Notifications

The bot will send notifications about new bounties in the following ways:

1. To a channel named "bounties" in your server (if it exists)
2. To the user with ID 463124682678206466 via direct message
3. If neither of the above is available, to the channel where the `/activate` command was used

## How It Works

The bot uses a two-step process to scrape bounties:

1. When you use the `/scrape_bounties` command or when periodic scraping is active, the bot runs a separate Python script (`scrape_bounties.py`) as a subprocess
2. The script uses undetected_chromedriver to bypass Cloudflare's anti-bot protection and scrape the bounty information
3. The script saves the bounty information to a JSON file
4. The bot then sends the JSON file to the Discord channel

For periodic scraping:
1. When you use the `/activate` command, the bot starts a background task that runs every 10 minutes
2. Each time it runs, it compares the newly scraped bounties with the previous ones
3. If new bounties are found (based on the "time" field), it sends notifications
4. Use the `/deactivate` command to stop the periodic scraping

This approach helps bypass Cloudflare's detection mechanisms that might block scraping when done directly from the bot.

## Requirements

- Python 3.8 or higher
- Discord.py
- Requests
- BeautifulSoup4
- python-dotenv
- undetected-chromedriver
- Chrome browser

## Creating a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click on "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under the "TOKEN" section, click "Copy" to copy your bot token
5. Paste this token in your `.env` file
6. Under "Privileged Gateway Intents", enable all intents
7. Go to the "OAuth2" tab, then "URL Generator"
8. Select the "bot" and "applications.commands" scopes
9. Select the "Send Messages" and "Use Slash Commands" bot permissions
10. Copy the generated URL and open it in your browser to add the bot to your server

## Running the Bot

You can run the bot in two ways:

1. Using the run script (recommended):
   ```
   python run.py
   ```
   This script will check if all dependencies are installed and if the `.env` file is properly configured before running the bot.

2. Directly running the bot:
   ```
   python bot.py
   ```

## Troubleshooting

### Common Issues

#### Chrome Not Found

This error occurs when the bot cannot find Chrome installed on your system. To fix this:

1. Make sure Chrome is installed on your system
2. If you're on Windows, make sure Chrome is installed in one of the standard locations:
   - `C:\Program Files\Google\Chrome\Application\chrome.exe`
   - `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`
   - `C:\Users\<username>\AppData\Local\Google\Chrome\Application\chrome.exe`
3. If Chrome is installed in a non-standard location, you may need to add it to your PATH environment variable

#### undetected_chromedriver Issues

If you encounter issues with undetected_chromedriver:

1. Make sure Chrome is installed on your system
2. Try upgrading the undetected-chromedriver package:
   ```
   pip install --upgrade undetected-chromedriver
   ```
3. If you're on Windows, make sure your Chrome installation is in a standard location
4. If you get a version mismatch error, check your Chrome version and update the code to match:
   - Find your Chrome version by navigating to `chrome://settings/help` in Chrome
   - In the `scrape_bounties.py` file, update the `version_main` parameter to match your Chrome version:
     ```python
     driver = uc.Chrome(
         options=options,
         version_main=133  # Replace with your Chrome version
     )
     ```

#### Cloudflare Detection

If you're still getting blocked by Cloudflare:

1. Try running the `scrape_bounties.py` script directly to see if it works:
   ```
   python scrape_bounties.py
   ```
2. If the script works but the bot doesn't, there might be an issue with how the bot is executing the script
3. Try adding more randomization to the script, such as random delays between actions

#### Periodic Scraping Issues

If periodic scraping is not working correctly:

1. Make sure you've used the `/activate` command to start periodic scraping
2. Check if the bot has permission to send messages in the "bounties" channel
3. If you want to receive DMs, make sure you have DMs enabled for the server the bot is in
4. If the bot is not detecting new bounties, check if the time information is being correctly scraped

#### Other Issues

- If the bot is not responding to slash commands, make sure you've invited the bot with the correct permissions
- If the scraping is not working, the website structure might have changed, and the selectors in the code might need to be updated 