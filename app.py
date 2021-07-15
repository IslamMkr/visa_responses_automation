import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select


class VisaResponse:
    def __init__(self):
        self.bot = webdriver.Firefox()
        self.response_dates = {}
        self.responses_number = 0
        self.waiting_number = 0
        self.resume_file = open("résumé.txt", "w")
        self.resume_file.truncate()
        self.delivered_file = open("dossiers_en_livraison.txt", "w")
        self.delivered_file.truncate()
        self.waiting_file = open("dossiers_en_attente.txt", "w")
        self.waiting_file.truncate()

    def login(self):
        bot = self.bot
        bot.get('https://fastmaildz.com/newfastmail/public/passportstatus')
        time.sleep(5)

    def close_dialog(self):
        dialog_close_button = self.bot.find_element_by_class_name("close")
        dialog_close_button.click()
        time.sleep(2)

    def select_destination(self):
        select = Select(self.bot.find_element_by_id("destination"))
        select.select_by_index(24)

    def search_for_folder(self, folder_number):
        folder_number_field = self.bot.find_element_by_id("grp-changelist-search-dossier")
        folder_number_field.clear()
        folder_number_field.send_keys(folder_number)
        search_button = self.bot.find_element_by_class_name("grp-search-button")
        self.bot.execute_script("arguments[0].click()", search_button)
        time.sleep(1)
        self.retrieve_response(folder_number)

    def retrieve_response(self, folder_number):
        print(folder_number)
        response_status = self.bot.find_element_by_id("instTrait")
        error_note = self.bot.find_element_by_class_name("errornote")
        error_note_text = error_note.text
        response_status_text = response_status.text
        if response_status_text == "En instance de traitement.":
            self.write_on_waiting(folder_number, response_status_text)
        elif response_status_text == "" and error_note_text == "":
            date_of_response = self.bot.find_element_by_class_name("status_date").text
            self.write_on_delivered(folder_number, "En instance de laivraison.", date_of_response)

    def write_on_delivered(self, folder_number, response_status_text, date_of_response):
        if date_of_response in self.response_dates:
            self.response_dates[date_of_response] = self.response_dates[date_of_response] + 1
        else:
            self.response_dates[date_of_response] = 1
        self.responses_number += 1
        self.delivered_file.write("---------------------------------------------\n")
        self.delivered_file.write(f"Dossier : \t{folder_number}\n")
        self.delivered_file.write(f"Status : \t{response_status_text}\n")
        self.delivered_file.write(f"Date de réponse : {date_of_response}\n\n")

    def write_on_waiting(self, folder_number, response_status_text):
        self.waiting_number += 1
        self.waiting_file.write("---------------------------------------------\n")
        self.waiting_file.write(f"Dossier : \t{folder_number}\n")
        self.waiting_file.write(f"Status : \t{response_status_text}\n\n")

    def write_resume(self):
        self.resume_file.write(f"Nombre de dossiers au total : {self.responses_number + self.waiting_number}\n")
        self.resume_file.write(f"Nombre de dossiers traité : {self.responses_number}\n")
        self.resume_file.write(f"Nombre de dossiers en attente : {self.waiting_number}\n\n\n")
        self.resume_file.write(f"Les dates des réponses et leurs nombres : \n")
        for date in self.response_dates.keys():
            self.resume_file.write(f"{date} : {self.response_dates[date]} dossier traité.\n")


visa_response = VisaResponse()
visa_response.login()
visa_response.close_dialog()
visa_response.select_destination()

folder = ""

for number in range(1, 335):
    # Formatting the folder number
    if len(str(number)) == 1:
        folder = "300621/000" + str(number) + "/01"
    elif len(str(number)) == 2:
        folder = "300621/00" + str(number) + "/01"
    else:
        folder = "300621/0" + str(number) + "/01"
    # Searching for the response of the folder number
    # Retrieving the response in a file
    visa_response.search_for_folder(folder)

visa_response.write_resume()
