from django.test import TestCase
from django.urls import reverse

USERNAME = "NoName"
GROUP_SLUG = "test-slug"
POST_ID = 1
ROUTES = [
    ("/", "index", []),
    ("/create/", "post_create", []),
    (f"/group/{GROUP_SLUG}/", "group_list", [GROUP_SLUG]),
    (f"/profile/{USERNAME}/", "profile", [USERNAME]),
    (f"/posts/{POST_ID}/", "post_detail", [POST_ID]),
    (f"/posts/{POST_ID}/edit/", "post_edit", [POST_ID]),
]


class Test(TestCase):
    def test_url_routes(self):
        for url, page, args in ROUTES:
            with self.subTest(url=url, page=page, args=args):
                self.assertEqual(url, reverse("posts:" + page, args=args))