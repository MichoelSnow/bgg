import requests
from bs4 import BeautifulSoup

from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
cookies = {}


LOGIN_USERNAME_FIELD = '//*[@id="user_session_email"]'
LOGIN_PASSWORD_FIELD = '//*[@id="user_session_password"]'
LOGIN_BUTTON = '//*[@id="new_user_session"]/fieldset/ol/li[3]/input'


driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.kickstarter.com/login")
login = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, LOGIN_USERNAME_FIELD)))
password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, LOGIN_PASSWORD_FIELD)))

login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, LOGIN_BUTTON)))

login.send_keys(USERNAME)
password.send_keys(PASSWORD)

login_button.click()
sleep(1)
selenium_cookies = driver.get_cookies()
for cookie in selenium_cookies:
    cookies[cookie['name']] = cookie['value']

# driver = webdriver.Chrome(options=chrome_options)
# # driver = webdriver.Chrome()

# selenium_cookies = driver.get_cookies()

# for cookie in selenium_cookies:
#     cookies[cookie['name']] = cookie['value']
# x = 5  

s = requests.Session()
r = s.get("https://www.kickstarter.com/discover/advanced?category_id=12&sort=newest&seed=2770665&page=1")
soup = BeautifulSoup(r.text, 'html.parser')
xcsrf = soup.find("meta", {"name": "csrf-token"})["content"]

query = """
query GetEndedToLive($slug: String!) {
  project(slug: $slug) {
      id
      deadlineAt
      showCtaToLiveProjects
      state
      description
      url
      __typename
  }
}"""

r = s.post("https://www.kickstarter.com/graph",
    headers= {
        "x-csrf-token": xcsrf
    },
    json = {
        "query": query,
        "variables": {
            "slug":"kuhkubus-3d-escher-figures"
        }
    })

print(r.json())