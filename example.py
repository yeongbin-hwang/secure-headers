
import asyncio
import aiohttp
import time
import csv
import json
import os
from aiolimiter import AsyncLimiter
import requests

limiter = AsyncLimiter(1, 0.125)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
headers={'User-Agent':USER_AGENT}

class Crawler():
    def __init__(self):
        self._urls = []
        self._all_file = ''
        self._error_file = ''
        self._exception_file = ''

    def get_urls(self):
        with open('log/top-1m.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, line in enumerate(reader):
                if i >= 500:
                    break
                self._urls.append('http://www.'+line[1])

    def find_true_exception(self):
        for filename in os.listdir("example/exception"):
            with open(os.path.join("example/exception", filename), 'r') as f_except:
                exception = dict(json.loads(f_except.read()))
                domain = exception.keys()[0]
                try:
                    response = requests.get(domain, timeout=1, headers=headers)
                    if not response:
                        print(f'[True exception: timeout] {domain}')
                        with open(os.path.join("example/true_exception", filename), 'w') as f_true:
                            f_true.write(json.dumps(exception))
                except:
                    print(f'[True exception] {domain}')
                    with open(os.path.join("example/true_exception", filename), 'w') as f_true:
                        f_true.write(json.dumps(exception))

    def eliminate_urls(self):
        duplicate_list = []
        error_content = ''
        resp_content = ''
        try:
            with open('example/error_file.json', 'r') as error_file:
                error_content = error_file.read()
                # remove , and add
                duplicate_list += list(dict(json.loads(error_content)).keys())
        except:
            print('[No file: error file]')
        try:
            with open('example/response_headers.json', 'r') as resp_file:
                resp_content = resp_file.read()
                duplicate_list += list(dict(json.loads(resp_content)).keys())
        except:
            print('[No file: response file]')
            
        try:
            with open('example/true_exception_file.json', 'r') as exception_file:
                exception_content = exception_file.read()
                duplicate_list += list(dict(json.loads(exception_content)).keys())
        except:
            print('[No file: true exception file]')
        
        new_urls = []
        for url in self._urls:
            if url not in duplicate_list:
                new_urls.append(url)
        self._urls = new_urls
        
        self.restore_file(resp_content[:-1] if len(resp_content) > 2 else '{', error_content[:-1] if len(error_content) > 2 else '{')
        
    def restore_file(self, resp_content, error_content):
        self._error_file = open('example/error_file.json', 'w')
        self._all_file = open('example/response_headers.json', 'w')
        self._exception_file = open('example/exception_file.json', 'w')
        
        # set default
        if error_content == '{': self._error_file.write('''{
            "http://www.myshopify.com": {"status": 403}
            ''')
        else: self._error_file.write(error_content)
        
        if resp_content == '{': self._all_file.write('''{
            "http://www.xxxxx520.com": {
                "Server": "nginx",
                "Date": "Sun, 04 Dec 2022 20:48:37 GMT",
                "Content-Type": "text/html; charset=UTF-8",
                "Content-Length": "7465",
                "Connection": "keep-alive",
                "Vary": "Accept-Encoding, Cookie",
                "Cache-Control": "max-age=3, must-revalidate",
                "Content-Encoding": "gzip",
                "Strict-Transport-Security": "max-age=31536000"
            }
            ''')
        else: self._all_file.write(resp_content)
        # default
        self._exception_file.write('''{
            "http://www.microsoftonline.com": {"status": "exception"}
        ''')
        
    def exit(self):
        self._all_file.write('}')
        self._error_file.write('}')
        self._exception_file.write('}')
        self._all_file.close()
        self._error_file.close()
        self._exception_file.close()
    
    def print_url(self):
        print(len(self._urls))
        
    async def download_pep(self, url, semaphore):
        async with aiohttp.ClientSession(headers=headers) as session:
            await semaphore.acquire()
            async with limiter:
                print(f"Begin downloading {url} {(time.perf_counter() - s):0.4f} seconds")
                try:
                    async with session.get(url) as resp:
                        # content = await resp.read()
                        print(f"Finished downloading {url}")
                        semaphore.release()
                        return resp
                except:
                    semaphore.release()
                    return None


    async def write_to_file(self, url, resp) -> None:
        if resp == None:
            resp_dict = dict()
            resp_dict["status"] = "exception"
            self._exception_file.write(f', "{url}" : {json.dumps(resp_dict)}')
            print('[Exception]')
            return
        
        if resp.status == 200:
            self._all_file.write(f', "{url}" : {json.dumps(dict(resp.headers))}')
        else:
            resp_dict = dict()
            resp_dict["status"] = resp.status
            self._error_file.write(f', "{url}" : {json.dumps(resp_dict)}')
            print('[Error]')

    async def web_scrape_task(self, url, semaphore) -> None:
        content = await self.download_pep(url, semaphore)
        if content == None: 
            await self.write_to_file(url, None)
        else:
            await self.write_to_file(url, content)

    async def main(self) -> None: 
        tasks = []
        semaphore = asyncio.Semaphore(value=10)
        for i, url in enumerate(self._urls):
            tasks.append(self.web_scrape_task(url, semaphore))
        await asyncio.wait(tasks)

if __name__ == "__main__":
    s = time.perf_counter()
    crawler = Crawler()
    crawler.get_urls()
    crawler.find_true_exception()
    crawler.eliminate_urls()
    crawler.print_url()
    # all_file.write('{')
    # error_file.write('{')
    # exception_file.write('{')
    try:
        asyncio.run(crawler.main()) # Activate this line if the code is to be executed in VS Code
        crawler.exit()
    except:
        print('[Run error]')
        crawler.exit()
    # , etc. Otherwise deactivate it.
    # await main()          # Activate this line if the code is to be executed in Jupyter 
    # Notebook! Otherwise deactivate it.
    elapsed = time.perf_counter() - s
    print(f"Execution time: {elapsed:0.2f} seconds.")