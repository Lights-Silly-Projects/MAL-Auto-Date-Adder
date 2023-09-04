import os

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from .scrape import wait
from .env import DEBUG

__all__: list[str] = [
    "login",
    "browse_to_sublist"
]


def login(driver: Chrome) -> Chrome:
    """Try to log into MAL and access the user's Anime List page."""
    print("Logging into your MyAnimeList account...")

    driver.get("https://myanimelist.net/login.php?from=%2F")

    try:
        assert "myanimelist" in driver.title.lower()
    except AssertionError:
        exit("You're likely getting rate-limited! Stopping the program for now...")

    try:
        wait(driver, By.CLASS_NAME, "css-47sehv", 4)
        driver.find_element(By.CLASS_NAME, "css-47sehv").click()
    except TimeoutError:
        pass

    # Login.
    driver.find_element(By.ID, "loginUserName").send_keys(os.environ.get("USERNAME"))
    driver.find_element(By.ID, "login-password").send_keys(os.environ.get("PASSWORD"))

    try:
        # Get this annoying button out of the way.
        wait(driver, By.XPATH, "//button[contains(text(),'OK')]", 5.0)
        driver.find_element(By.XPATH, "//button[contains(text(),'OK')]").click()
    except TimeoutError:
        pass

    driver.find_element(By.CLASS_NAME, "btn-form-submit").submit()

    # Logged in, navigate to user's "Currently watching" list.
    wait(driver, By.CLASS_NAME, "header-list")

    return driver


def browse_to_sublist(driver: Chrome, sublist_class: str) -> Chrome:
    sublist_class = sublist_class.lower()

    valid_categories = ["all_anime", "watching", "completed", "onhold", "dropped", "plantowatch"]

    if sublist_class not in valid_categories:
        raise ValueError(f"\"{sublist_class}\" is not a class used by MAL for sub-lists!")

    idx = valid_categories.index(sublist_class)

    if idx == 0:
        idx = 7

    driver.get(f"https://myanimelist.net/animelist/{os.environ.get('USERNAME')}?status={idx}")

    wait(driver, By.CLASS_NAME, sublist_class, 10)

    return driver
