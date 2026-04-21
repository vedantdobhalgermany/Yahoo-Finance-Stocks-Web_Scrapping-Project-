import pandas as pd
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

class StocksScrapper:
    def __init__(self,driver,timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(self.driver,timeout=timeout)
        self.data = []

    def wait_for_page_to_load(self):
        page_title = self.driver.title
        # wait for webpage to load 
        try:
            self.wait.until(
                lambda d: d.execute_script("return document.readyState") == "complete"
                )
        except:
            print(f"The page \"{page_title}\" did not get fully loaded within the given duration.\n")
        else:
            print(f"The page \"{page_title}\" is successfully loaded!\n")
        

    def cookie(self):
        # Declining cookies
        try:
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="consent-page"]/div/div/div/form/div[2]/div[2]/button[2]')
                    )
                    )
            cookie_btn.click()
        except:
            print("Cookie popup not found.")


    def access_main_url(self,url):
        self.driver.get(url)
        self.wait_for_page_to_load()
        

    def access_most_active_stocks(self):
        actions = ActionChains(self.driver)
        # Hovering on Markets menu
        markets_menu = self.wait.until(EC.presence_of_element_located((By.XPATH,"//div[normalize-space()='Markets']")))
        actions.move_to_element(markets_menu).perform()

        # Hovering to Stocks inside Market menu
        stocks_menu = self.wait.until(EC.visibility_of_element_located((By.XPATH,'/html[1]/body[1]/div[1]/header[1]/div[1]/nav[1]/ol[1]/li[3]/ol[1]/li[1]/a[1]')))
        actions.move_to_element(stocks_menu).perform()

        # Hovering to -> Trending Tickers
        trending_tickers = self.wait.until(EC.visibility_of_element_located((By.XPATH,'/html[1]/body[1]/div[1]/header[1]/div[1]/nav[1]/ol[1]/li[3]/ol[1]/li[1]/ol[1]/li[4]/a[1]/span[1]')))
        actions.move_to_element(trending_tickers).perform()

        # Clicking Trending Tickers
        trending_tickers_click = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html[1]/body[1]/div[1]/header[1]/div[1]/nav[1]/ol[1]/li[3]/ol[1]/li[1]/ol[1]/li[4]/a[1]')))
        trending_tickers_click.click()

        self.wait_for_page_to_load()

        # Click on Most Active
        most_active = self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html[1]/body[1]/div[1]/div[4]/main[1]/section[1]/section[1]/section[1]/section[1]/section[1]/div[1]/div[1]/div[1]/a[1]')))
        most_active.click()
        self.wait_for_page_to_load()


    def extract_stocks_data(self):
        # scraping the data
        while True:
            # scraping
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME,"table")))
            rows = self.driver.find_elements(By.CSS_SELECTOR,"table tbody tr")
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
            self.data.append(stock)
        
            # click next
            try:
                next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[4]/main/section/section/section/section/section[1]/div/div[4]/div[3]/button[3]')))
            except:
                print("The \"next button\" is not clickable. We have navigated through all the pages.")
                break
            else:
                next_button.click()
                time.sleep(1)

    def clean_and_save_data(self,filename="temp"):
        stocks_df = (
            pd
            .DataFrame(self.data)
            # Strip spaces from text columns
            .apply(
                lambda col: col.str.strip()
                if col.dtype == "object"
                else col
                )
            .assign(
                # Price
                price=lambda df_:
                pd.to_numeric(
                    df_.price,
                    errors="coerce"
                    ),
                # Change
                change=lambda df_:
                pd.to_numeric(
                    df_.change
                    .replace(["-", "--", "N/A"], np.nan)
                    .str.replace("+", "", regex=False),
                    errors="coerce"
                    ),
                    
                # Volume (assumes M values)
                volume=lambda df_:
                pd.to_numeric(
                    df_.volume
                    .replace(["-", "--", "N/A"], np.nan)
                    .str.replace("M", "", regex=False),
                    errors="coerce"
                    ),

                # Market cap -> convert all to Billions
                market_cap=lambda df_:
                df_.market_cap.apply(
                    lambda val:
                    np.nan if pd.isna(val) or val in ["-", "--", "N/A"] else
                    float(val.replace("M", ""))/1000 if "M" in val else
                    float(val.replace("B", "")) if "B" in val else
                    float(val.replace("T", ""))*1000 if "T" in val else
                    np.nan
                    ),

                # P/E ratio
                pe_ratio=lambda df_:
                  pd.to_numeric(
                      df_.pe_ratio
                      .replace(["-", "--", "N/A"], np.nan)
                      .str.replace(",", "", regex=False),
                      errors="coerce"
                      )
                    )
                    .rename(columns={
                        "price": "price_usd",
                        "volume": "volume_M",
                        "market_cap": "market_cap_B"
                        })
                        )

        stocks_df.to_csv(f"{filename}.csv",index=False)
        stocks_df.to_excel(f"{filename}.xlsx", index=False)


if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.maximize_window()

    url = "https://finance.yahoo.com/"
    scraper = StocksScrapper(driver,10)

    scraper.access_main_url(url)
    scraper.cookie()
    scraper.access_most_active_stocks()
    scraper.extract_stocks_data()
    scraper.clean_and_save_data("yahoo-finance-stocks")

    driver.quit()