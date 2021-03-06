# -*- coding: utf-8 -*-
import re
import logging
from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = 'https://www.novelpassion.com/search?keyword=%s'

class NovelPassion(Crawler):
    base_url = 'https://www.novelpassion.com/'

    # lncrawl -q "Forced to Date a Big Shot" --sources

    def search_novel(self, query):
        query = query.lower().replace(' ', '%20')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('div.lh1d5'):
            a = tab.select_one('a')
            # NOTE: Could not get latest chapter to show.
            # latest = tab.select_one('.dab a')
            latest = " "
            votes = tab.select_one('span[class="g_star"]')['title']
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': 'Rating: %s' % (votes),
            })
        # end for

        return results
    # end def

    # def search_novel(self, query):
    #     '''Gets a list of (title, url) matching the given query'''
    #     query = query.strip().lower().replace(' ', '%20')
    #     soup = self.get_soup(search_url % query)

    #     results = []
    #     for div in soup.select('.d-80 .j_bookList ul li > lh1d5'):
    #         a = div.select_one('a.c_000')
    #         info = div.select_one('.dab')
    #         results.append(
    #             {
    #                 'title': a.text.strip(),
    #                 'url': self.absolute_url(a['href']),
    #                 'info': info.text.strip() if info else '',
    #             }
    #         )
    #     # end for

    #     return results

    # # end def
    
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        img = soup.select_one('div.nw i.g_thumb img')
        self.novel_title = img['alt'].strip()
        self.novel_cover = self.absolute_url(img['src'])

        span = soup.select_one('div.dns a.stq')
        if span:
            self.novel_author = span.text.strip()
        # end if

        chap_id = 0
        for a in soup.select('#stq a.c_000'):
            vol_id = chap_id // 100 + 1
            if vol_id > len(self.volumes):
                self.volumes.append({
                    'id': vol_id,
                    'title': 'Volume %d' % vol_id
                })
            # end if

            chap_id += 1
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': ('Chapter %d' % chap_id),
                'url': self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        strong = soup.select_one('.cha-words strong')
        if strong and re.search(r'Chapter \d+', strong.text):
            chapter['title'] = strong.text.strip()
            logger.info('Updated title: %s', chapter['title'])
        # end if

        self.bad_tags += ['h1', 'h3', 'hr']
        contents = soup.select_one('.cha-words')
        body = self.extract_contents(contents)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
