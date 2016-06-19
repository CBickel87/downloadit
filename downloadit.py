import sys
import os
import re
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Gives a nice visual percentage for downloading
def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize:  # near the end
            sys.stderr.write("\n")
    else:  # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))


def cleanstr(title, i):
    newtitle = ''.join(e for e in title if e.isalnum())
    newtitle = (("%02d_" % i) + newtitle + '.mp4')
    print(newtitle)
    return newtitle

webpage = input('Paste the URL of the course here.')
m1 = re.search('part', webpage, flags=re.IGNORECASE)
if m1:
    pass
else:
    webpage = webpage + 'part00.html'


browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

browser.get('https://www.mainwebsite.com/')

# Click 'Sign In'
linkElem = browser.find_element_by_link_text('Sign In')
linkElem.click()

# Enter credentials
emailElm = browser.find_element_by_id('id_email')
emailElm.send_keys('username@domain.com')
passwordElem = browser.find_element_by_id('id_password1')
passwordElem.send_keys('password')
passwordElem.submit()

# Go to page & get total video count
browser.get(webpage)
wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id=\"container\"]")))
amount = browser.find_element_by_xpath("//*[@id=\"container\"]/div[2]/section/h1").text

# Search for 2 or more digits in total video count
m2 = re.search(r'(\d){2,}', amount)
x = int(m2.group())

# Splits off 'part'
pagesplit = re.split(("part"), webpage)
webpage = pagesplit[0]


for i in range(x):
    browser.get(webpage + 'part{}.html'.format("%02d" % i))

    # Wait until javascript loads. Select & switch to iFrame
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#js-kaltura-player-region_ifp')))
    iframe = browser.find_element_by_css_selector('#js-kaltura-player-region_ifp')
    browser.switch_to_frame(iframe)

    # Wait until javascript loads. Select and get Src Video URL
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#pid_js-kaltura-player-region")))
    url = browser.find_element_by_css_selector("#pid_js-kaltura-player-region").get_attribute("src")

    # Get "Title" tag text
    title = browser.find_element_by_css_selector("head > title").get_attribute('text')

    # Clean title. Remove whitespace, ':', and '?' characters
    newtitle = cleanstr(title, i)

    # If the file name exists pass otherwise download it
    if os.path.isfile(newtitle):
        pass
    else:
        urlretrieve(url, newtitle, reporthook)

browser.close()

