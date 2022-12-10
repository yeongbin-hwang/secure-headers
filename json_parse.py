from collections import defaultdict
import time
import csv
import json

class Crawler():
    def __init__(self):
        self._urls = []
        self._total_dict = dict()
        self._header_field_dict = defaultdict(list)
        self._policies = {
            'cors',
            'contentsecuritypolicy',
            'contentsecuritypolicy2',
            'stricttransportsecurity',
            'x-frame-options',
            'feature-policy',
            'referrer-policy',
            'permissions-policy',
            'document-policy',
        }
    
    def start(self) -> None:
        self.read_json()
        self.build_field_dict()

    def read_json(self):
        with open("log/response_headers.json", "r") as f:
            self._total_dict = dict(json.loads(f.read()))
            self._urls = list(self._total_dict.keys())
            
    def build_field_dict(self):
        for elem in self._total_dict:
            for header in self._total_dict[elem]:
                self._header_field_dict[header].append(self._total_dict[elem][header])
    
    def print_urls(self):
        print(len(self._urls)) 
    
    def print_count(self):
        self._header_field_dict = dict(sorted(self._header_field_dict.items(), key=lambda item: len(item[1])))
        
        for field in self._header_field_dict:
            print(field, len(self._header_field_dict[field]))
        
        print(len(self._header_field_dict.keys()))

if __name__ == "__main__":
    s = time.perf_counter()
    crawler = Crawler()
    crawler.start()
    crawler.print_count()
    elapsed = time.perf_counter() - s
    print(f"Execution time: {elapsed:0.2f} seconds.")