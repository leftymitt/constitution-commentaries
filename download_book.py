#! /usr/bin/env python3

from bs4 import BeautifulSoup as bs
from bs4 import Comment
#  from html2text import html2text
import urllib3
import re
import os


def download_page(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = bs(response.data, "lxml")
    return soup


def parse_toc(soup):
    rows = soup.find_all('tr')
    book = {
        "url": [],
        "volume": [],
        "book": [],
        "booktitle": [],
        "chapter": [],
        "chaptertitle": []
    }
    volumeidx = 0
    bookidx = 0
    temp = ""
    newbook = False
    chapteridx = 1
    for row in rows:
        tdata = row.find_all('td')
        if len(tdata) == 1:
            if re.search(r'VOLUME', tdata[0].text):
                volumeidx += 1
                bookidx = 0
            if re.search(r'BOOK', tdata[0].text):
                bookidx += 1
                newbook = True
            elif newbook == True:
                temp = tdata[0].text.strip().title()
                newbook = False
        if len(tdata) == 7:
            book["url"].append(tdata[0].a["href"])
            book["volume"].append(volumeidx)
            book["book"].append(bookidx)
            book["booktitle"].append(temp)
            book["chapter"].append(chapteridx)
            book["chaptertitle"].append(re.sub('\t|\n', '', tdata[4].text))
            chapteridx += 1
    return book


def generate_toc(book):
    html       = '<div class="uk-panel uk-panel-box">\n'
    html      += '  <h3 class="uk-panel-title">Table of Contents</h3>\n'
    vol1html   = '  <ul class="uk-nav-side uk-nav" data-uk-nav>\n'
    vol1html  += '    <li class="uk-nav-header">Volume 1</li>\n'
    book1html  = '    <li class="uk-parent">\n'
    book1html += '      <ul class="uk-nav-sub">\n'
    book1html += '        <li class="uk-nav-header">Book 1: ' + str(book["booktitle"][0]) + '</li>\n'
    book2html  = '    <li class="uk-parent">\n'
    book2html += '      <ul class="uk-nav-sub">\n'
    book2html += '        <li class="uk-nav-header">Book 2: ' + str(book["booktitle"][1]) + '</li>\n'
    book3html  = '    <li class="uk-parent">\n'
    book3html += '      <ul class="uk-nav-sub">\n'
    book3html += '        <li class="uk-nav-header">Book 3: ' + str(book["booktitle"][2]) + '</li>\n'
    vol2html   = '  <ul class="uk-nav-sub">\n'
    vol2html  += '    <li class="uk-nav-header">Volume 3</li>\n'
    vol3html   = '  <ul class="uk-nav-sub">\n'
    vol3html  += '    <li class="uk-nav-header">Volume 3</li>\n'
    for idx in range(0, len(book["volume"])):
        if book["volume"][idx] == 1:
            if book["book"][idx] == 1:
                book1html += '        <li><a href="#">Ch. ' + str(book["chapter"][idx]) + ': ' + str(book["chaptertitle"][idx]) + '</a></li>\n'
            elif book["book"][idx] == 2:
                book2html += '        <li><a href="#">Ch. ' + str(book["chapter"][idx]) + ': ' + str(book["chaptertitle"][idx]) + '</a></li>\n'
            elif book["book"][idx] == 3:
                book3html += '        <li><a href="#">Ch. ' + str(book["chapter"][idx]) + ': ' + str(book["chaptertitle"][idx]) + '</a></li>\n'
        elif book["volume"][idx] == 2:
            vol2html  += '    <li><a href="#">Ch. ' + str(book["chapter"][idx]) + ': ' + str(book["chaptertitle"][idx]) + '</a></li>\n'
        elif book["volume"][idx] == 3:
            vol3html  += '    <li><a href="#">Ch. ' + str(book["chapter"][idx]) + ': ' + str(book["chaptertitle"][idx]) + '</a></li>\n'
    book1html += '      </ul>\n'
    book1html += '    </li>\n'
    book2html += '      </ul>\n'
    book2html += '    </li>\n'
    book3html += '      </ul>\n'
    book3html += '    </li>\n'
    vol1html  += book1html + book2html + book3html + '  </ul>\n'
    vol2html  += '  </ul>\n'
    vol3html  += '  </ul>\n'
    html += vol1html + vol2html + vol3html
    html += '</div>\n'
    f = open('toc.html', 'w')
    f.write(html)
    f.close()


#
# Parse table of contents
#

prefix = "http://www.constitution.org/js/"

soup = download_page(prefix + "js_005.htm")
book = parse_toc(soup)
generate_toc(book)
