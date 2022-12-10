from collections import defaultdict
import requests
import csv

# https://blog.devgenius.io/best-way-to-speed-up-a-bulk-of-http-requests-in-python-4ec75badabed

class Crawler():
    def __init__(self):
        self._urls = []
        self._total_dict = dict()
        self._header_field_dict = defaultdict(list)
        self._error_list = []
    
    def get_urls(self):
        with open('top-1m.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, line in enumerate(reader):
                if i >= 10:
                    break
                self._urls.append('http://www.'+line[1])
    
    def get_subdomain_urls(self):
        return
    
    def run_crawl(self):
        for url in self._urls:
            print(url)
            response = requests.get(url)
            if response.status_code != 200:
                self._error_list.append((url, response.status_code))
                
            self._total_dict[url] = response.headers
            for header in response.headers:
                self._header_field_dict[header].append(response.headers[header])
    
    def print_urls(self):
        print(len(self._urls)) 
      
    def print_contents(self):
        # print(self._total_dict)
        # print(self._header_field_dict)
        print(self._error_list)
    
    def print_count(self):
        for field in self._header_field_dict:
            print(field, len(self._header_field_dict[field]))

crawl = Crawler()
crawl.get_urls()
# crawl.print_urls()
crawl.run_crawl()
# crawl.print_contents()
crawl.print_count()
crawl.print_contents()