import time
import os
from pathlib import Path
import uvicorn
import django
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

def run_server():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from django.contrib.auth.models import User
    from spezspellz.models.spell import Spell
    User.objects.filter(username="E2ETester").delete()
    Spell.objects.filter(title="E2E Test Ritual").delete()
    try:
        uvicorn.run("config.asgi:application", host="127.0.0.1", port=8000)
    except Exception as err:
        print(err.with_traceback())

def find(browser, selector):
    return browser.find_element(by=By.CSS_SELECTOR, value=selector)

def findAll(browser, selector):
    return browser.find_elements(by=By.CSS_SELECTOR, value=selector)

def wait():
    time.sleep(0.5)

def register(browser):
    element = find(browser, "[name='username']")
    element.send_keys("E2ETester")
    wait()
    element = find(browser, "[name='password1']")
    element.send_keys("notsosecretpasswd")
    wait()
    element = find(browser, "[name='password2']")
    element.send_keys("notsosecretpasswd")

def login(browser):
    element = find(browser, "[type='submit']")
    element.click()
    wait()
    element = find(browser, "[name='login']")
    element.send_keys("E2ETester")
    wait()
    element = find(browser, "[name='password']")
    element.send_keys("notsosecretpasswd")
    wait()
    element = find(browser, "button")
    element.click()

def upload(browser):
    element = find(browser, "#spell_title")
    element.send_keys("E2E Test Ritual")
    wait()
    element = find(browser, "#category")
    element.click()
    wait()
    element = find(browser, "option[value='Ritual']")
    element.click()
    wait()
    element = find(browser, "#add_tag")
    element.click()
    wait()
    for name in ("util", "heal", "protect"):
        element = find(browser, "#add_tag_dlg_search")
        element.clear()
        element.send_keys(name)
        wait()
        elements = findAll(browser, ".tag-search-entry")
        element = next(ele for ele in elements if name in ele.text.lower())
        element.click()
        wait()
    element = find(browser, "#close_add_tag_dlg")
    element.click()
    wait()
    element = find(browser, "#add_noti_btn")
    element.click()
    wait()
    element = find(browser, "#noti_dlg_text")
    element.send_keys("Hey! time for testing.")
    wait()
    element = find(browser, "#noti_dlg_every")
    element.click()
    wait()
    element = find(element, "[value='W']")
    element.click()
    wait()
    element = find(browser, "#noti_dlg_date_time")
    element.send_keys("112620240900P")
    wait()
    element = find(browser, "#ok_noti_dlg")
    element.click()
    wait()
    element = find(browser, "#markdown_input")
    element.clear()
    element.send_keys("# This is a test spell\rWhy don't you have some fun!\r\r- have\r- some\r- fun\r")
    wait()
    element = find(browser, "#thumbnail_file")
    element.send_keys(str(Path("./content/brain_power.jpg").absolute()))
    wait()
    element = find(browser, "#upload_btn")
    element.click()
    wait()
    element = find(browser, "#spell_btn")
    element.click()
    wait()
    element = find(browser, "#bookmark")
    element.click()
    wait()
    element = find(browser, "#comments_btn")
    element.click()
    wait()
    element = find(browser, "#comment_desc")
    element.send_keys("This is my first spell so please be kind.")
    wait()
    element = find(browser, "#submit_comment")
    element.click()

def main():
    process = Process(target=run_server)
    process.start()
    options = Options()
    # options.add_argument("--headless")
    browser = webdriver.Firefox(options=options)
    browser.get("http://127.0.0.1:8000")
    wait()
    element = find(browser, "[src='/assets/login.svg']")
    element.click()
    wait()
    element = find(browser, "p > a")
    element.click()
    wait()
    register(browser)
    wait()
    login(browser)
    wait()
    element = find(browser, "[src='/assets/upload.svg']")
    element.click()
    wait()
    upload(browser)
    try:
        process.join()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
