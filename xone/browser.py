import pandas as pd

import requests
import time
import os
import shutil

from xone import logs, files
from collections import namedtuple
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import \
    NoSuchElementException, ElementClickInterceptedException


BROWSERS = {
    'firefox': (webdriver.Firefox, webdriver.FirefoxOptions()),
    'chrome': (webdriver.Chrome, webdriver.ChromeOptions()),
}

PageSource = namedtuple('PageSource', ['source', 'soup'])


def get_text(elem) -> str:
    """
    Get text from element
    """
    for line in elem.find_all('br'): line.replace_with('\n')
    return elem.text.strip()


def to_text(soup, elem_name, func: callable = None) -> list:
    """
    Get list of texts from row data
    """
    return [
        func(get_text(elem=elem)) if callable(func) else get_text(elem=elem)
        for elem in soup.select(elem_name)
    ]


def get_rel_path(folder: str, home=os.path.expanduser('~')) -> str:
    """
    Get relative path from home folder
    """
    return (
        f'{home}/{folder}'
        .replace('/', os.path.sep)
        .replace('\\', os.path.sep)
    )


def get_browser(browser, headless=True, download='', *args):
    """
    Get browser

    Args:
        browser: one of firefox and chrome
        headless: whether to show browser
        download: folder to download files to - relative to ~/Downloads
                  files in the folder WILL BE REMOVED when browser is returned
    """
    br, br_opt = BROWSERS[browser]
    if headless: br_opt.add_argument('--headless')
    br_opt.add_argument('--disable-gpu')
    br_opt.add_experimental_option('excludeSwitches', ['enable-logging'])
    if download:
        dl_path = get_rel_path(folder=f'Downloads/{download}')
        if files.exists(dl_path): shutil.rmtree(dl_path, ignore_errors=True)
        files.create_folder(dl_path)
        br_opt.add_experimental_option('prefs', {
            'download.default_directory': dl_path,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
        })
    for arg in args: br_opt.add_argument(arg)
    return br(options=br_opt)


def page_source(
        url: str,
        browser: str = '',
        click: str = '',
        headless=True,
        *args
) -> PageSource:
    """
    Page source from url

    Args:
        url: url
        browser: one of firefox, chrome and ie
        click: element to click - useful for scroll down page
               will use browser if given - default browser Chrome
        headless: whether to show browser

    Returns:
        PageSource
    """
    logger = logs.get_logger(page_source)

    if click and (not browser): browser = 'chrome'
    if not browser:
        page = requests.get(url)
        if page.status_code == 200:
            return PageSource(
                source=page.content,
                soup=BeautifulSoup(page.content, 'lxml'),
            )
        else:
            logger.warning(f'Invalid status code {page.status_code} for url:\n{url}')
            return PageSource(source='', soup=BeautifulSoup('', 'lxml'))

    if browser not in BROWSERS:
        raise LookupError(
            f'Cannot find browser: {browser}.\n'
            f'Valid browsers: {list(BROWSERS.keys())}.'
        )

    with get_browser(browser, headless=headless, *args) as driver:
        driver.get(url=url)
        if click:
            try:
                driver.find_element_by_xpath(click).click()
            except (NoSuchElementException, ElementClickInterceptedException) as e:
                logger.error(e)
            time.sleep(1)
        return PageSource(
            source=driver.page_source,
            soup=BeautifulSoup(driver.page_source, 'lxml'),
        )


def read_html(
        soup: BeautifulSoup,
        tag: str,
        attrs: dict,
        cols: list,
        **kwargs
) -> pd.DataFrame:
    """
    Read table from soup instead of the whole web page
    """
    table = soup.find_all(tag, attrs=attrs)
    if not table: return pd.DataFrame()
    tb = pd.read_html(table[0].prettify(), **kwargs)
    if not tb: return pd.DataFrame()
    return tb[0].rename(columns=dict(zip(range(len(cols)), cols)))
