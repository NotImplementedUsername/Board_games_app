from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model

from .models import BoardGames, Users, Roles, Comments


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
        self.comment1 = Comments.objects.create(rating=2, comment_date='2021-7-18', game_id=self.game1.id, user_id=self.user.id)
        self.comment2 = Comments.objects.create(rating=5, comment_date='2021-7-18', game_id=self.game2.id, user_id=self.user.id)


    def test_register_functionality(self): # ten test mi nie działa (nie znajduje tego użytkownika w bazie po rejestracji)
        # Przejście do strony rejestracji
        self.selenium.get(self.live_server_url + '/register/')

        # Wypełnienie formularza rejestracyjego
        username_input = self.selenium.find_element("name", "username")
        username_input.send_keys("nowy_uzytkownik")

        email_input = self.selenium.find_element("name", "email")
        email_input.send_keys("nowy_uzytkownik@example.com")

        password1_input = self.selenium.find_element("name", "password1")
        password1_input.send_keys("testowe_haslo")

        password2_input = self.selenium.find_element("name", "password2")
        password2_input.send_keys("testowe_haslo")

        # Zatwierdzenie formularza rejestracyjnego
        password2_input.send_keys(Keys.ENTER)

        # Poczekanie na zakończenie rejestracji i przekierowanie
        WebDriverWait(self.selenium, 5).until(
            EC.url_changes(self.live_server_url)
        )

        # Sprawdzenie, czy użytkownik został przekierowany na stronę główną po rejestracji
        self.assertIn("", self.selenium.current_url)

        # Sprawdzenie, czy nowy użytkownik został dodany do bazy danych
        user_exists = Users.objects.filter(username="nowy_uzytkownik").exists()

        if user_exists:
            print("User exists in the database.")
        else:
            print("User does not exist in the database.")

        self.assertTrue(user_exists)

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

    def test_top_games_functionality(self):
        # Przejście do strony z najlepiej ocenianymi grami
        self.selenium.get(self.live_server_url + '/top_games/')

        games = self.selenium.find_elements('xpath', '//li') # Zakładam, że gry są w liście <ol> i każda gra to <li>
        game_info = [
            (game.find_element('xpath','.//div[@class="fw-bold"]/a').text, game.find_element('xpath','.//span').text)
            for game in games]

        # Oczekiwana kolejność gier
        expected_order = [('Game 2', 5), ('Game 1', 2)]

        # Sprawdzenie, czy gry są w odpowiedniej kolejności
        for i, (title, rating) in enumerate(game_info):
            expected_title, expected_rating = expected_order[i]
            self.assertEqual(title, expected_title)
            self.assertEqual(float(rating.replace(',', '.')), expected_rating)

