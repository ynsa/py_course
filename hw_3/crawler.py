import csv
from concurrent.futures import ThreadPoolExecutor, wait
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
                 process_amount: int = 4,
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
        self._pages = []
        self._staff_pages = []

        retry = Retry(
            total=3,
            read=5,
            connect=5,
            backoff_factor=0.5,
            respect_retry_after_header=True
            # status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        self._session = session

        self._works = []

    @property
    def processed_pages(self):
        return self._processed_pages

    @property
    def unprocessed_pages(self):
        return self._unprocessed_pages

    def run_staff(self):
        while self._unprocessed_pages.qsize() < 100:
            try:
                url = self._unprocessed_staff_pages.get(timeout=2)
                if url not in self._processed_staff_pages:
                    print(f'Staff {url}.')
                    self._processed_staff_pages.add(url)
                    self._works.append(self._pool.submit(self.crawl, url, True))
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
                    self._works.append(self._pool.submit(self.crawl, url))
            except Empty:
                break
            except KeyboardInterrupt:
                print("Someone closed the program2")
                break
            except Exception as e:
                print(f'Get Exception2: {e}')

    def run(self):
        self.run_staff()
        wait(self._works)
        # with open('staff_page_content.csv', 'w') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=['url', 'content'])
        #     writer.writeheader()
        #     for data in self._staff_pages:
        #         writer.writerow(data)
        self._works = []
        self.run_articles()
        wait(self._works)
        print(f'Have processed {len(self._processed_pages)} articles.')
        print(f'Pages amount: {len(self._pages)}')
        print(f'Link arrays amount: {len(self._adjacency_list)}')
        try:
            with open('page_content.txt', 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['url', 'content'])
                writer.writeheader()
                writer.writerows(row for row in self._pages if row)
        except Exception as e:
            print(
                "Unable to store records in CSV file.\n")
            print(str(e))
        finally:
            print("Total Records  = " + str(len(self.processed_pages)))

    def crawl(self, url: str, is_staff: bool = False):
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
        try:
            response = self._session.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                if is_staff:
                    self.find_staff_links(url, response)
                else:
                    self.save_page(url, response)
            else:
                print(f'Page {url} return status {response.status_code}.')
                print(f'Text: {response.text}.')
        except requests.RequestException as e:
            print(f'Get request exception {e}')

    def find_staff_links(self, current_url, page):
        link_list = []
        self._staff_pages.append({'url': current_url,
                                  'content': page.text.encode("utf-8")})
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

    def save_page(self, current_url, page):
        soup = BeautifulSoup(page.text, 'html.parser')
        article = soup.find('li', {'id': 'ca-nstab-main'}).find('a').text == 'Артыкул'

        if not article:
            print(f'Can\'t find `Артыкул` in page.')
            return
        main_content = soup.find("div", {"id": "content"})
        no_article = main_content.find('div', {'class': 'noarticletext mw-content-ltr'})
        if no_article:
            print(f'There isn\'t an article at {current_url}')
            self._pages.append({'url': current_url, 'content': 'No article'})
            # self._pages[current_url] = 'No article'
            return
        self._pages.append({'url': current_url,
                            'content': page.text.encode("utf-8")})


if __name__ == '__main__':
    # Усе артыкулы
    crawler = Crawler('https://be.wikipedia.org/w/index.php?title=%D0%90%D0%B4%D0%BC%D1%8B%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D0%B5:AllPages&from=%21')
    crawler.run()
    # pprint(crawler.processed_pages)
    pprint(crawler._adjacency_list)




