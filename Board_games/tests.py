from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model

from .models import BoardGames, Users, Roles, Comments, GamesCollection


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
        moderator_role = Roles.objects.create(name='Moderator', description='User with additional permissions')
        self.user = Users.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword', role=role)
        self.user1 = Users.objects.create_user(username='testuser1', email='testuser1@example.com',
                                              password='testpassword', role=role)
        self.moderator = Users.objects.create_user(username='testmoderator', email='testmoderator@example.com', password='testpassword', role=moderator_role)
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

    def test_add_game_to_collection_functionality(self):
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

        self.selenium.get(self.live_server_url + 'board_games/1')
        # Dodanie gry do kolekcji
        add_to_collection_button = self.selenium.find_element("name", "add_to_collection")
        add_to_collection_button.click()

        user = Users.objects.filter(username="nowy_uzytkownik")
        game = BoardGames.objects.filter(id=1)

        self.assertTrue(GamesCollection.objects.filter(game=game, user=user).exists())

    def test_add_comment_incorrect_rating_functionality(self):
        # Zaloguj się za pomocą przeglądarki automatycznej
        self.selenium.get(self.live_server_url + '/login/')
        username_input = self.selenium.find_element("name", "username")
        username_input.send_keys("testuser1@example.com")
        password_input = self.selenium.find_element("name", "password")
        password_input.send_keys("testpassword")
        password_input.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 2).until(
            EC.url_changes(self.live_server_url + '/login/')
        )

        self.selenium.get(self.live_server_url + 'board_games/1')

        add_to_collection_button = self.selenium.find_element("name", "add_comment")
        add_to_collection_button.click()

        self.assertIn("/add_comment/", self.selenium.current_url)
        rating = self.selenium.find_element("name", "rating")
        rating.send_keys("-1")
        rating.send_keys(Keys.RETURN)

        self.assertIn("/add_comment/", self.selenium.current_url)

        user = Users.objects.filter(username="testuser1")
        game = BoardGames.objects.filter(id=1)
        self.assertFalse(Comments.objects.filter(game=game, user=user).exist())
        
        self.selenium.get(self.live_server_url + 'board_games/1')

        add_to_collection_button = self.selenium.find_element("name", "add_comment")
        add_to_collection_button.click()

        self.assertIn("/add_comment/", self.selenium.current_url)
        rating = self.selenium.find_element("name", "rating")
        rating.send_keys("11")
        rating.send_keys(Keys.RETURN)

        self.assertIn("/add_comment/", self.selenium.current_url)

        user = Users.objects.filter(username="testuser1")
        game = BoardGames.objects.filter(id=1)
        self.assertFalse(Comments.objects.filter(game=game, user=user).exist())

    def test_add_comment_only_rating_functionality(self):
        # Zaloguj się za pomocą przeglądarki automatycznej
        self.selenium.get(self.live_server_url + '/login/')
        username_input = self.selenium.find_element("name", "username")
        username_input.send_keys("testuser1@example.com")
        password_input = self.selenium.find_element("name", "password")
        password_input.send_keys("testpassword")
        password_input.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 2).until(
            EC.url_changes(self.live_server_url + '/login/')
        )

        self.selenium.get(self.live_server_url + 'board_games/1')

        add_to_collection_button = self.selenium.find_element("name", "add_comment")
        add_to_collection_button.click()

        self.assertIn("/add_comment/", self.selenium.current_url)
        rating = self.selenium.find_element("name", "rating")
        rating.send_keys("0")
        rating.send_keys(Keys.RETURN)

        self.assertIn("/board_games/", self.selenium.current_url)

        user = Users.objects.filter(username="testuser1")
        game = BoardGames.objects.filter(id=1)
        self.assertTrue(Comments.objects.filter(game=game, user=user).exist())
        comment = Comments.objects.get(game=game, user=user)

        self.assertEqual(comment.rating, 0)
        self.assertEqual(comment.comment, "")

    def test_add_comment_rating_and_comment_functionality(self):
        # Zaloguj się za pomocą przeglądarki automatycznej
        self.selenium.get(self.live_server_url + '/login/')
        username_input = self.selenium.find_element("name", "username")
        username_input.send_keys("testuser1@example.com")
        password_input = self.selenium.find_element("name", "password")
        password_input.send_keys("testpassword")
        password_input.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 2).until(
            EC.url_changes(self.live_server_url + '/login/')
        )

        self.selenium.get(self.live_server_url + 'board_games/2')

        add_to_collection_button = self.selenium.find_element("name", "add_comment")
        add_to_collection_button.click()

        self.assertIn("/add_comment/", self.selenium.current_url)
        rating = self.selenium.find_element("name", "rating")
        rating.send_keys("10")
        comment = self.selenium.find_element("name", "comment")
        comment.send_keys("Opinia tekstowa")
        comment.send_keys(Keys.RETURN)

        self.assertIn("/board_games/", self.selenium.current_url)

        user = Users.objects.get(username="testuser1")
        game = BoardGames.objects.get(id=2)
        self.assertTrue(Comments.objects.filter(game=game, user=user).exist())
        comment = Comments.objects.get(game=game, user=user)

        self.assertEqual(comment.rating, 10)
        self.assertEqual(comment.comment, "Opinia tekstowa")

    def test_add_game_functionality(self):
        # Zaloguj się za pomocą przeglądarki automatycznej
        self.selenium.get(self.live_server_url + '/login/')
        username_input = self.selenium.find_element("name", "username")
        username_input.send_keys("testmoderator@example.com")
        password_input = self.selenium.find_element("name", "password")
        password_input.send_keys("testpassword")
        password_input.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 2).until(
            EC.url_changes(self.live_server_url + '/login/')
        )

        self.selenium.get(self.live_server_url + '/add_game/')

        title_input = self.selenium.find_element("name", "title")
        title_input.send_keys("Game 3")

        author_input = self.selenium.find_element("name", "author")
        author_input.send_keys("Author 3")

        publisher_input = self.selenium.find_element("name", "publisher")
        publisher_input.send_keys("Publisher 3")
        publisher_input.send_keys(Keys.RETURN)

        self.assertTrue(BoardGames.objects.filter(title="Game 3").exist())
        game = BoardGames.objects.get(title="Game 3")

        self.assertEqual(game.author, "Author 3")
        self.assertEqual(game.publisher, "Publisher 3")

    def test_remove_comment_functionality(self):
        # Zaloguj się za pomocą przeglądarki automatycznej
        self.selenium.get(self.live_server_url + '/login/')
        username_input = self.selenium.find_element("name", "username")
        username_input.send_keys("testmoderator@example.com")
        password_input = self.selenium.find_element("name", "password")
        password_input.send_keys("testpassword")
        password_input.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 2).until(
            EC.url_changes(self.live_server_url + '/login/')
        )

        self.selenium.get(self.live_server_url + 'board_games/1')

        comment = self.selenium.find_element("username", "testuser")
        comment.click()

        delete_button = self.selenium.find_element("id", "deleteCommentBtn")
        delete_button.click()

        user = Users.objects.get(username="testuser")
        game = BoardGames.objects.get(id=1)
        self.assertFalse(Comments.objects.filter(game=game, user=user).exist())
