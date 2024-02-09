#!/usr/bin/python
# -*- coding: utf-8 -*-
from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems

items = WorkItems()
browser_lib = Selenium()
browser_lib.auto_close = True
items.get_input_work_item()
input_items = items.get_work_item_variables()


class Step2:

    def __init__(self):

        self.url = 'https://nypost.com/'

    def open_website(self):

        try:
            browser_lib.open_available_browser(
                self.url, browser_selection="chrome", maximized=True)
        except Exception as e:
            print(e)
            browser_lib.close_all_browsers()

    def using_input_work_itens(self):

        try:
            browser_lib.click_button_when_visible(
                "css:#masthead > div.site-header__wrapper > div.site-header__container > div.site-header__left > button.site-header__search-toggle")
            browser_lib.input_text_when_element_is_visible(
                "css:#search-input-header", input_items["search_phrase"])
            browser_lib.click_button_when_visible(
                "css:#masthead > div.search.search--header.search--open > form > button")
        except Exception as e:
            print(e)
            browser_lib.close_all_browsers()

        browser_lib.wait_until_element_is_visible(
            "css:#main > div > div.layout.layout--sidebar > div > div.layout__item.layout__item--sidebar.d-none.d-block-lg > div > div > nav > ul:nth-child(5)")

        try:
            current_url = self.url + "search/" + \
                str(input_items["search_phrase"]).replace(" ", "+") + "/"
            browser_lib.set_browser_implicit_wait(0.3)
            browser_lib.go_to(current_url + "?section=" +
                              str.lower(input_items["sections"]))
            browser_lib.click_element_when_clickable(
                "css:#search-results > div > div.search-results__header > div > ul > li.search-results__order.search-results__order--selected > a")
            return str(current_url + "?section=" + str.lower(input_items["sections"]))
        except Exception as e:
            print("aq " + e)

    def work_items_outputs(self):
        url = self.using_input_work_itens()

        output = {
            "news_list": "#search-results > div > div.search-results__stories",
            "current_url": url,
            "n_months": input_items["n_months"],
            "search_phrase": input_items["search_phrase"]
        }

        return output


if __name__ == "__main__":

    robot = Step2()
    robot.open_website()
    input_data = robot.work_items_outputs()
    items.create_output_work_item(input_data, save=True)
