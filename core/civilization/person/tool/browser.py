import time
from logging import config

import pandas as pd
import pytesseract
from PIL import Image
from selenium import webdriver

URL = "https://www.naver.com"

driver = webdriver.Chrome(executable_path="chromedriver")
driver.get(url=URL)

tessdata_dir_config = r'--tessdata-dir "./tessdata/"'
data = pytesseract.image_to_data(
    Image.open("screenshot.png"), lang="kor", config=tessdata_dir_config
)

df = pd.DataFrame([x.split("\t") for x in data.split("\n")])
df = pd.DataFrame(df.values[1:], headers=df.iloc[0])

print(df)


driver.quit()
print("end...")
