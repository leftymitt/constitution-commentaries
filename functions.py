from bs4 import BeautifulSoup as bs
from bs4 import Comment
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
            book["chaptertitle"].append(re.sub('\t', '', re.sub('\n', ' ', tdata[4].text)))
            chapteridx += 1
    return book


def download_original(prefix, book):
    http = urllib3.PoolManager()
    for idx in range(0, len(book["url"])):
        print("downloading chapter " +
              str(book["chapter"][idx]) + " - " + book["chaptertitle"][idx])
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
        outfile = str(book["chapter"][idx]).zfill(2)  + "-" + re.sub('[-\s]+', '-', re.sub(
            '[^\w\s-]', '', book["chaptertitle"][idx]).strip().lower()) + ".html"
        with open(outdir + outfile, "wb") as f:
            f.write(response.data)
        response.release_conn()


def generate_toc(book):
    html       = '<div class="uk-panel uk-panel-box">\n'
    html      += '  <h3 class="uk-panel-title">table of contents</h3>\n'
    html      += '  <hr>\n'
    vol1html   = '  <ul class="uk-nav uk-nav-side">\n'
    vol1html  += '    <li class="uk-nav-header">volume 1</li>\n'
    vol1html  += '  </ul>\n'
    vol1html  += '  <ul class="uk-nav uk-nav-side uk-margin-small-left">\n'
    book1html  = '    <li class="uk-nav-header">book 1: ' + str(list(set(book["booktitle"]))[0]).strip().lower() + '</li>\n'
    book2html  = '    <li class="uk-nav-header">book 2: ' + str(list(set(book["booktitle"]))[1]).strip().lower() + '</li>\n'
    book3html  = '    <li class="uk-nav-header">book 3: ' + str(list(set(book["booktitle"]))[2]).strip().lower() + '</li>\n'
    vol2html   = '  <ul class="uk-nav uk-nav-side">\n'
    vol2html  += '    <li class="uk-nav-header">volume 2</li>\n'
    vol2html  += '  </ul>\n'
    vol2html  += '  <ul class="uk-nav uk-nav-side">\n'
    vol3html   = '  <ul class="uk-nav uk-nav-side">\n'
    vol3html  += '    <li class="uk-nav-header">volume 3</li>\n'
    vol3html  += '  </ul>\n'
    vol3html  += '  <ul class="uk-nav uk-nav-side">\n'
    for idx in range(0, len(book["volume"])):
        chaptertitle = str(book["chaptertitle"][idx]).strip().lower()
        chapterurl = str(book["chapter"][idx]).zfill(2)  + "-" + re.sub('[-\s]+', '-', re.sub('[^\w\s-]', '', book["chaptertitle"][idx]).strip().lower()) + "/"
        if book["volume"][idx] == 1:
            if book["book"][idx] == 1:
                book1html += '    <li><a href="vol1/book1/' + chapterurl + '">ch ' + str(book["chapter"][idx]) + ': ' + chaptertitle + '</a></li>\n'
            elif book["book"][idx] == 2:
                book2html += '    <li><a href="vol1/book2/' + chapterurl + '">ch ' + str(book["chapter"][idx]) + ': ' + chaptertitle + '</a></li>\n'
            elif book["book"][idx] == 3:
                book3html += '    <li><a href="vol1/book3/' + chapterurl + '">ch ' + str(book["chapter"][idx]) + ': ' + chaptertitle + '</a></li>\n'
        elif book["volume"][idx] == 2:
            vol2html  += '    <li><a href="vol2/' + chapterurl + '">ch ' + str(book["chapter"][idx]) + ': ' + chaptertitle + '</a></li>\n'
        elif book["volume"][idx] == 3:
            vol3html  += '    <li><a href="vol3/' + chapterurl + '">ch ' + str(book["chapter"][idx]) + ': ' + chaptertitle + '</a></li>\n'
    vol1html  += book1html + book2html + book3html + '  </ul>\n'
    vol2html  += '  </ul>\n'
    vol3html  += '  </ul>\n'
    html += vol1html + '  <hr>\n'
    html += vol2html + '  <hr>\n'
    html += vol3html
    html += '</div>\n'
    outdir = "revised/"
    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)
    f = open(outdir + 'toc.html', 'w')
    f.write(html)
    f.close()

