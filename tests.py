import unittest
import requests


class TestMMSPApp(unittest.TestCase):
    def setUp(self):
        self.api_url = "http://localhost:5000"
        self.headers = {'Accept': 'application/json'}
        self.auth = ('john', 'test')

    def test_home_json_unauthorized(self):
        response = requests.get(f"{self.api_url}/", headers=self.headers)
        self.assertEqual(response.status_code, 401)

    def test_home_json_authorized(self):
        response = requests.get(f"{self.api_url}/", headers=self.headers, auth=self.auth)
        self.assertEqual(response.status_code, 200)

    def test_create_post_json_authorized(self):
        data = {'post_content': 'Test post content'}
        response = requests.post(f"{self.api_url}/create_post", headers=self.headers, auth=self.auth, data=data)
        self.assertEqual(response.status_code, 200)

    def test_add_or_remove_like_json_authorized(self):
        data = {'post_id': 1}
        response = requests.post(f"{self.api_url}/add_like/1", headers=self.headers, auth=self.auth, data=data)
        self.assertEqual(response.status_code, 200)

    def test_add_comment_json_authorized(self):
        data = {'post_id': 1, 'comment_content': 'Test comment content'}
        response = requests.post(f"{self.api_url}/add_comment/1", headers=self.headers, auth=self.auth, data=data)
        self.assertEqual(response.status_code, 200)

    def test_search_users_json_authorized(self):
        data = {'search_username': 'test'}
        response = requests.post(f"{self.api_url}/search_users", headers=self.headers, auth=self.auth, data=data)
        self.assertEqual(response.status_code, 200)

    def test_add_friend_json_authorized(self):
        data = {'friend_id': 2}
        response = requests.post(f"{self.api_url}/add_friend/2", headers=self.headers, auth=self.auth, data=data)
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        data = {'username': 'automatictest', 'email': 'test@auto.com', 'password': 'test'}
        response = requests.post(f"{self.api_url}/register", headers=self.headers, data=data)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
