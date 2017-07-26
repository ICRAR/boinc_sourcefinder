import unittest
from helpers import create_test_schemas, destroy_test_schemas


class WorkGeneratorTest(unittest.TestCase):
    def setUp(self):
        create_test_schemas()

    def tearDown(self):
        destroy_test_schemas()

    def register_run(self):
        self.assertEqual(True, False)

    def register_cube(self):
        self.assertEqual(True, False)

    def work_generator(self):
        self.assertEqual(True, False)

if __name__ == '__main__':
    unittest.main()