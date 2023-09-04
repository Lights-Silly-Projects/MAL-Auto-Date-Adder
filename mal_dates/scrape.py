from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

__all__: list[str] = [
    "wait",
    "exists_by_xpath",
    "get_anime_list",
]


def wait(driver: Chrome, element: By | str = By.ID, value: str = "", timeout: float = 10.0) -> None:
    """Wait for n seconds until the element with the given value is available."""
    try:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((element, value)))  # type:ignore[arg-type]
    except:
        # if DEBUG:
        #     print(driver.page_source)

        raise TimeoutError(
            f"Timeout expired @ \"{driver.current_url}\"\nwhile searching for \"{element}\" elements "
            f"matching the value \"{value}\"!"
        )


def exists_by_xpath(driver: Chrome, value: str = ""):
    """Check if an XPATH element exists."""
    try:
        driver.find_element(By.XPATH, value)
    except NoSuchElementException:
        return False

    return True


def get_anime_list(driver: Chrome, scroll_time: float = 5.0) -> list[WebElement]:
    """Get every anime on the current page's list."""
    last_scroll_pos = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

        sleep(scroll_time)

        if (current_scroll_pos := driver.execute_script("return document.body.scrollHeight")) == last_scroll_pos:
            print("Finished scrolling!")
            break

        print(f"Current scroll position: {current_scroll_pos}")

        last_scroll_pos = current_scroll_pos

    driver.execute_script("window.scrollTo(0, 0);")

    return driver.find_elements(By.CLASS_NAME, "list-item")
