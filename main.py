import re
import json
import requests
from bs4 import BeautifulSoup


# Obtains detailed job information from the parent page.
class DetailedJobInformation:
    def __init__(self, url):
        self.url = url
        self.dict_job_details = {
            "title": ""
            , "place": ""
            , "salary": ""
            , "contract_type": ""
            , "contact_email": ""
        }
        try:
            self.page = requests.get(self.url)
        except Exception as error:
            print(error)
        else:
            self.soup = BeautifulSoup(self.page.content, "html.parser")
            self.find_title()
            self.find_place()
            self.find_salary()
            self.find_contract()
            self.find_email()

    # Finds title on the page.
    def find_title(self):
        title = self.soup.find("h1").text
        self.dict_job_details["title"] = title

    # Finds place on the page.
    def find_place(self):
        place = list(self.soup.find("strong", string="Miesto výkonu práce:").parent.stripped_strings)[1]
        self.dict_job_details["place"] = place

    # Finds salary on the page.
    def find_salary(self):
        salary = list(self.soup.find("strong", string="Platové ohodnotenie").parent.stripped_strings)[1].split(",-")
        del salary[-1]
        salary = " ".join(salary).rstrip() + " €"
        self.dict_job_details["salary"] = salary

    # Finds contract type on the page.
    def find_contract(self):
        contract = list(self.soup.find("strong", string="Typ pracového pomeru").parent.stripped_strings)[1]
        self.dict_job_details["contract_type"] = contract

    # FindS contact email on the page.
    def find_email(self):
        pattern = r"\"mailto:(.*)\""
        container_contact = str(self.soup.find("div", {"class": "container position-contact"}))
        email = re.search(pattern, container_contact).groups()[0]
        self.dict_job_details["contact_email"] = email

    # Returns job details.
    def get_job_details(self):
        return self.dict_job_details


# Obtains main page, parse it and save it.
class ParsePage:
    def __init__(self, url="", class_id=""):
        self.url = url
        self.base_url = url.rsplit('/', 2)[0]
        self.class_id = class_id
        self.ls_job_links = []
        self.ls_parsed_job_details = []
        try:
            self.page = requests.get(self.url)
        except Exception as error:
            print(error)
        else:
            self.soup = BeautifulSoup(self.page.content, "html.parser")
            self.id_content = self.soup.find(id=self.class_id)
            self.ls_job_links = [self.base_url + link.get("href") for link in self.id_content.find_all('a')]
            self.parse_job_links()

    # Obtains job details through the job links.
    def parse_job_links(self):
        for link in self.ls_job_links:
            obj_content_page = DetailedJobInformation(link)
            selection_info = obj_content_page.get_job_details()
            self.ls_parsed_job_details.append(selection_info)

    # Saves the job details to the json file.
    def save_json_file(self):
        job_details_json = json.dumps(self.ls_parsed_job_details, indent=2, ensure_ascii=False)
        try:
            with open("job_details.json", "w", encoding="UTF-8") as outfile:
                outfile.write(job_details_json)
        except Exception as error:
            print(error)


if __name__ == '__main__':
    url_hyperia = "https://www.hyperia.sk/kariera/"
    new_page = ParsePage(url=url_hyperia, class_id="positions")
    new_page.save_json_file()
