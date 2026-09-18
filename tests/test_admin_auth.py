import importlib
import os
import unittest
from contextlib import contextmanager
from unittest.mock import patch

import app as app_module


MISSING = object()
VALID_SESSION_SECRET = "test-session-secret-" + ("x" * 12)


@contextmanager
def app_with_admin_password(password=MISSING, session_secret=VALID_SESSION_SECRET):
    """Load the application with an isolated admin configuration."""
    environment = {"SESSION_SECRET": session_secret}
    if password is not MISSING:
        environment["ADMIN_PASSWORD"] = password

    with patch.dict(os.environ, environment, clear=True):
        module = importlib.reload(app_module)
        module.app.config.update(TESTING=True)
        yield module


class AdminAuthTests(unittest.TestCase):
    def test_login_is_disabled_without_a_usable_session_secret(self):
        for secret in ("", " \t\n ", "x" * 31):
            with self.subTest(secret=secret):
                with app_with_admin_password("correct-password", secret) as module:
                    self.assertFalse(module.SESSION_SECRET_CONFIGURED)
                    self.assertFalse(module.ADMIN_AUTH_ENABLED)
                    self.assertIsNone(module.app.secret_key)

                    response = module.app.test_client().get("/admin/login")

                    self.assertEqual(response.status_code, 200)
                    self.assertIn(
                        b"Admin login is unavailable until SESSION_SECRET is configured with at least 32 characters.",
                        response.data,
                    )
                    self.assertNotIn(b'name="password"', response.data)

    def test_login_is_disabled_without_a_usable_admin_password(self):
        for password in (MISSING, "", " \t\n "):
            with self.subTest(password=password):
                with app_with_admin_password(password) as module:
                    client = module.app.test_client()

                    response = client.get("/admin/login")

                    self.assertEqual(response.status_code, 200)
                    self.assertIn(
                        b"Admin login is unavailable until ADMIN_PASSWORD is configured.",
                        response.data,
                    )
                    self.assertNotIn(b'name="password"', response.data)

                    response = client.post(
                        "/admin/login", data={"password": "correct-password"}
                    )

                    self.assertEqual(response.status_code, 200)
                    self.assertIn(
                        b"Admin login is unavailable until ADMIN_PASSWORD is configured.",
                        response.data,
                    )
                    with client.session_transaction() as session:
                        self.assertNotIn("admin_logged_in", session)

    def test_configured_password_allows_login(self):
        with app_with_admin_password("correct-password") as module:
            client = module.app.test_client()

            response = client.post(
                "/admin/login",
                data={"password": "correct-password"},
                follow_redirects=False,
            )

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.headers["Location"], "/admin")
            with client.session_transaction() as session:
                self.assertTrue(session["admin_logged_in"])

            dashboard = client.get("/admin")
            self.assertEqual(dashboard.status_code, 200)
            self.assertIn(b"Admin Dashboard", dashboard.data)

    def test_incorrect_password_is_rejected_when_configured(self):
        with app_with_admin_password("correct-password") as module:
            client = module.app.test_client()

            response = client.post(
                "/admin/login", data={"password": "incorrect-password"}
            )

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Invalid password", response.data)
            with client.session_transaction() as session:
                self.assertNotIn("admin_logged_in", session)

    def test_existing_admin_session_is_rejected_after_credentials_are_disabled(self):
        with app_with_admin_password("correct-password") as module:
            client = module.app.test_client()
            login = client.post(
                "/admin/login",
                data={"password": "correct-password"},
                follow_redirects=False,
            )
            self.assertEqual(login.status_code, 302)

            with patch.object(module, "ADMIN_PASSWORD", None), patch.object(
                module, "ADMIN_AUTH_ENABLED", False
            ):
                for route in ("/admin", "/admin/categories"):
                    with self.subTest(route=route):
                        response = client.get(route, follow_redirects=False)

                        self.assertEqual(response.status_code, 302)
                        self.assertEqual(
                            response.headers["Location"], "/admin/login"
                        )


if __name__ == "__main__":
    unittest.main()