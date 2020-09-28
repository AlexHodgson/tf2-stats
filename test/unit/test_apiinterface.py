import sys
sys.path.append('A:\Documents\GitHub\\tf2-stats\src')

import unittest
import api_interface as api # Code to be tested
import numpy as np

class TestMathMethods(unittest.TestCase):

    def test_hash(self):
        # Check consistency has been maintained 

        test_dict = {'a' : 2, 'b' : 3}
        self.assertEqual(api.hash_dict(test_dict),6**3)

    def test_normalize(self):
        # Check the normalization function

        test_array = np.random.randint(100, size=(50))

        self.assertEqual(len(test_array), np.sum(api.normalize_rows(test_array)))

if __name__ == '__main__':
    unittest.main()
