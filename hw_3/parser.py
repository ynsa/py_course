import csv
import sys
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from queue import Queue, Empty
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from hw_3.crawler import Crawler


class StrangeException(Exception):
    pass


class WikiParser:
    def __init__(self, base_url: str, process_amount: int = 20):
        self.base_url = base_url
        self.processed_pages = []
        self.unprocessed_pages = Queue()
        self.adjacency_list = []
        self.pages = dict()

        self.pool = ThreadPoolExecutor(max_workers=process_amount)
        self.works = []

        # for page in self._adjacency_list:
        #     adj_l = self._adjacency_list[page]
        #     for link in adj_l:
        #         if link not in self._adjacency_list.keys():
        #             adj_l.remove(link)
        #     self._adjacency_list[page] = adj_l

    def run(self):
        print(f'Len of unprocessed_pages: {self.unprocessed_pages.qsize()}.')
        self.run_articles()

    def run_articles(self):
        while True:
            try:
                url = self.unprocessed_pages.get(timeout=2)

                if url not in self.processed_pages:
                    # print(f'Article {url}.')
                    self.processed_pages.append(url)
                    self.works.append(self.pool.submit(
                        self.find_links, url))
            except Empty:
                break
            except KeyboardInterrupt:
                print("Someone closed the program2")
                break
            except Exception as e:
                print(f'Get Exception2: {e}')
        print(f'Have processed {len(self.processed_pages)} articles.')
        print(f'Link arrays amount: {len(self.adjacency_list)}')

    def find_links(self, current_url):
        link_list = []
        page = self.pages[current_url]
        soup = BeautifulSoup(page, 'html.parser')
        article = soup.find('li', {'id': 'ca-nstab-main'}).find('a').text == 'Артыкул'.encode("utf-8")

        if not article:
            print(f'Can\'t find `Артыкул` in page.')
            counter = 0
            for some_page in self.adjacency_list:
                if current_url in self.adjacency_list[some_page]:
                    links = self.adjacency_list[some_page]
                    links.pop(current_url)
                    self.adjacency_list[some_page] = links
                    counter += 1
            print(f'Remove incorrect links from {counter} pages')
            return link_list
        main_content = soup.find("div", {"id": "content"})
        adj_list = set()
        footer_links = main_content.find_all('div', {'id': 'catlinks'})
        for link in footer_links:
            link.extract()
        links = main_content.find_all('a', href=True)
        for link in links:
            url = link['href']
            url = urljoin(self.base_url, url)
            if self.pages.get(url, None):
                adj_list.add(url)
            # if url.startswith('/wiki') or url.startswith(self.base_url):
                # if 'class' in link and \
                #         all(cl not in self.skip_classes for cl in link['class']):
                # url = urljoin(self.base_url, url)
        self.adjacency_list[current_url] = adj_list
        print(f'{len(adj_list)} links at {current_url}')


if __name__ == '__main__':
    # Усе артыкулы
    crawler = Crawler(
        'https://be.wikipedia.org/w/index.php?title=%D0%90%D0%B4%D0%BC%D1%8B%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D0%B5:AllPages&from=%21')
    crawler.run()
    parser = WikiParser(base_url='https://be.wikipedia.org/wiki/')
    parser.unprocessed_pages = crawler.unprocessed_pages
    parser.pages = crawler._pages
    parser.run()
    # pprint(crawler.processed_pages)
    pprint(parser.adjacency_list)