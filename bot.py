import os
import json
import asyncio
import discord
import subprocess
import sys
import time
from discord import app_commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Discord bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Global variables for periodic scraping
periodic_task = None
SCRAPE_INTERVAL = 600  # 10 minutes in seconds
USER_ID = 463124682678206466  # User ID to send DMs to
last_bounty_time = None
last_bounties = []

@tree.command(name="scrape_bounties", description="Scrape bounties from Replit and save to a JSON file")
async def scrape_bounties(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    
    try:
        # Send a message to indicate the process has started
        await interaction.followup.send("Scraping bounties from Replit... This may take a moment.")
        
        # Define the output file
        filename = "replit_bounties.json"
        
        # Run the scrape_bounties.py script as a separate process
        process = await asyncio.create_subprocess_exec(
            sys.executable, "scrape_bounties.py", filename,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for the process to complete
        stdout, stderr = await process.communicate()
        
        # Check if the process was successful
        if process.returncode == 0:
            # Load the JSON file to check if it contains valid data
            with open(filename, "r", encoding="utf-8") as f:
                bounties = json.load(f)
            
            # Send the JSON file to the Discord channel
            await interaction.followup.send(
                f"Successfully scraped {len(bounties)} bounties! Saved to {filename}",
                file=discord.File(filename)
            )
        else:
            # If the process failed, send an error message
            error_message = stderr.decode() if stderr else "Unknown error"
            await interaction.followup.send(f"Failed to scrape bounties: {error_message}")
            
            # Try to send the JSON file if it exists (it might contain error information)
            if os.path.exists(filename):
                await interaction.followup.send(
                    "Here's the error information:",
                    file=discord.File(filename)
                )
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@tree.command(name="activate", description="Activate periodic bounty scraping every 10 minutes")
async def activate(interaction: discord.Interaction):
    global periodic_task
    
    if periodic_task is not None and not periodic_task.cancelled():
        await interaction.response.send_message("Periodic scraping is already active!")
        return
    
    await interaction.response.send_message("Activating periodic bounty scraping every 10 minutes...")
    
    # Start the periodic task
    periodic_task = asyncio.create_task(periodic_scrape(interaction.channel))
    
    # Store initial bounties for comparison
    await update_last_bounties()

@tree.command(name="deactivate", description="Deactivate periodic bounty scraping")
async def deactivate(interaction: discord.Interaction):
    global periodic_task
    
    if periodic_task is None or periodic_task.cancelled():
        await interaction.response.send_message("Periodic scraping is not active!")
        return
    
    # Cancel the periodic task
    periodic_task.cancel()
    periodic_task = None
    
    await interaction.response.send_message("Periodic bounty scraping has been deactivated.")

async def update_last_bounties():
    """Update the last_bounties list with the current bounties."""
    global last_bounties
    
    # Define the output file
    filename = "replit_bounties.json"
    
    # Run the scrape_bounties.py script as a separate process
    process = await asyncio.create_subprocess_exec(
        sys.executable, "scrape_bounties.py", filename,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Wait for the process to complete
    await process.communicate()
    
    # Check if the process was successful
    if process.returncode == 0 and os.path.exists(filename):
        # Load the JSON file
        with open(filename, "r", encoding="utf-8") as f:
            last_bounties = json.load(f)

async def periodic_scrape(channel):
    """Periodically scrape bounties and send new ones."""
    global last_bounties
    
    while True:
        try:
            # Define the output file
            filename = "replit_bounties.json"
            
            # Run the scrape_bounties.py script as a separate process
            process = await asyncio.create_subprocess_exec(
                sys.executable, "scrape_bounties.py", filename,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the process to complete
            await process.communicate()
            
            # Check if the process was successful
            if process.returncode == 0 and os.path.exists(filename):
                # Load the JSON file
                with open(filename, "r", encoding="utf-8") as f:
                    current_bounties = json.load(f)
                
                # Check for new bounties
                if last_bounties and current_bounties:
                    new_bounties = []
                    
                    # Get the time of the latest bounty from the previous scrape
                    last_bounty_time_str = last_bounties[0].get("time", "")
                    
                    # Compare with current bounties to find new ones
                    for bounty in current_bounties:
                        current_bounty_time_str = bounty.get("time", "")
                        
                        # If the current bounty has a newer time than the last known bounty
                        if is_newer_time(current_bounty_time_str, last_bounty_time_str):
                            new_bounties.append(bounty)
                        else:
                            # Once we hit an old bounty, we can stop checking
                            break
                    
                    # Send new bounties
                    if new_bounties:
                        await send_new_bounties(new_bounties, channel)
                
                # Update the last bounties
                last_bounties = current_bounties
        
        except Exception as e:
            print(f"Error in periodic scraping: {e}")
        
        # Wait for the next interval
        await asyncio.sleep(SCRAPE_INTERVAL)

def is_newer_time(current_time_str, last_time_str):
    """
    Compare two time strings to determine if the current time is newer.
    Examples of time strings: "5 minutes ago", "2 hours ago", "just now"
    """
    if not current_time_str or not last_time_str:
        return True
    
    # If they're the same, it's not newer
    if current_time_str == last_time_str:
        return False
    
    # "just now" is always newer than anything else
    if current_time_str.lower() == "just now":
        return True
    if last_time_str.lower() == "just now":
        return False
    
    # Extract the number and unit from the time strings
    current_parts = current_time_str.lower().split()
    last_parts = last_time_str.lower().split()
    
    if len(current_parts) < 3 or len(last_parts) < 3:
        # If we can't parse the time strings, assume it's newer
        return True
    
    try:
        current_value = int(current_parts[0])
        last_value = int(last_parts[0])
        
        current_unit = current_parts[1]
        last_unit = last_parts[1]
        
        # Convert to a common unit (minutes)
        units_to_minutes = {
            "minute": 1,
            "minutes": 1,
            "hour": 60,
            "hours": 60,
            "day": 1440,
            "days": 1440,
            "week": 10080,
            "weeks": 10080,
            "month": 43200,
            "months": 43200,
            "year": 525600,
            "years": 525600
        }
        
        current_minutes = current_value * units_to_minutes.get(current_unit, 0)
        last_minutes = last_value * units_to_minutes.get(last_unit, 0)
        
        # Lower minutes means more recent
        return current_minutes < last_minutes
    except (ValueError, IndexError):
        # If we can't parse the time strings, assume it's newer
        return True

async def send_new_bounties(bounties, channel):
    """Send new bounties to the appropriate destination."""
    # Try to find a channel named "bounties"
    bounties_channel = None
    for guild in client.guilds:
        for ch in guild.text_channels:
            if ch.name.lower() == "bounties":
                bounties_channel = ch
                break
        if bounties_channel:
            break
    
    # Try to get the user for DM
    user = client.get_user(USER_ID)
    
    for bounty in bounties:
        # Create an embed for the bounty
        embed = discord.Embed(
            title=bounty.get("title", "New Bounty"),
            description=bounty.get("description", "No description available"),
            color=discord.Color.green()
        )
        
        # Add fields for additional information
        if "amount" in bounty and bounty["amount"]:
            embed.add_field(name="Amount", value=bounty["amount"], inline=True)
        
        if "time" in bounty and bounty["time"]:
            embed.add_field(name="Posted", value=bounty["time"], inline=True)
        
        # Send to the bounties channel if it exists
        if bounties_channel:
            await bounties_channel.send(embed=embed)
        
        # Send to the user's DM if possible
        if user:
            try:
                await user.send(embed=embed)
            except discord.errors.Forbidden:
                print(f"Cannot send DM to user {USER_ID}")
        
        # If neither option is available, send to the original channel
        if not bounties_channel and not user:
            await channel.send(embed=embed)

@client.event
async def on_ready():
    await tree.sync()
    print(f"{client.user} is now running!")

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("No Discord token found. Please set the DISCORD_TOKEN environment variable.")
    client.run(token) 