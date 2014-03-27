from django.conf import settings

import requests


class Api(object):

    def __init__(self):
        self.base_url = "https://api.trello.com"
        self.token = getattr(settings, "WAITINGLIST_TRELLO_TOKEN", None)
        self.key = getattr(settings, "WAITINGLIST_TRELLO_KEY", None)
        self.org_slug = getattr(settings, "WAITINGLIST_TRELLO_ORG_SLUG", None)
        self.board_short_id = getattr(settings, "WAITINGLIST_TRELLO_BOARD_SHORT_ID", None)
        self.answered_surveys_list_name = getattr(settings, "WAITINGLIST_TRELLO_ANSWERED_SURVEY_LIST_NAME", "Answered Surveys")
        self.imported_contacts_list_name = getattr(settings, "WAITINGLIST_TRELLO_IMPORTED_CONTACTS_LIST_NAME", "Imported Contacts")
        self._answered_surveys_list_id = None
        self._imported_contacts_list_id = None
        self._board_id = None

    @property
    def board_id(self):
        if not self._board_id:
            url = "/1/organizations/{0}?token={1}&key={2}".format(self.org_slug, self.token, self.key)
            org_id = requests.get("{0}{1}".format(self.base_url, url)).json()["id"]
            url = "/1/organizations/{0}/boards/?token={1}&key={2}".format(org_id, self.token, self.key)
            boards = requests.get("{0}{1}".format(self.base_url, url)).json()
            for board in boards:
                if board["shortLink"] == self.board_short_id:
                    self._board_id = board["id"]
                    break
        return self._board_id

    def _get_or_create_list(self, name):
        url = "/1/boards/{0}/lists?token={1}&key={2}".format(self.board_id, self.token, self.key)
        lists = requests.get("{0}{1}".format(self.base_url, url)).json()
        list_id = None
        for lst in lists:
            if lst["name"] == name:
                list_id = lst["id"]
        if list_id is None:
            url = "/1/lists?token={0}&key={1}".format(self.token, self.key)
            list_id = requests.post("{0}{1}".format(self.base_url, url), data={
                "name": name,
                "idBoard": self.board_id
            }).json()["id"]
        return list_id

    @property
    def answered_surveys_list_id(self):
        if not self._answered_surveys_list_id:
            self._answered_surveys_list_id = self._get_or_create_list(self.answered_surveys_list_name)
        return self._answered_surveys_list_id

    @property
    def imported_contacts_list_id(self):
        if not self._imported_contacts_list_id:
            self._imported_contacts_list_id = self._get_or_create_list(self.imported_contacts_list_name)
        return self._imported_contacts_list_id

    def create_card(self, title, description, list_id):
        url = "/1/cards?token={0}&key={1}".format(self.token, self.key)
        return requests.post("{0}{1}".format(self.base_url, url), data={"name": title, "desc": description, "idList": list_id}).json()

    def delete_card(self, card_id):
        url = "/1/cards/{2}?token={0}&key={1}".format(self.token, self.key, card_id)
        return requests.delete("{0}{1}".format(self.base_url, url))
