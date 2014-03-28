import unittest

import bux_grader_framework.grader as grader
import bux_grader_framework.conf as conf


class TestGrader(unittest.TestCase):

    def setUp(self):
        self.grader = grader.Grader()

    def test_init(self):
        self.assertIsInstance(self.grader, grader.Grader)

    def test_grader_config(self):
        # Assert default config class
        self.assertTrue(hasattr(self.grader, 'config_class'))
        self.assertIs(self.grader.config_class, conf.Config)

        # Assert config instantiated on property accesss
        self.assertTrue(hasattr(self.grader, 'config'))
        self.assertIsInstance(self.grader.config, self.grader.config_class)

if __name__ == '__main__':
    unittest.main()