def clean_html(html):
    # strip out <script>, <style>, and other tags from the html
    for tag in html.findAll(True):
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

    [tag.decompose() for tag in html("script")]
    [tag.decompose() for tag in html("noscript")]
    [tag.decompose() for tag in html("style")]
    for match in html.findAll('span'):
        match.replaceWithChildren()
    for comment in html.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    return html


def parse_full_section(content):
    print("Printing full section.")
    [tag.decompose() for tag in content("center")]
    [text, footnotes, etc] = content.prettify().split("<hr/>")
    text = re.sub("<font>|</font>|  +| *<div.*>|</div>", "", text)
    footnotes = re.sub("<font>|</font>|  +|<div .*>|</div>", "", footnotes)
    #  footnotes = [re.sub('\n+', ' ', item.text.strip().rstrip())
    #               for item in bs(footnotes, 'lxml').findAll('p')]
    footnotes = [re.sub('\n+', '', item.text.strip().rstrip())
                 for item in bs(footnotes, 'lxml').findAll('p')]

    temp = []
    for footnote in footnotes:
        if re.match('^\d+. ', footnote):
            temp.append(footnote)
        else:
            temp[-1] += ' ' + footnote
    footnotes = temp

    for idx in range(0, len(footnotes)):
        footnotenum = "{0:0>3}".format(
            int(re.findall(r'^ *\d+', footnotes[idx])[0].strip()))
        footnotes[idx] = re.sub('^\d+ *\. ', '<a id="%s"></a>' %
                                footnotenum, footnotes[idx])
    return text, footnotes


def parse_end_section(content):
    print("Printing end summary section.")
    [tag.decompose() for tag in content("center")]
    [text, footnotes] = content.prettify().split("<hr/>")
    text = re.sub("<font>|</font>|  +| *<div.*>|</div>", "", text)
    footnotes = ""
    return text, footnotes


