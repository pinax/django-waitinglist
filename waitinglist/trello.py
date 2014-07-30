from django.conf import settings

import requests


class Api(object):

    def __init__(self):
        self.base_url = "https://api.trello.com"
        self.token = getattr(settings, "WAITINGLIST_TRELLO_TOKEN", None)
        self.key = getattr(settings, "WAITINGLIST_TRELLO_KEY", None)
        self.org_slug = getattr(settings, "WAITINGLIST_TRELLO_ORG_SLUG", None)
        self.board_short_id = getattr(settings, "WAITINGLIST_TRELLO_BOARD_SHORT_ID", None)
        self.answered_surveys_list_name = getattr(settings,
                                                  "WAITINGLIST_TRELLO_ANSWERED_SURVEY_LIST_NAME",
                                                  "Answered Surveys")
        self.imported_contacts_list_name = getattr(settings,
                                                   "WAITINGLIST_TRELLO_IMPORTED_CONTACTS_LIST_NAME",
                                                   "Imported Contacts")
        self.imported_answers_list_name = getattr(settings,
                                                  "WAITINGLIST_TRELLO_IMPORTED_ANSWERS_LIST_NAME",
                                                  "Imported Answered")
        self.to_contact_list_name = getattr(settings, "WAITINGLIST_TRELLO_TO_CONTACT_LIST_NAME",
                                            "To Contact")
        self.contacted_list_name = getattr(settings, "WAITINGLIST_TRELLO_CONTACTED_LIST_NAME",
                                           "Contacted")
        self._answered_surveys_list_id = None
        self._imported_contacts_list_id = None
        self._to_contact_list_id = None
        self._contacted_list_id = None
        self._board_id = None
        self._org_id = None

    @property
    def org_id(self):
        if not self._org_id:
            url = "/1/organizations/{0}?token={1}&key={2}".format(self.org_slug, self.token,
                                                                  self.key)
            print url
            r = requests.get("{0}{1}".format(self.base_url, url))
            print r.status_code
            self._org_id = requests.get("{0}{1}".format(self.base_url, url)).json()["id"]
        return self._org_id

    @property
    def board_id(self):
        if not self._board_id:
            url = "/1/organizations/{0}/boards/?token={1}&key={2}".format(self.org_id, self.token,
                                                                          self.key)
            boards = requests.get("{0}{1}".format(self.base_url, url)).json()
            for board in boards:
                if board["shortLink"] == self.board_short_id:
                    self._board_id = board["id"]
                    break
        return self._board_id

    def lists(self, board_id):
        url = "/1/boards/{0}/lists?token={1}&key={2}".format(self.board_id, self.token, self.key)
        return requests.get("{0}{1}".format(self.base_url, url)).json()

    def create_list(self, name, board_id):
        url = "/1/lists?token={0}&key={1}".format(self.token, self.key)
        return requests.post("{0}{1}".format(self.base_url, url), data={
            "name": name,
            "idBoard": board_id
        }).json()

    def card_short_url(self, card_id):
        url = "/1/cards/{0}/shortUrl?token={1}&key={2}".format(card_id, self.token, self.key)
        return requests.get("{0}{1}".format(self.base_url, url)).json()["_value"]

    def _get_or_create_list(self, name):
        list_id = None
        for lst in self.lists(self.board_id):
            if lst["name"] == name:
                list_id = lst["id"]
        if list_id is None:
            list_id = self.create_list(name, self.board_id)["id"]
        return list_id

    @property
    def to_contact_list_id(self):
        if not self._to_contact_list_id:
            self._to_contact_list_id = self._get_or_create_list(self.to_contact_list_name)
        return self._to_contact_list_id

    @property
    def contacted_list_id(self):
        if not self._contacted_list_id:
            self._contacted_list_id = self._get_or_create_list(self.contacted_list_name)
        return self._contacted_list_id

    @property
    def answered_surveys_list_id(self):
        if not self._answered_surveys_list_id:
            self._answered_surveys_list_id = self._get_or_create_list(
                self.answered_surveys_list_name)
        return self._answered_surveys_list_id

    @property
    def imported_contacts_list_id(self):
        if not self._imported_contacts_list_id:
            self._imported_contacts_list_id = self._get_or_create_list(
                self.imported_contacts_list_name)
        return self._imported_contacts_list_id

    def cards(self, list_id):
        url = "/1/lists/{0}/cards?token={1}&key={2}".format(list_id, self.token, self.key)
        return requests.get("{0}{1}".format(self.base_url, url)).json()

    def move_card(self, card_id, list_id):
        url = "/1/card/{0}/idList?token={1}&key={2}".format(card_id, self.token, self.key)
        return requests.put("{0}{1}".format(self.base_url, url), data={"value": list_id})

    def create_card(self, title, description, list_id):
        url = "/1/cards?token={0}&key={1}".format(self.token, self.key)
        return requests.post("{0}{1}".format(self.base_url, url),
                             data={"name": title, "desc": description, "idList": list_id}).json()

    def delete_card(self, card_id):
        url = "/1/cards/{2}?token={0}&key={1}".format(self.token, self.key, card_id)
        return requests.delete("{0}{1}".format(self.base_url, url))

    def setup_board(self, name):
        url = "/1/boards/?token={0}&key={1}".format(self.token, self.key)
        board_data = requests.post("{0}{1}".format(self.base_url, url), data={
            "name": name.encode("utf-8"),
            "prefs_permissionLevel": "org",
            "prefs_selfJoin": "true",
            "idOrganization": self.org_id
        }).json()
        return self.create_list(self.imported_answers_list_name, board_data["id"])["id"]
