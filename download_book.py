#! /usr/bin/env python3

import os

import functions as fn


#
# Parse table of contents
#

prefix = "http://www.constitution.org/js/"

soup = fn.download_page(prefix + "js_005.htm")
book = fn.parse_toc(soup)
fn.generate_toc(book)

for idx in range(0, len(book["url"])):
    print("downloading chapter " +
          str(book["chapter"]) + ": " + book["chaptertitle"].strip().lower())
    soup = fn.download_page(book["url"][idx])
    [text, footnotes] = fn.parse_chapter(soup)
    print("parsing chapter...")
    fn.generate_chapter(text, footnotes, book, idx)
    print("generating chapter...")

print("done.")
