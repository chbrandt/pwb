import base64
import time
import json
import contextlib
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

ra = 194.046670
dec = -5.789310
url = "https://tools.ssdc.asi.it/SED/sed.jsp?ra={ra!s}&dec={dec!s}".format(ra=ra,dec=dec)

options = Options()
options.headless = True
# driver = webdriver.Firefox(options=options)
with contextlib.closing(webdriver.Firefox(options=options)) as driver:
    driver.get(url)
    btn_loaddata = driver.find_element_by_id('button_loaddata')
    btn_loaddata.send_keys(Keys.ENTER)
    driver.execute_script('showAllData()')

    for i in range(10):
        try:
            p = driver.find_element_by_xpath('//p[contains(text(), "Source Data")]')
            # ps = driver.find_elements_by_xpath('//p[contains(text(), "Source Data")]')
            link_csv = driver.find_element_by_xpath('//a[text()="csv"]')
            # link_csvs = driver.find_elements_by_xpath('//a[text()="csv"]')
            print("Page loaded.")
            break
        except:
            print("Page not loaded. Retrying (:d)".format(i))
            time.sleep(1)
        finally:
            print('finally')

    download_url = link_csv.get_attribute('href')
    print(download_url)

    driver.execute_script("""
        window.file_contents = null;
        var xhr = new XMLHttpRequest();
        xhr.responseType = 'blob';
        xhr.onload = function() {
            var reader  = new FileReader();
            reader.onloadend = function() {
                window.file_contents = reader.result;
            };
            reader.readAsDataURL(xhr.response);
        };
        xhr.open('GET', %(download_url)s);
        xhr.send();
    """.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ') % {
        'download_url': json.dumps(download_url),
    })

    print('Looping until file is retrieved')
    downloaded_file = None
    while downloaded_file is None:
        # Returns the file retrieved base64 encoded (perfect for downloading binary)
        downloaded_file = driver.execute_script('return (window.file_contents !== null ? window.file_contents.split(\',\')[1] : null);')
        if not downloaded_file:
            print('\tNot downloaded, waiting...')
            time.sleep(0.5)
    print('Done')

    fp = open('yay.txt','wb')
    fp.write(base64.b64decode(downloaded_file))
    fp.close()

    # driver.close() # close web browser, or it'll persist after python exits.
