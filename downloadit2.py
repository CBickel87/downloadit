import sys
import lxml.html
import re
from urllib.request import urlretrieve
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

save_path = 'E:\\Folder\\Folder\\'


def sign_in():
    browser.get('http://www.urltodownloadfrom/sign_in')
    email_elm = browser.find_element_by_id('user_email')
    email_elm.send_keys('email')
    password_elem = browser.find_element_by_id('user_password')
    password_elem.send_keys('password')
    password_elem.submit()


def get_title():
    content = browser.page_source
    doc = lxml.html.fromstring(content)
    section_title = doc.xpath('//*[@id="lecture_heading"]/text()')
    section_title = ''.join(section_title)
    m1 = re.search(r'S(\d){1,2}L(\d){1,2}', section_title)
    title = m1.group()
    print(title)
    return title


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


def navigate_dl():
    browser.get('https://www.urltodlownloadfrom.com/specificaddress')

    while True:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "body > div.course-mainbar.lecture-content > "
                                                                      "div:nth-child(2) > div.video-options > a")))
        dl_url = browser.find_element_by_css_selector("body > div.course-mainbar.lecture-content > "
                                                      "div:nth-child(2) > div.video-options > a").get_attribute("href")
        next_btn = browser.find_element_by_css_selector("#lecture_complete_button > span")

        title = get_title()

        try:
            dl_extras = browser.find_element_by_css_selector("body > div.course-mainbar.lecture-content > "
                                                             "div:nth-child(4) > div:nth-child(3) > a").get_attribute("href")
            print(dl_extras)
            urlretrieve(dl_extras, save_path + title + '.pptx', reporthook)
        except NoSuchElementException:
            pass

        try:
            print(dl_url)
            urlretrieve(dl_url, save_path+title+'.mp4', reporthook)
            next_btn.click()
        except NoSuchElementException:
            break


def main():
    sign_in()
    navigate_dl()

main()
