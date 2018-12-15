from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from queue import Queue, Empty
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


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

    def run(self):
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
        while True:
            try:
                url = self._unprocessed_pages.get(timeout=2)
                if url not in self.processed_pages:
                    print(f'Article {url}.')
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
        try:
            # file to store state based URLs
            record_file = open('records_file.txt', 'a+')
            record_file.write("\n".join(self._pages.items()))
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
            sleep(1)
            response = requests.get(url, headers=headers, timeout=self.timeout)
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
        # main_content = BeautifulSoup(main_content, 'html.parser')
        soup = main_content
        all_pages = soup.find("div", {"class": "mw-allpages-body"})
        staff_page = True if all_pages else False
        if not staff_page:
            print('Strange staff page without all_pages.')
            raise StrangeException()
            # heading = soup.find("h1", {"class": "firstHeading"})
            # if heading:
            #     self._adjacency_list[heading] = []
            #     self._pages[heading] = page.text
            # adj_list = self._adjacency_list.get(heading, [])
        links = all_pages.find_all('a', href=True)
        for link in links:
            url = link['href']
            if url.startswith('/wiki') or url.startswith(self.base_url):
                # if 'class' in link and \
                #         all(cl not in self.skip_classes for cl in link['class']):
                url = urljoin(self.base_url, url)
                if url not in self.processed_pages:
                    self._unprocessed_pages.put(url)
                    # self._pages[url] = ''
                    # self._adjacency_list[url] = []
        # navigation = soup.find("div", {"class": "mw-allpages-nav"})
        # nav_a = navigation.findChildren("a", recursive=False)
        # for link in nav_a:
        #     url = urljoin(self.base_url, link['href'])
        #     if url not in self._processed_staff_pages:
        #         self._unprocessed_staff_pages.put(url)

    def find_links(self, current_url, page):
        link_list = []
        soup = BeautifulSoup(page.text, 'html.parser')
        main_content = soup.find("div", {"id": "content"})
        if not main_content:
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
        # self._unprocessed_pages.put(current_url)
        no_article = main_content.find('div', {'class': 'noarticletext mw-content-ltr'})
        if no_article:
            print(f'There isn\'t an article at {current_url}')
            self._pages[current_url] = 'No article'
            return
        self._pages[current_url] = page.text
        # main_content = BeautifulSoup(main_content, 'html.parser')
        # soup = main_content
        # heading = soup.find("h1", {"class": "firstHeading"})
        # if heading:
        #     self._adjacency_list[heading] = []
        #     self._pages[heading] = page.text
        adj_list = []
        links = main_content.find_all('a', {'class': 'mw-redirect'}, href=True)
        for link in links:
            url = link['href']
            if url.startswith('/wiki') or url.startswith(self.base_url):
                # if 'class' in link and \
                #         all(cl not in self.skip_classes for cl in link['class']):
                url = urljoin(self.base_url, url)
                adj_list.append(url)
        self._adjacency_list[current_url] = adj_list

        print(f'{len(adj_list)} links arrives at {current_url}.')
        # navigation = soup.find("div", {"class": "mw-allpages-nav"})
        # nav_a = navigation.findChildren("a", recursive=False)
        # for link in nav_a:
        #     url = urljoin(self.base_url, link['href'])
        #     if url not in self._processed_staff_pages:
        #         self._unprocessed_staff_pages.put(url)


    def strange_result_func(self, result):
        pass
        # print('in strange_result_func')


if __name__ == '__main__':
    # Усе артыкулы
    crawler = Crawler('https://be.wikipedia.org/w/index.php?title=%D0%90%D0%B4%D0%BC%D1%8B%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D0%B5:AllPages&from=%21')
    crawler.run()
    # pprint(crawler.processed_pages)
    pprint(crawler._adjacency_list)




