#!/usr/bin/env python
import unittest

import mox
import six.moves.urllib.request as urlrequest
from six import StringIO

from solution import Solution


class TestSolution(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()
        pass

    def tearDown(self):
        self.mox.VerifyAll()
        self.mox.UnsetStubs()

    def test_create_solution(self):
        s = Solution('test_data/example/info.yaml')
        self.assertEqual(len(s.id), 32)
        self.assertEqual(s.title, 'the_title')
        self.assertEqual(s.logo, 'test_data/example/the_logo.png')
        self.assertEqual(s.release, '0.1')
        self.assertEqual(s.short_description, '<p>The short description</p>')
        self.assertIn('This is the <em>long</em> description',
                      s.long_description)
        self.assertIn('src="test_data/example/diagram.png"', s.long_description)
        self.assertIn('alt="here is a diagram"', s.long_description)
        self.assertIn('<strong>architecture</strong>', s.architecture)
        self.assertIn('Design spec #1', s.design_specs)
        self.assertIn('Design spec #2', s.design_specs)
        self.assertEqual(s.heat_template, 'example.yaml')
        self.assertEqual(s.env_file, 'env.yaml')

    def test_incomplete_solution(self):
        lines = open('test_data/example/info.yaml').readlines()

        # ensure the solution isn't imported if any of the items
        # below are missing
        missing_list = ['name', 'short_desc', 'long_desc', 'heat_template',
                        'release']
        self.mox.StubOutWithMock(urlrequest, 'urlopen')
        for missing in missing_list:
            yaml = [line for line in lines if missing not in line]
            urlrequest.urlopen(
                'http://example.com/no-{0}.yaml'.format(missing)) \
                .AndReturn(StringIO('\n'.join(yaml)))
        self.mox.ReplayAll()

        for missing in missing_list:
            with self.assertRaises(KeyError):
                Solution('http://example.com/no-{0}.yaml'.format(missing))

    def test_parameter_types(self):
        s = Solution('test_data/example/info.yaml')
        params = s.get_parameter_types(None)

        self.assertEqual(len(params), 5)

        self.assertEqual(params[0]['name'], 'floating-network-id')
        self.assertEqual(params[0]['type'], 'comma_delimited_list')
        self.assertIn(params[0]['default'],
                      params[0]['constraints'][0]['allowed_values'])
        self.assertIn('_mapping', params[0])
        self.assertEqual(params[0]['_mapping'], {'first_network': '11',
                                                 'second_network': '22',
                                                 'third_network': '33'})
        self.assertEqual(s.map_parameter(params, 'floating-network-id',
                                         'second_network'), '22')

        self.assertEqual(params[1]['name'], 'flavor')
        self.assertEqual(params[1]['type'], 'comma_delimited_list')
        self.assertIn(params[1]['default'], 'm1.small')

        self.assertEqual(params[2]['name'], 'image')
        self.assertEqual(params[2]['type'], 'comma_delimited_list')
        self.assertIn(params[2]['default'],
                      params[2]['constraints'][0]['allowed_values'])

        self.assertEqual(params[3]['name'], 'image-count')
        self.assertEqual(params[3]['type'], 'number')

        self.assertEqual(params[4]['name'], 'keyname')
        self.assertEqual(params[4]['type'], 'comma_delimited_list')
        self.assertIn(params[4]['default'],
                      params[4]['constraints'][0]['allowed_values'])


if __name__ == '__main__':
    unittest.main()