def parse_single_section(section, text, footnotes, footnotecount):
    temp = re.split('(?:<p>\n *|<b>\n *|<b>\n *</b>\n *) *__+ *(?:</b>\n *|</p> *|<br/>\n)', section)
    if len(temp) == 1:
        temp = re.split('(?:<p>\n *|<b>\n *|<b>\n *</b>\n *) *__+ *(?:\n{2,}|\n |\t |</b>\n *|</p> *|<br/>\n)', section) # 337 section 82
    if len(temp) == 1:
        temp = re.split('(?:<p>\n *|<b>\n *|<b>\n *</b>\n *) *__+ *(?:\n\t|</b>\n *|</p> *|<br/>\n)', section) # 204 section 23
    if len(temp) == 1:
        temp = re.split('(?:<p>\n *|<b>\n *|<b>\n *</b>\n *) *__+ *(?:\n{2,}|\n|\t|</b>\n *|</p> *|<br/>\n)', section) # 314 section 21


    if (len(temp) == 2) or (len(temp) == 3):

        # get body text
        body = re.sub('<b>\n + __+\n +</b>\n', '', temp[0])
        body = re.sub('=A7', '§', body)

        # get footer text
        footer = re.sub("<p>|</p>|</b>|<b>|<ol>|</ol>|<ul>|</ul>|<li>|</li>|<div>|</div>", "", temp[1]).strip()
        footer = footer.replace("=09", "") # for 304 section 2
        if len(temp) == 3:
            footer += '<br/>\n ' + re.sub("<p>|</p>|</b>|<b>|<ol>|</ol>|<ul>|</ul>|<li>|</li>|<div>|</div>", "", temp[2]).strip()

        # get the number of references in the main body
        bodycount = len(re.findall("(?:[\.,\?\";:a-z\)\]]|\.\" )\d{1,2}[\) \n]| \d{1,2}\)|<b>\n +\d{1,2}\n +</b>\n +|\d{1,2}$|[a-z]+ \d{1,2} [a-z]+", body)) # for 337 section 54

        # get the number of numbered footnotes in the footer (excludes carryover text from previous footnote from count)
        listcount = len(re.findall('(^\d{1,2} |\n\t *\d{1,2} |<br/>\n +\d{1,2} |(?:\n +){3}\d{1,2})', footer)) # for 309 section 24
        if bodycount != 0 and listcount == 0: # for 338 section 10
            listcount = len(re.findall('(^\d{1,2} |\n\t *\d{1,2} |<br/>\n +\d{1,2} |(?:\n +){2}\d{1,2})', footer))

        #  # commented out below to fix 304 section 23
        #  if bodycount == listcount == 0: # not sure what this is for...
        #      footer = ""
        #      body += re.sub(r'<b>[\s\s]+</b>\n', '', temp[1]).strip()

        newfootnotes = [""]
        temp = list(filter(None, [ item.strip() for item in re.split('\n\t|<br/>\n|(?:\n +){3,}', footer) ]))
        if len(temp) == 1 and bodycount == listcount > 0: # parser needed for 314 section 39, so give it its own logic
            temp = list(filter(None, [ item.strip() for item in re.split('\t', footer) ])) # this MUST match the parser for newcount

        for item in temp:
            if re.match("^\d{1,2}[ \n]", item):
                if newfootnotes[-1]:
                    newfootnotes.append(item)
                else:
                    newfootnotes[-1] += " " + item
            else:
                newfootnotes[-1] += " " + item
        footercount = len(newfootnotes)
        iscarryover = False

        # moved down becauser of errors caused by parsing this earlier in 336 section 46
        if bodycount > 0 and listcount != bodycount and listcount != footercount: # not tested to see if it breaks compatibility with 314 section 39
            newcount = len(re.findall('(^\d{1,2} |\t\d{1,2})', footer))
            if newcount == bodycount:
                listcount = newcount
            else: # 314 section 127 needs a space between \t and \d
                newcount = len(re.findall('(^\d{1,2} |\t \d{1,2})', footer))
                if newcount == bodycount:
                    listcount = newcount

        # when everything is just peachy
        if listcount == footercount and footercount == bodycount and bodycount == listcount:
            print("all good:\t\tbody=" + str(bodycount) +
                  "\tlist=" + str(listcount) + "\tfooter=" + str(footercount))

        # when an enumerated item gets appended to preceding carryover text
        elif bodycount == footercount and footercount == listcount + 1:
            iscarryover = True
            newfootnotes[0:1] = re.split("\n\t", newfootnotes[0])
            print("mismatch: type 1\tbody=" + str(bodycount) +
                  "\tlist=" + str(listcount) + "\tfooter=" + str(footercount))

        # when there is only preceding carryover text
        elif listcount == bodycount and footercount == listcount + 1:
            iscarryover = True
            print("mismatch: type 2\tbody=" + str(bodycount) +
                  "\tlist=" + str(listcount) + "\tfooter=" + str(footercount))

        # when the footer lists a reference not found in the body. (need to match
        # reference number in text to the one in the body).
        elif listcount == footercount and listcount == bodycount + 1:
            print("mismatch: type 3\tbody=" + str(bodycount) +
                  "\tlist=" + str(listcount) + "\tfooter=" + str(footercount))
            temp = []
            #  bodyrefs = re.findall("[\.,\?\";]\d[\) |\n]", body) # type 1 and 2
            bodyrefs = re.findall("(?:[\.,\?\";:a-z\]]|\.\" )\d{1,2}[\) \n]| \d{1,2}\)|<b>\n +\d+\n +</b>\n +", body)
            for bodyref in bodyrefs:
                bodyrefnum = int(re.findall('\d', bodyref)[0])
                for newfootnote in newfootnotes:
                    footrefnum = int(re.findall(
                        r'^\D*(\d+)', newfootnote)[0])
                    if footrefnum == bodyrefnum:
                        temp.append(newfootnote.rstrip().strip())
                    else:
                        continue
            newfootnotes = temp

        # print any mismatch
        else:
            print("mismatch unknown:\tbody=" + str(bodycount) +
                  "\tlist=" + str(listcount) + "\tfooter=" + str(footercount))

        # format text and append to document
        if iscarryover:
            footnotes[-1] = footnotes[-1].rstrip().strip()
            footnotes[-1] += " " + newfootnotes[0]
            del newfootnotes[0]
            iscarryover = False

        for newfootnote in newfootnotes:
            numstring = re.findall(r'^\D*(\d+)', newfootnote)
            if numstring:
                footrefnum = int(numstring[0])
                body = re.sub(r'([\.,\?\";])%d([\) |\n])' % footrefnum,
                              r'\1<sup><a href="#%d">%d</a></sup>\2' % (footnotecount, footnotecount), body)
                newfootnote = re.sub(
                    r'^\D*%d ' % footrefnum, r'<a id="%d"></a> ' % footnotecount, newfootnote)
                footnotecount += 1
            footnotes.append(newfootnote)
        text += body

    else:
        print("no footnotes?")
        print(temp)
        body = re.sub('=A7', '§', temp[0])
        text += body

    # clean up tags
    soup = bs(text, "html.parser")
    for x in soup.find_all():
        if len(x.text) == 0:
            x.extract()
        elif x.text == '\n':
            x.extract()
    text = soup.prettify()
    text = text.replace("/p&gt;", "")
    text = text.replace("p&gt;", "")
    text = text.replace("&lt;p", "")
    return text, footnotes, footnotecount


