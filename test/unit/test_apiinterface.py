import sys
sys.path.append('A:\Documents\GitHub\\tf2-stats\src')

import unittest
import api_interface as api # Code to be tested

class TestMathMethods(unittest.TestCase):

    def test_hash(self):
        # Check consistency has been maintained 

        test_dict = {'a' : 2, 'b' : 3}
        self.assertEqual(api.hash_dict(test_dict),6**3)

if __name__ == '__main__':
    unittest.main()
