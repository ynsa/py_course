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

        self.pool = ThreadPoolExecutor(max_workers=process_amount)
        self.works = []

        # for page in self._adjacency_list:
        #     adj_l = self._adjacency_list[page]
        #     for link in adj_l:
        #         if link not in self._adjacency_list.keys():
        #             adj_l.remove(link)
        #     self._adjacency_list[page] = adj_l

    def run(self, filename):
        csv.field_size_limit(922337203)
        with open(filename, 'r') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            for row in csv_reader:
                self.unprocessed_pages.put(row)
        print(f'Len of unprocessed_pages: {self.unprocessed_pages.qsize()}.')
        self.run_articles()

    def run_articles(self):
        while True:
            try:
                page = self.unprocessed_pages.get(timeout=2)
                if len(page) != 2 or self.base_url not in page[0]:
                    continue
                url = page[0]
                if url not in self.processed_pages:
                    # print(f'Article {url}.')
                    self.processed_pages.append(url)
                    self.works.append(self.pool.submit(
                        self.find_links, url, page[1]))
            except Empty:
                break
            except KeyboardInterrupt:
                print("Someone closed the program2")
                break
            except Exception as e:
                print(f'Get Exception2: {e}')
        print(f'Have processed {len(self.processed_pages)} articles.')
        print(f'Link arrays amount: {len(self.adjacency_list)}')

    def find_links(self, current_url, page):
        link_list = []
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
        # no_article = main_content.find('div', {'class': 'noarticletext mw-content-ltr'})
        # if no_article:
        #     print(f'There isn\'t an article at {current_url}')
        #     # self._pages[current_url] = 'No article'
        #     return
        # self._pages[current_url] = page.text
        adj_list = set()
        # links = main_content.find_all('a', {'class': 'mw-redirect'}, href=True)
        footer_links = main_content.find_all('div', {'id': 'catlinks'})
        for link in footer_links:
            link.extract()
        links = main_content.find_all('a', href=True)
        # links = set(link['href'] for link in links) - \
        #         set(link['href'] for link in footer_links)
        for link in links:
            url = link['href']
            if url.startswith('/wiki') or url.startswith(self.base_url):
                # if 'class' in link and \
                #         all(cl not in self.skip_classes for cl in link['class']):
                url = urljoin(self.base_url, url)
                adj_list.add(url)
        self.adjacency_list[current_url] = adj_list


if __name__ == '__main__':
    # Усе артыкулы
    crawler = Crawler(
        'https://be.wikipedia.org/w/index.php?title=%D0%90%D0%B4%D0%BC%D1%8B%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D0%B5:AllPages&from=%21')
    crawler.run()
    parser = WikiParser(base_url='https://be.wikipedia.org/wiki/')
    parser.unprocessed_pages = crawler.unprocessed_pages
    parser.run(filename='page_content.txt')
    # pprint(crawler.processed_pages)
    pprint(parser.adjacency_list)