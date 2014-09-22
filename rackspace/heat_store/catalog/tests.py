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
        s = Solution('test_data/info.yaml')
        self.assertEqual(s.title, 'the_title')
        self.assertEqual(s.short_description, 'the short description')
        self.assertIn('the <em>long</em> description', s.long_description)
        self.assertIn('src="test_data/diagram.png"', s.long_description)
        self.assertIn('alt="here is a diagram"', s.long_description)
        self.assertIn('highlight_1', s.highlights)
        self.assertIn('highlight_2', s.highlights)
        self.assertIn('<p><a href="http://example.com/">example.com</a></p>',
                      s.links)
        self.assertIn(
            '<p><a href="http://download.example.com/">Download</a></p>',
            s.links)
        self.assertEqual(s.heat_template,
                         'https://raw.githubusercontent.com/' +
                         'example/heat-example/master/example.yaml')
        self.assertEqual(s.env_file,
                         'https://raw.githubusercontent.com/' +
                         'example/heat-example/master/env.yaml')
        self.assertEqual(s.template_version, '0.0.1')

    def test_incomplete_solution(self):
        lines = open('test_data/info.yaml').readlines()

        # ensure the solution isn't imported if any of the items
        # below are missing
        missing_list = ['title', 'logo', 'short_description',
                        'long_description', 'heat_template',
                        'env_file', 'template_version']
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


if __name__ == '__main__':
    unittest.main()