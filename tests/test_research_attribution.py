import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_AUTHORS = {
    '2601.11109': 'Shaofeng Yin et al.',
    '2602.13294': 'Jiarong Liang et al.',
    '2602.11757': 'Yi Zhang et al.',
    '2604.23580': 'Tianyidan Xie et al.',
    '2606.01057': 'Yipeng Gao et al.',
    '2608.27549': 'Hanyang Wang et al.',
    '2610.03715': 'Ruihong Shen et al.',
}


class ResearchAttributionTests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'index.html').read_text()

    def section(self, section_id):
        match = re.search(r'<section id="' + section_id + r'"[^>]*>(.*?)</section>',
                          self.html, re.S)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_own_work_and_external_research_are_separate(self):
        own = self.section('research-context')
        related = self.section('related-research')
        self.assertIn('Our work: IR3D-Bench.', own)
        self.assertIn('href="#citation"', own)
        self.assertNotIn('related-grid', own)
        self.assertNotIn('id="related-research"', own)
        self.assertIn('<h2 id="related-research-title">Selected Related Research</h2>', related)
        self.assertNotIn('Our work', related)
        self.assertNotIn('Cite IR3D-Bench', related)
        self.assertNotIn('related-card-ours', self.html)

    def test_each_external_card_has_verified_byline_and_paper_link(self):
        cards = re.findall(r'<article class="related-card">(.*?)</article>',
                           self.section('related-research'), re.S)
        self.assertEqual(len(cards), len(EXPECTED_AUTHORS))
        for paper_id, author in EXPECTED_AUTHORS.items():
            matches = [card for card in cards if 'https://arxiv.org/abs/' + paper_id in card]
            self.assertEqual(len(matches), 1)
            self.assertIn('<p class="related-authors">' + author + '</p>', matches[0])
            self.assertIn('<h3>', matches[0])
            self.assertNotIn('ir3d.webp', matches[0])

    def test_attribution_boundary_is_visible_before_cards(self):
        related = self.section('related-research')
        preamble = related.split('<div class="related-grid">')[0]
        self.assertIn('Each project is credited to its original authors.', preamble)
        self.assertIn('does not imply collaboration, endorsement, direct influence, or priority',
                      preamble)
        self.assertIn('Dates refer to the first arXiv submission.', preamble)


if __name__ == '__main__':
    unittest.main()
