from RPA.Robocorp.WorkItems import WorkItems
from RPA.Browser.Selenium import Selenium
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import os
from robocorp import log
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
from PIL import Image as PILImage


items = WorkItems(autoload=True)
browser_lib = Selenium()
browser_lib.auto_close = True


items.get_input_work_item()
input_items = items.get_work_item_variables()


class Step3():
    def __init__(self):
        self.url = input_items["current_url"]
        self.main_list_selector = input_items["news_list"]
        self.months = input_items["n_months"]
        self.search_phrase = input_items["search_phrase"]
        self.workbook = Workbook()

    def open_website(self):
        try:

            browser_lib.open_available_browser(
                self.url, browser_selection="chrome", maximized=True)
        except Exception as e:
            log.info("Couldn't open Browser:" + e)
            browser_lib.close_all_browsers()

    def is_date_within_interval(self, text):
        current_time = datetime.now()
        oldest_time = 0
        if self.months == 0:
            oldest_time = 1
        else:
            oldest_time = self.months
        correct_oldest_month = current_time - relativedelta(months=oldest_time)
        date_pattern = r"(\w+\s\d{1,2},\s\d{4})"
        match = re.search(date_pattern, text)
        if match:
            matched_date_str = match.group(1)
            parsed_date = datetime.strptime(matched_date_str, "%B %d, %Y")
            return (bool(correct_oldest_month <= parsed_date <= current_time),
                    parsed_date)
        else:
            return (False, [])

    def count_search_phrase_occurrences(self, search_phrase, text):

        pattern = re.compile(r'\b{}\b'.format(re.escape(search_phrase)))
        matches = re.findall(pattern, text)

        return len(matches)

    def contains_money(self, title, description):

        money_pattern = r'\$[\d,.]+|\d+\s*(?:dollars|USD)'

        return bool(re.search(money_pattern, title) or
                    re.search(money_pattern, description))

    def insert_images_to_excel(self):
        current_folder = os.getcwd()
        image_folder = os.path.join(current_folder, 'output')
        worksheet = self.workbook.active
        image_files = sorted([file for file in os.listdir(image_folder) if file.endswith('.png')])

        for i, image_file in enumerate(image_files, start=2):
            image_path = os.path.join(image_folder, image_file)
            img = PILImage.open(image_path)
            img_obj = ExcelImage(img)
            img_obj.anchor = f'H{i}'
            worksheet.add_image(img_obj)
            worksheet.row_dimensions[i].height = img.height
        self.workbook.save("output.xlsx")

    def iterate_through_news(self):

        news_items = browser_lib.find_elements("css:.story__text")
        images = browser_lib.find_elements(
            "css:div.story__image.story__image--floated > a > img")
        counter = 0
        titles = []
        dates = []
        descriptions = []
        picture_filename = []
        count_of_search_phrase_in_title = []
        count_of_search_phrase_in_description = []
        contains_money_reference = []
        read_page = 1

        while (read_page):

            for news, image in zip(news_items, images):
                texts = browser_lib.get_text(news)
                text_splitted = texts.split('\n')
                date_of_interest = (self.is_date_within_interval
                                    (text_splitted[1])[0],
                                    self.is_date_within_interval
                                    (text_splitted[1])[1])

                if (date_of_interest[0]):
                    titles.append(text_splitted[0])
                    dates.append(date_of_interest[1].strftime("%B %d, %Y"))
                    descriptions.append(text_splitted[2])
                    picture_filename.append(
                        browser_lib.get_element_attribute(image, "src"))
                    browser_lib.scroll_element_into_view(image)
                    browser_lib.capture_element_screenshot(
                        image, "output/screenshot{input}.png"
                        .format(input=counter))
                    count_of_search_phrase_in_title.append(
                        self.count_search_phrase_occurrences
                        (self.search_phrase, text_splitted[0]))
                    count_of_search_phrase_in_description.append(
                        self.count_search_phrase_occurrences
                        (self.search_phrase, text_splitted[2]))
                    contains_money_reference.append(
                        self.contains_money
                        (text_splitted[0], text_splitted[2]))
                    counter += 1
            if len(titles) == 0:
                log.info("There are no news in this section regarding the inputted search phrase.")
                browser_lib.close_all_browsers()

            if len(titles) % 20 == 0 and len(titles) != 0:
                browser_lib.set_browser_implicit_wait(0.3)
                browser_lib.click_link(
                    "css:#search-results > div > div.search-results__more > a")
            else:
                read_page = 0

            full_list = [titles, dates, descriptions, picture_filename,
                         count_of_search_phrase_in_title,
                         count_of_search_phrase_in_description,
                         contains_money_reference]

            full_list_transposed = list(zip(*full_list))

            worksheet = self.workbook.active
            headers = ['Title', 'Date', 'Description', 'Picture Source',
                       'Count of Search Phrase in Title',
                                'Count of Search Phrase in Description',
                                'Contains Money Reference', 'Image']

            worksheet.append(headers)
            for row_data in full_list_transposed:
                worksheet.append(row_data)
            self.insert_images_to_excel()


if __name__ == "__main__":

    robot = Step3()
    robot.open_website()
    robot.iterate_through_news()
    items.create_output_work_item(files="output.xlsx", save=True)
