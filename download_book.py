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


def download_book(prefix, book):
    http = urllib3.PoolManager()
    for idx in range(0, len(book["url"])):
        if book["book"][idx] != 0:
            outdir = "original/vol" + \
                str(book["volume"][idx]) + "/book" + \
                str(book["book"][idx]) + "/"
        else:
            outdir = "original/vol" + str(book["volume"][idx]) + "/"
        if not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)
        response = http.request('GET', prefix + book["url"][idx])
        soup = bs(response.data, "lxml")
        outfile = str(book["chapter"][idx]) + " " + \
            book["chaptertitle"][idx] + ".html"
        with open(outdir + outfile, "wb") as f:
            f.write(response.data)
        response.release_conn()


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


def parse_chapter(soup):
    content = soup.find("div", {"id": "stylesheet_body"})

    # strip out <script>, <style>, and other tags from the html
    for tag in content.findAll(True):
        href = None
        name = None
        if 'href' in tag.attrs:
            href = tag['href']
        if 'name' in tag.attrs:
            name = tag['name']
        tag.attrs.clear()
        if href:
            tag['href'] = href
            href = None
        if name:
            tag['id'] = name
            name = None

    [tag.decompose() for tag in content("script")]
    [tag.decompose() for tag in content("noscript")]
    [tag.decompose() for tag in content("style")]
    [tag.decompose() for tag in content("span")]
    for comment in content.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    if len(content.prettify().split("<hr/>")) == 3:
        [tag.decompose() for tag in content("center")]
        [text, footnotes, etc] = content.prettify().split("<hr/>")
        text = re.sub("<font>|</font>|  +| *<div.*>|</div>", "", text)
        footnotes = re.sub("<font>|</font>|  +|<div .*>|</div>", "", footnotes)
        footnotes = [re.sub('\n+', ' ', item.text.strip().rstrip())
                     for item in bs(footnotes, 'lxml').findAll('p')]
    else:
        sections = content.prettify().split("</center>")
        del sections[0]
        sections = [item.split("<center>")[0] for item in sections]

        text = ""
        footnotes = []
        footnotecount = 1
        for sectionidx in range(0, len(sections)):
            temp = re.split('\n *<b>\n *__+\n *</b>\n *', sections[sectionidx])
            if len(temp) == 2:
                # extract text (above the ___) and footer (below the ___)
                body = temp[0]
                footer = bs(re.sub("(<p>\n|</p>\n)", "",
                                   temp[1]), "lxml").find("ul").text
                # get the number of references in the main body
                #  bodycount = len(re.findall("(\.|,|\?|\"|;)\d(\)| |\n)", body))
                bodycount = len(re.findall("[\.,\?\";]\d[\) |\n]", body))
                # get the number of items enumerated in the footer
                #  listcount = len(re.findall("\n *\d .*\n", footer))
                listcount = len(re.findall(
                    '_-_ *\d ', re.sub('\n', ' ', re.sub('(\n\n|\n +\n)', '_-_', footer))))
                # the the number of items (total) in the footer
                newfootnotes = [""]
                temp = list(filter(None, [item.strip()
                                          for item in re.split("\n +\n", footer)]))
                for item in temp:
                    if re.match("^\d ", item):
                        if newfootnotes[-1]:
                            newfootnotes.append(item)
                        else:
                            newfootnotes[-1] += " " + item
                    else:
                        newfootnotes[-1] += " " + item
                footercount = len(newfootnotes)
                iscarryover = False
                # print any mismatch
                if listcount != footercount or footercount != bodycount or bodycount != listcount:
                    print(str(sectionidx) + ": mismatch\tbody=" + str(bodycount) +
                          "\tlist=" + str(listcount) + "\tfooter=" + str(footercount))
                # when everything is just peachy
                if listcount == footercount and footercount == bodycount and bodycount == listcount:
                    print(str(sectionidx) + ":\t\tbody=" + str(bodycount) +
                          "\tlist=" + str(listcount) + "\tfooter=" + str(footercount))
                # when an enumerated item gets appended to preceding carryover
                # text
                elif bodycount == footercount and footercount == listcount + 1:
                    iscarryover = True
                    newfootnotes[0:1] = re.split("\n\t", newfootnotes[0])
                    print(str(sectionidx) + ": type 1\tbody=" + str(bodycount) +
                          "\tlist=" + str(listcount) + "\tfooter=" + str(footercount))
                # when there is only preceding carryover text
                elif listcount == bodycount and footercount == listcount + 1:
                    iscarryover = True
                    print(str(sectionidx) + ": type 2\tbody=" + str(bodycount) +
                          "\tlist=" + str(listcount) + "\tfooter=" + str(footercount))
                # when the footer lists a reference not found in the body. (need to match
                # reference number in text to the one in the body).
                elif listcount == footercount and listcount == bodycount + 1:
                    temp = []
                    bodyrefs = re.findall("[\.,\?\";]\d[\) |\n]", body)
                    for bodyref in bodyrefs:
                        bodyrefnum = int(re.findall('\d', bodyref)[0])
                        for newfootnote in newfootnotes:
                            footrefnum = int(re.findall(
                                r'^\D*(\d+)', newfootnote)[0])
                            if footrefnum == bodyrefnum:
                                temp.append(newfootnote)
                            else:
                                continue
                    newfootnotes = temp
                    print(str(sectionidx) + ": type 3\tbody=" + str(bodycount) +
                          "\tlist=" + str(listcount) + "\tfooter=" + str(footercount))
                # format text and append to document
                if iscarryover:
                    footnotes[-1] = footnotes[-1].rstrip()
                    footnotes[-1] += " " + newfootnotes[0]
                    del newfootnotes[0]
                    iscarryover = False
                for newfootnote in newfootnotes:
                    footrefnum = int(re.findall(r'^\D*(\d+)', newfootnote)[0])
                    body = re.sub(r'([\.,\?\";])%d([\) |\n])' % footrefnum,
                                  r'\1<sup><a href="#%d">%d</a></sup>\2' % (footnotecount, footnotecount), body)
                    newfootnote = re.sub(
                        r'^%d ' % footrefnum, r'<a id="%d"></a>%d ' % (footnotecount, footnotecount), newfootnote)
                    footnotecount += 1
                    footnotes.append(newfootnote)
                #  text += html2text(body) # strips anchor tags...
                text += body
            else:
                print(str(sectionidx) + ": no footnotes")
                #  body = html2text(body) # strips anchor tags...
                text += body
    return text, footnotes


#
# Parse table of contents
#

prefix = "http://www.constitution.org/js/"

soup = download_page(prefix + "js_005.htm")
book = parse_toc(soup)
generate_toc(book)

soup = download_page(prefix + "js_336.htm")
[ text, footnotes ] = parse_chapter(soup)

#  for idx in range(0, len(book["url"])):
#      soup = download_page(book["url"][idx])
#      [ text, footnotes ] = parse_chapter(soup)
#      generate_chapter(text, footnotes, book)
