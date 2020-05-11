import os
import unittest
import app


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()

    # No route for "/"
    def test_index(self):
        response = self.app.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 404)

    def test_database(self):
        tester = os.path.exists(
            "C:/ProgramData/MySQL/MySQL Server 8.0/Data/flaskr")
        self.assertTrue(tester)


class TestLogin(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()

    def login(self, username, password):
        """Login helper function"""
        return self.app.post('/pythonlogin', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """Logout helper function."""
        return self.app.get('/pythonlogin/logout', follow_redirects=True)

    def register(self, username, password, email):
        """Login helper function"""
        return self.app.post('/pythonlogin/register', data=dict(
            username=username,
            password=password,
            email=email
        ), follow_redirects=True)

    def test_login(self):
        """Test Login access page (returns "")"""
        rv = self.app.get('/pythonlogin', follow_redirects=True)
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(rv.data, b'""\n')

        # Integration Test
        """Test login using helper functions."""
        rv = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']
        )
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(rv.data, b'"Successfully logged in"\n')

        rv = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD'] + 'x'
        )
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(rv.data, b'"Incorrect username/password!"\n')

        rv = self.login(
            app.app.config['USERNAME'] + 'x',
            app.app.config['PASSWORD']
        )
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(rv.data, b'"Incorrect username/password!"\n')

    def test_logout(self):
        """Test logout using helper functions."""
        rv = self.logout()
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(rv.data, b'"Successfully logged out"\n')

    # register already existing user (same as logged in)
    def test_register(self):
        """Test register using helper functions."""
        # Integration Test
        rv = self.register(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD'],
            app.app.config['EMAIL']
        )
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(rv.data, b'"Account already exists!"\n')

        rv = self.register(
            app.app.config['USERNAME'] + 'bis',
            app.app.config['PASSWORD'],
            app.app.config['EMAIL'] + "@"
        )
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(rv.data, b'"Invalid email address!"\n')

        rv = self.register(
            app.app.config['USERNAME'] + '_',
            app.app.config['PASSWORD'],
            app.app.config['EMAIL']
        )
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(
            rv.data, b'"Username must contain only characters and numbers!"\n')

        rv = self.register(
            app.app.config['USERNAME'] + 'bis',
            app.app.config['PASSWORD'],
            None
        )
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(
            rv.data, b'"Please fill out the form!"\n')

    def test_home(self):
        """Test redirect to Login page if user is not logged in"""
        rv = self.app.get('/pythonlogin/home', follow_redirects=True)
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(rv.data, b'"Redirect to login page"\n')

    def test_profile(self):
        """Test redirect to Login page if user is not logged in"""
        rv = self.app.get('/pythonlogin/profile', follow_redirects=True)
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual(rv.data, b'"Redirect to login page"\n')


if __name__ == '__main__':
    unittest.main()
