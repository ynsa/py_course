import math
from concurrent.futures import ThreadPoolExecutor, wait
from queue import Queue, Empty
from urllib.parse import urljoin

import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class StrangeException(Exception):
    """Exception is raised when Crawler expects staff page
    but get page of another type."""
    pass


class Crawler:

    def __init__(self, base_url: str,
                 process_amount: int = 4,
                 timeout: int = 10,
                 total_retry_count: int = 3,
                 backoff_factor: float = 0.5):

        self.base_url = base_url
        self.timeout = timeout
        self._pool = ThreadPoolExecutor(max_workers=process_amount)
        self._works = []

        self._processed_pages = set()
        self._unprocessed_pages = Queue()

        self._processed_staff_pages = set()
        self._unprocessed_staff_pages = Queue()
        self._unprocessed_staff_pages.put(base_url)

        self._adjacency_list = dict()
        self._counter = dict()
        self._pages = dict()
        self._staff_pages = []

        retry = Retry(
            total=total_retry_count,
            read=total_retry_count,
            connect=total_retry_count,
            backoff_factor=backoff_factor,
            respect_retry_after_header=True
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        self._session = session

    @property
    def processed_pages(self):
        return self._processed_pages

    @property
    def unprocessed_pages(self):
        return self._unprocessed_pages

    def _run_staff(self, min_page_count: int = 10000):
        while self._unprocessed_pages.qsize() < min_page_count:
            try:
                url = self._unprocessed_staff_pages.get(timeout=2)
                if url not in self._processed_staff_pages:
                    self._processed_staff_pages.add(url)
                    self._works.append(self._pool.submit(self.crawl, url, True))
            except Empty:
                break
            except Exception as e:
                print(f'Get Exception: {e}')
        print(f'Have processed {len(self._processed_staff_pages)} staff pages.')

    def _run_articles(self):
        while True:
            try:
                url = self._unprocessed_pages.get(timeout=2)
                if url not in self._processed_pages:
                    self._processed_pages.add(url)
                    self._works.append(self._pool.submit(self.crawl, url))
            except Empty:
                break
            except Exception as e:
                print(f'Get Exception2: {e}')

    def run(self):
        self._run_staff()
        wait(self._works)
        self._works = []
        self._run_articles()
        wait(self._works)
        print(f'Have processed {len(self._processed_pages)} articles.')
        self._clean_adj_list()
        self.generate_report()

    def generate_report(self):
        """Generates not the best version of bar for representing
        [(links amount)/page] relations."""

        self._pool.map(self._normalize, self._pages)
        pl_max = max(self._counter.values())
        results = {key: (value * 10.0 / pl_max) for key, value
                   in self._counter.items()}
        plt.bar(results.keys(), results.values(), color='g', width=1)
        plt.xlabel('Pages')
        plt.ylabel('Links count')
        plt.xticks(rotation='vertical')
        plt.savefig('bar.png')
        plt.show()

    def _normalize(self, url):
        self._counter[url] = math.log(self._counter[url])

    def _clean_adj_list(self):
        """
        Remove links to pages that haven't arrived in staff pages,
        (they are not presented in graph) and count links per each page
        in graph
        """

        for page in self._pages:
            adj_list = self._adjacency_list[page]
            adj_list = [link for link in adj_list if link in self._pages]
            for link in adj_list:
                counter = self._counter.get(link, None)
                if not counter:
                    self._counter[link] = 0
                self._counter[link] += 1
            self._adjacency_list[page] = adj_list

    def crawl(self, url: str, is_staff: bool = False):
        # add header to be more polite to the site
        headers = {
            'user-agent': 'Mozilla/5.0 '
                          'Macintosh; Intel Mac OS X 10_11_6) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/53.0.2785.143 Safari/537.36'}
        try:
            response = self._session.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                if is_staff:
                    self.find_staff_links(response)
                else:
                    self.find_links(url, response)
            else:
                print(f'Page {url} return status {response.status_code}.')
                print(f'Text: {response.text}.')
        except requests.RequestException as e:
            print(f'Get request exception {e}')

    def find_staff_links(self, page):
        """
        Find unprocessed staff urls and article urls in the current page.
        """
        soup = BeautifulSoup(page.text, 'html.parser')
        main_content = soup.find("div", {"id": "content"})
        if not main_content:
            print(f'Can\'t find main_content in page.')
            return
        soup = main_content
        all_pages = soup.find("div", {"class": "mw-allpages-body"})
        staff_page = True if all_pages else False
        if not staff_page:
            print('Strange staff page without all_pages.')
            raise StrangeException()
        links = all_pages.find_all('a', href=True)
        for link in links:
            url = link['href']
            # check that link is to the current site
            if url.startswith('/wiki') or url.startswith(self.base_url):
                url = urljoin(self.base_url, url)
                if url not in self.processed_pages:
                    self._unprocessed_pages.put(url)
                    self._pages[url] = ''

        # search for new staff urls
        navigation = soup.find("div", {"class": "mw-allpages-nav"})
        nav_a = navigation.findChildren("a", recursive=False)
        for link in nav_a:
            url = urljoin(self.base_url, link['href'])
            if url not in self._processed_staff_pages:
                self._unprocessed_staff_pages.put(url)

    def find_links(self, current_url: str, response):
        """
        Find unprocessed article links.
        """
        page = response.text
        soup = BeautifulSoup(page, 'html.parser')
        main_content = soup.find("div", {"id": "content"})

        # remove links that don't have straight connection to the article
        footer_links = main_content.find_all('div', {'id': 'catlinks'})
        for link in footer_links:
            link.extract()

        links = main_content.find_all('a', href=True)
        adj_list = set()
        for link in links:
            url = link['href']
            if 'wiki' in url:
                url = urljoin(self.base_url, url)
                adj_list.add(url)
        self._adjacency_list[current_url] = adj_list


if __name__ == '__main__':
    # All articles in Belarusian starting from the letter `п`.
    crawler = Crawler('https://be.wikipedia.org/wiki/%D0%90%D0%B4%D0%BC%D1%8B%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D0%B5:AllPages?from=%D0%BF&to=&namespace=0')
    crawler.run()




