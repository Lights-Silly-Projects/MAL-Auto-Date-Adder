from . import check_env, create_driver, login, process_list, wait, browse_to_sublist


def _main() -> None:
    check_env()

    driver = create_driver()

    # Logging in and getting to the user's Anime List page
    driver = login(driver)

    driver = browse_to_sublist(driver, "watching")
    driver = process_list(driver)

    driver = browse_to_sublist(driver, "completed")
    driver = process_list(driver)

    driver = browse_to_sublist(driver, "onhold")
    driver = process_list(driver)

    driver = browse_to_sublist(driver, "dropped")
    driver = process_list(driver)


if __name__ == "__main__":
    _main()
