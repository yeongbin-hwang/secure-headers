from selenium import webdriver
import chromedriver_autoinstaller
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
        chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        
        try:
            driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe')   
        except:
            chromedriver_autoinstaller.install(True)
            driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe')
        
        def expand_shadow_element():
            shadow_root = driver.execute_script('''
                return document.querySelector('ciu-feature-list').shadowRoot.querySelector('div.feature-list-wrap')
            ''')
            return shadow_root
        
        url = "https://caniuse.com/"
        driver.implicitly_wait(3)
        
        for policy in self._policies:
            policy_url = "%s?search=%s" % (url, policy)
            driver.get(policy_url)
            
            shadow_root = expand_shadow_element()

            print(shadow_root)            
            # root1 = driver.find_element("css selector", "#shadow-root")
            # shadow_root1 = root1.shadow_root
            
            # root2 = shadow_root1.find_element("css selector", "#shadow-root")
            # shadow_root2 = root2.shadow_root
            
            # root3 = shadow_root2.find_element("css selector", "#shadow-root")
            # shadow_root3 = expand_shadow_element(root3)
            while(True):
                pass
        return
        # for policy in self._policies:
        #     policy_url = "%s?search=%s" % (url, policy)
        #     print(policy_url)
        #     page = requests.get(policy_url)
        #     soup = bs(page.text, "html.parser")
            
        #     elements = soup.select('div.ciu-main-wrap main ciu-feature-list')
            
        #     print(elements)
            
        #     break
        
        # return
            
crawl = Crawler()
crawl.run_crawl()