def parse_chapter(soup):
    content = soup.find("div", {"id": "stylesheet_body"})
    content = clean_html(content)

    # when chapter has all text at top and all footnotes listed at the bottom
    if len(content.prettify().split("<hr/>")) == 3:
        [text, footnotes] = parse_full_section(content)

    # separare rule for concluding remarks section
    elif len(content.prettify().split("<hr/>")) == 2 and content.find("h3").text == 'CHAPTER XLV.':
        [text, footnotes] = parse_end_section(content)

    # when chapter text and footnotes are split into several sections
    else:
        # exceptions needed for pages 88 (rhode island), 130 (georgia), and
        # 144 (general review II)
        sections = re.split(r'</center>', content.prettify())
        del sections[0]
        sections = [item.split("<center>")[0].strip() for item in sections]
        sections = list(filter(None, [ item.strip() for item in sections ]))
        sections = [ re.split(r'[<p>\n +]?<b>\n +[0-9]+\t [A-Z ]+.\t \[B(?:ook|OOK) [A-Z\.]+\n +</b>\n +[</p>\n +]?', section) for section in sections ]
        sections = [ item for section in sections for item in section ]

        text = ""
        footnotes = []
        footnotecount = 1
        for sectionidx in range(0, len(sections)):
            print("\nsection " + str(sectionidx))
            [text, footnotes, footnotecount] = parse_single_section(
                sections[sectionidx], text, footnotes, footnotecount)

    return text, footnotes


def generate_chapter(text, footnotes, book, idx):
    outdir = "revised/"
    if book["book"][idx] != 0:
        outdir += "vol" + \
            str(book["volume"][idx]) + "/book" + \
            str(book["book"][idx]) + "/"
    else:
        outdir += "vol" + str(book["volume"][idx]) + "/"

    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    outfile = str(book["chapter"][idx]).zfill(2) + "-" + re.sub('[-\s]+', '-', re.sub('[^\w\s-]', '', book["chaptertitle"][idx]).strip().lower()) + ".html"

    html = '---\n'
    html += 'title: "chapter ' + \
        str(book["chapter"][idx]) + ': ' + \
        book["chaptertitle"][idx].strip().lower() + '"\n'
    html += 'layout: post\n'
    html += '---\n\n'
    html += '<div class="uk-article">\n' + text + '</div>\n'
    if len(footnotes) > 0:
        html += '<hr>\n'
        html += '<div class="uk-article-meta">\n'
        html += '<ol>\n'
        for footnote in footnotes:
            html += '<li>' + footnote + '</li>\n'
        html += '</ol>\n'
        html += '</div>\n'

    f = open(outdir + outfile, "w")
    f.write(html)
    f.close()

