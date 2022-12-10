import requests
from bs4 import BeautifulSoup as bs

class Crawler():
    def __init__(self):
        self._policies = ( # Supported headers/policies
			"hsts",
			"csp",
			"cors",
			"x_content_type_options",
			"x_xss_protection",
			"x_frame_options",
			"expect_ct",
			"feature_policy",
			"referrer_policy"
		)
    
    def run_crawl(self):
        url = "https://caniuse.com/"
        
        for policy in self._policies:
            policy_url = "%s?search=%s" % (url, policy)
            print(policy_url)
            page = requests.get(policy_url)
            soup = bs(page.text, "html.parser")
            
            elements = soup.select('div.ciu-main-wrap main ciu-feature-list')
            
            print(elements)
            
            break
        
        return
            
crawl = Crawler()
crawl.run_crawl()