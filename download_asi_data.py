import base64
import time
import json
import re
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
    print("Opening session: '{}'".format(url))
    driver.get(url)
    print('..done.')
    btn_loaddata = driver.find_element_by_id('button_loaddata')
    print("Refreshing data..")
    btn_loaddata.send_keys(Keys.ENTER)
    print("..done")
    print("Asking for data page..")
    driver.execute_script('showAllData()')
    print("..waiting page to load..")
    for i in range(10):
        try:
            # p = driver.find_element_by_xpath('//p[contains(text(), "Source Data")]')
            ps = driver.find_elements_by_xpath('//p[contains(text(), "Source Data")]')
            # link_csv = driver.find_element_by_xpath('//a[text()="csv"]')
            link_csvs = driver.find_elements_by_xpath('//a[text()="csv"]')
            print("..page loaded.")
            break
        except:
            print("Page not loaded. Retrying {:d}".format(i))
            time.sleep(1)
        finally:
            print('Finally, move to grab the data :)')

    assert len(ps) == len(link_csvs)
    n_sets = len(ps)
    for i in range(n_sets):
        print("Fetching dataset {:d}/{:d}".format(i,n_sets))
        p = ps[i]
        link_csv = link_csvs[i]
        catalog = p.text.replace('Source Data :','').strip()
        print(catalog, link_csv.text)
        download_url = link_csv.get_attribute('href')

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

        output_filename = '{catalog!s}.csv'.format(catalog=re.sub('\s+','_',catalog))
        fp = open(output_filename,'wb')
        fp.write(base64.b64decode(downloaded_file))
        fp.close()

    # driver.close() # close web browser, or it'll persist after python exits.
