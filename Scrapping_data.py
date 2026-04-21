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
        print(f"The page \"{page_title}\" did not get fully loaded within the given duration.")
    
    else:
        print(f"The page \"{page_title}\" is successfully loaded!")
        # Declining cookies
        wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="consent-page"]/div/div/div/form/div[2]/div[2]/button[2]'))).click()


url = "https://finance.yahoo.com/"
driver.get(url)
wait_for_page_to_load(driver,wait)

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

# Click on Most Active
most_active = wait.until(EC.element_to_be_clickable((By.XPATH,'/html[1]/body[1]/div[1]/div[4]/main[1]/section[1]/section[1]/section[1]/section[1]/section[1]/div[1]/div[1]/div[1]/a[1]')))
most_active.click()
wait_for_page_to_load(driver,wait)


time.sleep(2)
driver.quit()
