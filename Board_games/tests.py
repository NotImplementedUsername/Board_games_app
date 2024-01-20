from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .models import BoardGames, Users, Roles


class FunctionalTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Przygotuj dane testowe
        role = Roles.objects.create(name='Standard User', description='Standard user role')
        self.user = Users.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword', role=role)
        self.game1 = BoardGames.objects.create(title='Game 1', author='Author 1', publisher='Publisher 1')
        self.game2 = BoardGames.objects.create(title='Game 2', author='Author 2', publisher='Publisher 2')

    def test_login_functionality(self):
        # Zaloguj się za pomocą przeglądarki automatycznej
        self.selenium.get(self.live_server_url + '/login/')
        username_input = self.selenium.find_element("name", "username")
        username_input.send_keys("testuser@example.com")
        password_input = self.selenium.find_element("name", "password")
        password_input.send_keys("testpassword")
        password_input.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 2).until(
            EC.url_changes(self.live_server_url + '/login/')
        )

        # Sprawdź, czy zalogowano pomyślnie (czy zmieniono strone)
        self.assertNotIn("/login/", self.selenium.current_url)

    def test_search_game_functionality(self):
        # Wyszukaj grę
        self.selenium.get(self.live_server_url)
        search_input = self.selenium.find_element("name", "search_phrase")
        search_input.send_keys("Game 1")
        search_input.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located(("xpath", "//a[contains(text(), 'Game 1')]"))
        )

        # Sprawdź, czy wyniki zawierają tylko oczekiwaną grę
        self.assertIn("Game 1", self.selenium.page_source)
        self.assertNotIn("Game 2", self.selenium.page_source)
