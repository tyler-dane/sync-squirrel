from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from app import util
from app.config import Config
import logging

opts = Options()
opts.headless = Config.WEBDRIVER_HEADLESS
opts.add_experimental_option("prefs", {
  "download.default_directory": f"{Config.DOWNLOADS_DIR}",
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True
})


driver = Chrome(executable_path=Config.WEBDRIVER_PATH,
                options=opts)

wait = WebDriverWait(driver, 10)
fluent_wait = WebDriverWait(driver, timeout=10, poll_frequency=0.2)

util.create_logger("info", "SyncSquirrel.log")
logger = logging.getLogger()
