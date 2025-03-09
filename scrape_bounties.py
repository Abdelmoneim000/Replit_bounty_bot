import json
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys

def scrape_replit_bounties(output_file="replit_bounties.json"):
    """Scrape bounty information from Replit's bounty page and save to a JSON file."""
    print("Starting to scrape Replit bounties...")
    
    # URL for Replit bounties
    BOUNTIES_URL = "https://replit.com/bounties?order=creationDateDescending"
    
    # Set up undetected_chromedriver options
    options = uc.ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    
    try:
        # Initialize undetected_chromedriver with specific Chrome version
        driver = uc.Chrome(
            options=options,
            version_main=133  # Specify the major version of Chrome you're using
        )
        
        # Navigate to the bounties page
        print(f"Navigating to {BOUNTIES_URL}...")
        driver.get(BOUNTIES_URL)
        
        # Wait for the page to load
        print("Waiting for page to load...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/main/div/div/div[2]/div[1]/div/div[2]"))
        )
        
        print(f"Page title: {driver.title}")
        
        # Extract bounty information
        bounties = []
        
        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Look for bounty cards using xpath
        parent_element = soup.find('div', {'class': lambda x: x and 'useView_view__C2mnv' in x})
        
        if parent_element:
            # Get all bounty card elements (li elements)
            bounty_elements = parent_element.select("li")
            
            print(f"Found {len(bounty_elements)} bounties")
            
            for element in bounty_elements:
                try:
                    # Extract title using the specific selector
                    title_elem = element.select_one("div > div > h3")
                    title = title_elem.text.strip() if title_elem else ""
                    
                    # Extract amount using the specific selector 
                    amount_elem = element.select_one("div > div > span")
                    amount = amount_elem.text.strip() if amount_elem else ""
                    
                    # Extract description using the specific selector
                    desc_elem = element.select_one("div > div > span:nth-of-type(2)")
                    description = desc_elem.text.strip() if desc_elem else ""
                    
                    if title or description or amount:
                        bounty_info = {
                            "title": title,
                            "description": description,
                            "amount": amount
                        }
                        bounties.append(bounty_info)
                        
                except Exception as e:
                    print(f"Error extracting bounty information: {e}")
                    continue
                    
        # If BeautifulSoup approach failed, try with Selenium
        if not bounties:
            print("Trying alternative approach with Selenium...")
            try:
                # Find the parent element using xpath
                parent = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/main/div/div/div[2]/div[1]/div/div[2]")
                
                # Find all bounty cards
                bounty_cards = parent.find_elements(By.TAG_NAME, "li")
                
                if bounty_cards:
                    print(f"Found {len(bounty_cards)} bounties using Selenium")
                
                for card in bounty_cards:
                    try:
                        # Extract title
                        title_elem = card.find_element(By.CSS_SELECTOR, "div > div > h3")
                        title = title_elem.text.strip() if title_elem else ""
                        
                        # Extract amount
                        amount_elem = card.find_element(By.CSS_SELECTOR, "div > div > span")
                        amount = amount_elem.text.strip() if amount_elem else ""
                        
                        # Extract description
                        desc_elem = card.find_element(By.CSS_SELECTOR, "div > div > span:nth-of-type(2)")
                        description = desc_elem.text.strip() if desc_elem else ""
                        
                        bounty_info = {
                            "title": title,
                            "description": description,
                            "amount": amount
                        }
                        
                        bounties.append(bounty_info)
                    except Exception as e:
                        print(f"Error extracting bounty information: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error with Selenium approach: {e}")
        
        # If we still don't have any bounties, return a message
        if not bounties:
            print("No bounties found. The website structure might have changed.")
            bounties = [{
                "title": "Unable to scrape bounties",
                "description": "The current scraping method is not working. The website structure might have changed.",
                "amount": ""
            }]
        
        # Save bounties to a JSON file
        print(f"Saving {len(bounties)} bounties to {output_file}...")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(bounties, f, indent=4)
        
        print(f"Successfully scraped {len(bounties)} bounties!")
        return True
    except Exception as e:
        print(f"Error with undetected_chromedriver: {e}")
        # Save error information to the JSON file
        error_data = [{
            "title": "Error with undetected_chromedriver",
            "description": f"Error: {str(e)}. Please make sure Chrome is installed on your system.",
            "amount": ""
        }]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(error_data, f, indent=4)
        return False
    finally:
        # Close the browser if it was initialized
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    # Get output file from command line arguments if provided
    output_file = "replit_bounties.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    # Scrape bounties
    success = scrape_replit_bounties(output_file)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1) 