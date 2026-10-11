import json
from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PageTags(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class StaticLayoutTests(unittest.TestCase):
    def test_appendix_styles_are_prerendered(self):
        source = (ROOT / 'static/js/distill_template.v2.js').read_text()
        start = source.index('<style>', source.index('const T$2 = Template')) + 7
        expected = source[start:source.index('</style>', start)]
        self.assertEqual((ROOT / 'static/css/distill-appendix.css').read_text().strip(),
                         expected.strip())
        tags = PageTags((ROOT / 'index.html').read_text()).tags
        self.assertTrue(any(tag == 'd-appendix' and 'distill-prerendered' in attrs
                            for tag, attrs in tags))
        self.assertIn(('link', {'rel': 'stylesheet',
                              'href': './static/css/distill-appendix.css'}), tags)

    def test_css_matches_template_injection(self):
        source = (ROOT / 'static/js/distill_template.v2.js').read_text()
        parts = []
        for name in ('base', 'layout', 'title', 'byline', 'article', 'math', 'print'):
            prefix = '  var ' + name + ' = '
            line = next(line for line in source.splitlines() if line.startswith(prefix))
            parts.append(json.loads(line[len(prefix):-1]))
        self.assertEqual(
            (ROOT / 'static/css/distill-base.css').read_text().rstrip(),
            ''.join(parts).rstrip(),
            'Keep the static CSS in sync when updating the Distill template.',
        )

    def test_layout_is_render_blocking_and_precedes_overrides(self):
        tags = PageTags((ROOT / 'index.html').read_text()).tags
        layout = [(i, tag, attrs) for i, (tag, attrs) in enumerate(tags)
                  if attrs.get('id') == 'distill-prerendered-styles']
        self.assertEqual(len(layout), 1)
        index, tag, attrs = layout[0]
        self.assertEqual(tag, 'link')
        self.assertEqual(attrs.get('rel'), 'stylesheet')
        self.assertEqual(attrs.get('href'), './static/css/distill-base.css')
        self.assertNotIn('onload', attrs)
        self.assertNotIn('media', attrs)
        for i, (tag, attrs) in enumerate(tags):
            if attrs.get('src') == './static/js/distill_template.v2.js':
                self.assertLess(index, i)
            if attrs.get('href') == './static/css/style.css':
                self.assertLess(index, i)

    def test_video_keeps_click_to_load_and_hd_link(self):
        tags = PageTags((ROOT / 'index.html').read_text()).tags
        video = next(attrs for tag, attrs in tags if attrs.get('id') == 'showreel')
        self.assertEqual(video.get('preload'), 'none')
        self.assertNotIn('autoplay', video)
        self.assertNotIn('muted', video)
        self.assertIn(('source', {'src': 'static/video/ir3d-showreel-55s-en-720p.mp4',
                                 'type': 'video/mp4'}), tags)
        self.assertTrue(any(tag == 'a' and attrs.get('href') ==
                            'static/video/ir3d-showreel-55s-en.mp4'
                            for tag, attrs in tags))


if __name__ == '__main__':
    unittest.main()
