
import asyncio
import aiohttp
import time
import csv
import json
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
        true_exception = []
        try:
            with open("example/exception_file.json", "r") as exception:
                exception_list = list(dict(json.loads(exception.read())).keys())
                for elem in exception_list:
                    try:
                        response = requests.get(elem, timeout=1)
                        if response == None:
                            true_exception.append(elem)
                            print(f'[True exception: timeout] {elem}')
                    except:
                        true_exception.append(elem)
                        print(f'[True exception] {elem}')
        except:
            print('[No file: exception file]')
            
        if len(true_exception) != 0:
            self.update_true_exception(true_exception)

    def update_true_exception(self, true_exception):
        true_exception_content = ''
        try:
            with open('example/true_exception_file.json', 'r') as f:
                true_exception_content = f.read()
        except:
            print('[No file: true exception file]')
            
        with open('example/true_exception_file.json', 'w') as f:
            # need to fix
            exception_dict = dict()
            if len(true_exception_content) > 1:
                exception_dict = dict(json.loads(true_exception_content))
            else:
                exception_dict["http://www.microsoftonline.com"] = {"status": "exception"}
            
            for elem in true_exception:
                if elem not in exception_dict:
                    resp_dict = dict()
                    resp_dict["status"] = "exception"
                    exception_dict[elem] = resp_dict
            f.write(json.dumps(exception_dict))

    def eliminate_urls(self):
        duplicate_list = ["http://www.myshopify.com", "http://www.spankbang.com", "http://www.microsoftonline.com"]
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
        
        # set default for continuous json
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
        async with aiohttp.ClientSession(headers=headers, timeout=1) as session:
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