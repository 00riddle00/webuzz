import re
import threading
import time
import unittest
from selenium import webdriver
from app import create_app, db, fake
from app.models import Role, User, Post


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # start Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        try:
            cls.client = webdriver.Chrome(chrome_options=options)
        except:
            pass

        # skip these tests if the browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app("testing")
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # suppress logging to keep unittest output clean
            import logging

            logger = logging.getLogger("werkzeug")
            logger.setLevel("ERROR")

            # create the database and populate with some fake data
            db.create_all()
            Role.insert_roles()
            fake.users(10)
            fake.posts(10)

            # add an administrator user
            admin_role = Role.query.filter_by(name="Administrator").first()
            admin = User(
                email="flask.4dmin@yahoo.com",
                username="4dministrator",
                password="admin",
                role=admin_role,
                confirmed=True,
            )
            db.session.add(admin)
            db.session.commit()

            # start the Flask server in a thread
            cls.server_thread = threading.Thread(
                target=cls.app.run, kwargs={"debug": False}
            )
            cls.server_thread.start()

            # give the server a second to ensure it is up
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop the flask server and the browser
            cls.client.get("http://localhost:5000/shutdown")
            cls.client.quit()
            cls.server_thread.join()

            # destroy database
            db.drop_all()
            db.session.remove()

            # remove application context
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest("Web browser not available")

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        # navigate to home page
        self.client.get("http://localhost:5000/")
        self.assertTrue(
            re.search("Hello,\s+Stranger!", self.client.page_source)
        )

        # navigate to login page
        self.client.find_element("xpath", "//a[contains(text(), 'Log in')]").click()
        self.assertIn("<h1>Login</h1>", self.client.page_source)

        # login
        self.client.find_element("name", "email").send_keys("flask.4dmin@yahoo.com")
        self.client.find_element("name", "password").send_keys("admin")
        self.client.find_element("name", "submit").click()
        self.assertTrue(re.search("Hello,\s+4dministrator!", self.client.page_source))

        # navigate to the user's profile page
        self.client.find_element("xpath", "//a[contains(text(), 'Profile')]").click()
        self.assertIn("<h1>4dministrator</h1>", self.client.page_source)
