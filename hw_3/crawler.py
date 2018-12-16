import json
from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from queue import Queue, Empty
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class StrangeException(Exception):
    pass


class Crawler:
    skip_classes = ('image', )

    def __init__(self, base_url: str,
                 process_amount: int = 20,
                 timeout: int = 10, raise_for_status: bool = True):
        self.base_url = base_url
        self.timeout = timeout
        self.raise_for_status = raise_for_status
        self._pool = ThreadPoolExecutor(max_workers=process_amount)
        self._processed_pages = set()
        self._processed_staff_pages = set()
        self._unprocessed_staff_pages = Queue()
        self._unprocessed_staff_pages.put(base_url)
        self._unprocessed_pages = Queue()

        self._adjacency_list = dict()
        self._pages = dict()

    @property
    def processed_pages(self):
        return self._processed_pages

    @property
    def unprocessed_pages(self):
        return self._unprocessed_pages

    def run_staff(self):
        while True:
            try:
                url = self._unprocessed_staff_pages.get(timeout=2)
                if url not in self._processed_staff_pages:
                    print(f'Staff {url}.')
                    self._processed_staff_pages.add(url)
                    job = self._pool.submit(self.crawl, url, True)
                    job.add_done_callback(self.strange_result_func)
            except Empty:
                break
            except KeyboardInterrupt:
                print("Someone closed the program")
                break
            except Exception as e:
                print(f'Get Exception: {e}')
        print(f'Have processed {len(self._processed_staff_pages)} staff pages.')

    def run_articles(self):
        while True:
            try:
                url = self._unprocessed_pages.get(timeout=2)
                if url not in self._processed_pages:
                    # print(f'Article {url}.')
                    self._processed_pages.add(url)
                    job = self._pool.submit(self.crawl, url)
                    job.add_done_callback(self.strange_result_func)
            except Empty:
                break
            except KeyboardInterrupt:
                print("Someone closed the program2")
                break
            except Exception as e:
                print(f'Get Exception2: {e}')
        print(f'Have processed {len(self._processed_pages)} articles.')
        print(f'Pages amount: {len(self._pages)}')
        print(f'Link arrays amount: {len(self._adjacency_list)}')

    def run(self):
        self.run_staff()
        self.run_articles()
        # lock = Lock()
        # self._pool.join()
        # for page in self._adjacency_list:
        #     adj_l = self._adjacency_list[page]
        #     for link in adj_l:
        #         if link not in self._adjacency_list.keys():
        #             adj_l.remove(link)
        #     self._adjacency_list[page] = adj_l
        try:
            # file to store state based URLs
            record_file = open('records_file.txt', 'a+')
            record_file.write(json.dumps(self._pages.items()))
            record_file.close()
        except Exception as e:
            print(
                "Unable to store records in CSV file. Technical details below.\n")
            print(str(e))
        finally:
            print("Total Records  = " + str(len(self.processed_pages)))

    def crawl(self, url: str, is_staff: bool = False):
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
        try:
            # sleep(1)
            retry = Retry(
                total=3,
                read=5,
                connect=5,
                backoff_factor=0.1,
                respect_retry_after_header=True
                # status_forcelist=status_forcelist,
            )
            adapter = HTTPAdapter(max_retries=retry)
            session = requests.Session()
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            response = session.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                if is_staff:
                    self.find_staff_links(response)
                else:
                    self.find_links(url, response)
                # map(self.unprocessed_pages.put, links)

            else:
                print(f'Page {url} return status {response.status_code}.')
        except requests.RequestException as e:
            print(f'Get request exception {e}')

    def find_staff_links(self, page):
        link_list = []
        soup = BeautifulSoup(page.text, 'html.parser')
        # separate content from other staff
        main_content = soup.find("div", {"id": "content"})
        if not main_content:
            print(f'Can\'t find main_content in page.')
            return link_list
        soup = main_content
        all_pages = soup.find("div", {"class": "mw-allpages-body"})
        staff_page = True if all_pages else False
        if not staff_page:
            print('Strange staff page without all_pages.')
            raise StrangeException()
        links = all_pages.find_all('a', href=True)
        for link in links:
            url = link['href']
            if url.startswith('/wiki') or url.startswith(self.base_url):
                # if 'class' in link and \
                #         all(cl not in self.skip_classes for cl in link['class']):
                url = urljoin(self.base_url, url)
                if url not in self.processed_pages:
                    self._unprocessed_pages.put(url)
        navigation = soup.find("div", {"class": "mw-allpages-nav"})
        nav_a = navigation.findChildren("a", recursive=False)
        for link in nav_a:
            url = urljoin(self.base_url, link['href'])
            if url not in self._processed_staff_pages:
                self._unprocessed_staff_pages.put(url)

    def find_links(self, current_url, page):
        # if current_url == 'https://be.wikipedia.org/wiki/%D0%A4%D0%B0%D0%B9%D0%BB:Wiki_letter_w.svg':
        #     print()
        link_list = []
        soup = BeautifulSoup(page.text, 'html.parser')
        article = soup.find('li', {'id': 'ca-nstab-main'}).find('a').text == 'Артыкул'

        if not article:
            print(f'Can\'t find main_content in page.')
            counter = 0
            for some_page in self._adjacency_list:
                if current_url in self._adjacency_list[some_page]:
                    links = self._adjacency_list[some_page]
                    links.pop(current_url)
                    self._adjacency_list[some_page] = links
                    counter += 1
            print(f'Remove incorrect links from {counter} pages')
            return link_list
        main_content = soup.find("div", {"id": "content"})
        no_article = main_content.find('div', {'class': 'noarticletext mw-content-ltr'})
        if no_article:
            print(f'There isn\'t an article at {current_url}')
            self._pages[current_url] = 'No article'
            return
        self._pages[current_url] = page.text
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
        self._adjacency_list[current_url] = adj_list

        # print(f'{len(adj_list)} links arrives at {current_url}.')

    def strange_result_func(self, result):
        pass


if __name__ == '__main__':
    # Усе артыкулы
    crawler = Crawler('https://be.wikipedia.org/w/index.php?title=%D0%90%D0%B4%D0%BC%D1%8B%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D0%B5:AllPages&from=%21')
    crawler.run()
    # pprint(crawler.processed_pages)
    pprint(crawler._adjacency_list)




