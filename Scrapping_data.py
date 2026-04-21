from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

import time

driver = webdriver.Chrome()
driver.maximize_window()

# Explicit wait
wait = WebDriverWait(driver,20)

# A function to check web page is fully loaded
def wait_for_page_to_load(driver,wait):
    page_title = driver.title
    # wait for webpage to load
    try:
        wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    except:
        print(f"The page \"{page_title}\" did not get fully loaded within the given duration.\n")
    
    else:
        print(f"The page \"{page_title}\" is successfully loaded!\n")
        


url = "https://finance.yahoo.com/"
driver.get(url)
wait_for_page_to_load(driver,wait)

# Declining cookies
try:
    cookie_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="consent-page"]/div/div/div/form/div[2]/div[2]/button[2]')
        )
    )
    cookie_btn.click()

except:
    print("Cookie popup not found.")

actions = ActionChains(driver)

# Hovering on Markets menu
markets_menu = wait.until(EC.presence_of_element_located((By.XPATH,"//div[normalize-space()='Markets']")))
actions.move_to_element(markets_menu).perform()

# Hovering to Stocks inside Market menu
stocks_menu = wait.until(EC.visibility_of_element_located((By.XPATH,'/html[1]/body[1]/div[1]/header[1]/div[1]/nav[1]/ol[1]/li[3]/ol[1]/li[1]/a[1]')))
actions.move_to_element(stocks_menu).perform()

# Hovering to -> Trending Tickers
trending_tickers = wait.until(EC.visibility_of_element_located((By.XPATH,'/html[1]/body[1]/div[1]/header[1]/div[1]/nav[1]/ol[1]/li[3]/ol[1]/li[1]/ol[1]/li[4]/a[1]/span[1]')))
actions.move_to_element(trending_tickers).perform()

# Clicking Trending Tickers
trending_tickers_click = wait.until(EC.element_to_be_clickable((By.XPATH, '/html[1]/body[1]/div[1]/header[1]/div[1]/nav[1]/ol[1]/li[3]/ol[1]/li[1]/ol[1]/li[4]/a[1]')))
trending_tickers_click.click()

wait_for_page_to_load(driver,wait)

# Click on Most Active
most_active = wait.until(EC.element_to_be_clickable((By.XPATH,'/html[1]/body[1]/div[1]/div[4]/main[1]/section[1]/section[1]/section[1]/section[1]/section[1]/div[1]/div[1]/div[1]/a[1]')))
most_active.click()
wait_for_page_to_load(driver,wait)

# scraping the data
data = []
while True:
    # scraping
    wait.until(EC.presence_of_element_located((By.TAG_NAME,"table")))
    rows = driver.find_elements(By.CSS_SELECTOR,"table tbody tr")

    for row in rows:
        values = row.find_elements(By.TAG_NAME,"td")
        stock = {
            "name": values[1].text,
			"symbol": values[0].text,
			"price": values[3].text,
			"change": values[4].text,
			"volume": values[6].text,
			"market_cap": values[8].text,
			"pe_ratio": values[9].text,
        }
        data.append(stock)
        
    

    # click next
    try:
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[4]/main/section/section/section/section/section[1]/div/div[4]/div[3]/button[3]')))
    except:
        print("The \"next button\" is not clickable. We have navigated through all the pages.")
        break
    else:
        next_button.click()
        time.sleep(1)




driver.quit()
