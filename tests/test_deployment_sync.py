import unittest
from pathlib import Path


class DeploymentSyncTests(unittest.TestCase):
    def test_deployment_app_matches_main_app(self):
        project_root = Path(__file__).resolve().parents[1]

        self.assertEqual(
            (project_root / "app.py").read_bytes(),
            (project_root / "deployment" / "app.py").read_bytes(),
            "deployment/app.py must be regenerated from app.py before merging",
        )


if __name__ == "__main__":
    unittest.main()