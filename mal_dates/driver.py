from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from .env import DEBUG

__all__: list[str] = [
    "create_driver",
]


def create_driver() -> Chrome:
    """Create a functional Chrome driver."""
    chrome_options = Options()

    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if DEBUG:
        chrome_options.add_experimental_option("detach", True)

    driver = Chrome(options=chrome_options)

    return driver
