import undetected_chromedriver as uc

BOUNTIES_URL = "https://replit.com/bounties?order=creationDateDescending"


driver = uc.Chrome(
    options=uc.ChromeOptions(),
    version_main=133
)

driver.get(BOUNTIES_URL)

print(driver.title)

driver.quit()
