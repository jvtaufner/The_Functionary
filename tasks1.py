from RPA.Robocorp.WorkItems import WorkItems
import random

items = WorkItems(autoload=True)


class Step1:
    def __init__(self):
        items.get_input_work_item()
        self.input_items = items.get_work_item_variables()

    def setting_scraping_inputs(self):
        sections = random.choice(self.input_items["sections"])
        search_phrase = random.choice(self.input_items["search_phrase"])
        n_months = random.randint(0, 3)

        scraping_data_dict = {
            "sections": sections,
            "search_phrase": search_phrase,
            "n_months": n_months
        }
        return scraping_data_dict


if __name__ == "__main__":

    robot = Step1()
    input_data = robot.setting_scraping_inputs()
    items.create_output_work_item(input_data, save=True)
