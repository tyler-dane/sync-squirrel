from selenium.webdriver import Chrome
from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.support.ui import WebDriverWait
from app import util
from app.config import Config
import logging

# fp = webdriver.FirefoxProfile()
# fp.set_preference("browser.download.folderList", 2)
# fp.set_preference("browser.download.manager.showWhenStarting", False)
# fp.set_preference("browser.helperApps.alwaysAsk.force", False)
# fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")


# opts.headless = True
# driver_prefs = Firefox(options=opts, firefox_profile=fp, executable_path='/opt/WebDriver/geckodriver')
# driver = Firefox(options=opts, executable_path='/opt/WebDriver/geckodriver')  # works

opts = FFOptions()
opts.binary_location = Config.WEBDRIVER_PATH

driver = Chrome(executable_path=Config.WEBDRIVER_PATH)

wait = WebDriverWait(driver, 10)
fluent_wait = WebDriverWait(driver, timeout=10, poll_frequency=0.2)

util.create_logger("info", "SyncSquirrel.log")
logger = logging.getLogger()
