import requests
from bs4 import BeautifulSoup


LOGIN_URL = 'https://ringzer0team.com/login'


class Parser:
    def __init__(self, challenge_number):
        self.challenge_number = challenge_number
        self.credentials = None
        self.cookie = None
        self.session = requests.session()
        self.url = 'https://ringzer0team.com/challenges/' + str(self.challenge_number) + "/"

    def set_credentials(self, username, password):
        self.credentials = {'username': username, 'password': password}

    # Sets a cookie and adds it to the session's cookiejar
    def set_cookie(self, cookie_value):
        self.cookie = {'PHPSESSID': str(cookie_value)}
        requests.utils.add_dict_to_cookiejar(self.session.cookies, self.cookie)

    # Creates a connection based on the login credentials and auth cookies set
    def connect(self):
        if self.cookie:
            self.session.post(LOGIN_URL, cookies=self.cookie)
        elif self.credentials:
            self.session.post(LOGIN_URL, data=self.credentials)
        else:
            print("No credentials or cookie available!")

    # Retrieves the message field containing the data
    def get_message(self):
        response = self.session.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            return soup.find("div", {"class": "message"}).contents[2].strip()
        except AttributeError:
            exit("Could not find any message field in the response! Something went wrong.")

    def send_solution(self, solution):
        response = self.session.post(self.url + str(solution))
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup.find("div", {"class": "alert alert-info"}).contents[0].strip())
