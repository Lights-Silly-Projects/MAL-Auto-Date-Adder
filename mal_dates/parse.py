import re
from calendar import month_name
from time import sleep
from typing import cast

from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from tqdm import tqdm

from .browse import wait
from .env import DEBUG
from .scrape import get_anime_list

__all__: list[str] = [
    "process_list",

    "get_month_abbr",
    "find_date",
]


def process_list(driver: Chrome, scroll_time: float = 3.0) -> Chrome:
    """Process an individual sublist."""
    list_type = driver.find_element(By.XPATH, f"//a[contains(@class, ' on')]").text

    print(f"Collecting all the shows on your {list_type} list")

    shows = tqdm(get_anime_list(driver, scroll_time))
    action = ActionChains(driver)

    for i, show in enumerate(shows):
        shows.set_description("Finding name")

        driver.execute_script("arguments[0].scrollIntoView(true);", show)
        sleep(0.5)

        title = show.find_element(By.CLASS_NAME, "title")
        name = title.find_element(By.CLASS_NAME, "link").text.strip()

        shows.set_description(f"Processing \"{name}\"")

        ep_count = show.find_elements(By.XPATH, f"//*[starts-with(@class, 'progress-')]")[i]
        ep_count = ep_count.text.replace("\n", "").strip()

        force_no_finished = False

        try:
            total_episodes = int(ep_count)
        except (TypeError, ValueError):
            if x := re.findall(r"([\d-]+)", ep_count):
                try:
                    total_episodes = int(x[-1])
                except (TypeError, ValueError):
                    force_no_finished = True
            else:
                force_no_finished = True

        shows.set_description(f"Processing \"{name}\" (Episode count found: {total_episodes})")

        get_started = not bool(show.find_element(By.CLASS_NAME, "started").text)
        get_finished = not bool(show.find_element(By.CLASS_NAME, "finished").text)

        if force_no_finished:
            get_finished = False

        if not any([get_started, get_finished]):
            continue

        start_dates, finished_dates = (1, 1, 1970), (1, 1, 1970)
        start_changed, finished_changed = False, False

        # Enter the editing page
        shows.set_description(f"Processing \"{name}\" (Accessing quick-edit page)")

        get_y = list(show.find_element(By.CLASS_NAME, 'List_LightBox').location.values())[1]

        driver.execute_script(f"window.scrollTo(0, {get_y - min(int(46 - i / 4), 54)});")

        show.find_element(By.CLASS_NAME, "List_LightBox").click()
        wait(driver, By.ID, "fancybox-outer", 3)

        driver.switch_to.frame("fancybox-frame")

        # Enter the history page
        shows.set_description(f"Processing \"{name}\" (Checking history)")
        wait(driver, By.LINK_TEXT, "History")
        driver.find_element(By.LINK_TEXT, "History").click()

        wait(driver, By.CLASS_NAME, "spaceit_pad")
        watch_dates = driver.find_elements(By.CLASS_NAME, "spaceit_pad")

        shows.set_description(f"Processing \"{name}\" (Checking history ({len(watch_dates)} dates found))")

        watch_dates.reverse()

        if get_started:
            start_dates = find_date(watch_dates[0].text)

        if get_finished:
            for watch_date in watch_dates:
                if not _check_total_episodes_matches(watch_date, total_episodes):
                    continue

                finished_dates = find_date(watch_date.text)
                break

        # Back to the editing page
        shows.set_description(f"Processing \"{name}\" (Editing dates)")
        driver.back()

        driver.switch_to.frame("fancybox-frame")
        wait(driver, By.LINK_TEXT, "History")

        if get_started and start_dates[-1] != 1970:
            driver = _pick_dropdowns(driver, start=True, dates=start_dates)

            start_changed = True

        if get_finished and finished_dates[-1] != 1970:
            driver = _pick_dropdowns(driver, start=False, dates=finished_dates)

            finished_changed = True

        if start_changed or finished_changed:
            driver.find_elements(By.CLASS_NAME, "main_submit")[1].click()

            wait(driver, By.CLASS_NAME, "goodresult")

        shows.set_description(f"Processing \"{name}\" (Done)")

        driver.execute_script(f"el = document.elementFromPoint(0, 0); el.click();")
        # action.move_by_offset(-600, 0)
        action.click().perform()

        driver.switch_to.default_content()

        wait(driver, By.CLASS_NAME, "watching")

    return driver


def _pick_dropdowns(driver: Chrome, start: bool = True, dates: tuple[int, int, int] = (1, 1, 1970)) -> Chrome:
    start_or_finish = "start" if start else "finish"

    month, day, year = dates

    wait(driver, By.ID, f"add_anime_{start_or_finish}_date_month", 3)

    select_m = Select(driver.find_element(By.ID, f"add_anime_{start_or_finish}_date_month"))
    select_m.select_by_value(str(month))

    select_d = Select(driver.find_element(By.ID, f"add_anime_{start_or_finish}_date_day"))
    select_d.select_by_value(str(day))

    select_y = Select(driver.find_element(By.ID, f"add_anime_{start_or_finish}_date_year"))
    select_y.select_by_value(str(year))

    return driver


def _check_total_episodes_matches(element: WebElement, total_episodes: int) -> bool:
    """Check whether the element mentions the total episodes watched anywhere. This helps work around rewatches."""
    ep_num = int(element.text.split(",")[0].split(" ")[-1])

    return ep_num == total_episodes


def get_month_abbr(number: int) -> str:
    """Get the first three letter of a month name based on a given number."""
    try:
        number = int(number)
    except (TypeError, ValueError):
        raise ValueError(f"Could not convert \"{number}\" ({type(number)}) to <type: int>!")

    if not (1 <= number <= 12):
        raise ValueError(f"Number must be between 1–12, not \"{number}\"!")

    return month_name[number][:3]


def find_date(element: str) -> tuple[int, int, int]:
    """Find the start date and return as a tuple of (day, month, year)."""
    matches = re.findall(r"(\d{2})\/(\d{2})\/(\d{4})", str(element))

    if not len(matches) > 0:
        if DEBUG:
            print(element, "\n", matches, "\n")

        raise ValueError("Could not find date!")

    return cast(tuple[int, int, int], tuple([int(x) for x in matches[0]]))
