from django.test import TestCase
from django.urls import reverse

from ..urls import app_name


USERNAME = "NoName"
GROUP_SLUG = "test-slug"
POST_ID = 1
ROUTES = [
    ("/", "index", []),
    ("/create/", "post_create", []),
    ("/follow/", "follow_index", []),
    (f"/group/{GROUP_SLUG}/", "group_list", [GROUP_SLUG]),
    (f"/profile/{USERNAME}/", "profile", [USERNAME]),
    (f"/posts/{POST_ID}/", "post_detail", [POST_ID]),
    (f"/posts/{POST_ID}/edit/", "post_edit", [POST_ID]),
    (f"/posts/{POST_ID}/comment/", "add_comment", [POST_ID]),
    (f"/profile/{USERNAME}/follow/", "profile_follow", [USERNAME]),
    (f"/profile/{USERNAME}/unfollow/", "profile_unfollow", [USERNAME])
]


class Test(TestCase):
    def test_url_routes(self):
        for url, route, args in ROUTES:
            with self.subTest(url=url, route=route, args=args):
                self.assertEqual(url, reverse(
                    f"{app_name}:{route}", args=args))
