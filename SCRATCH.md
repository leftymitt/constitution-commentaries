mismatch key:
 * type 1   = when enumerated item isn't indented correctly and gets wrongly
              appended to previous footnote
 * type 2   = there is carryover text from end of previous section footnotes
 * type 3   = extra footnote that needs to be removed
 * type ??? = citation number in text doesn't match anything in the footer

105:
 - section 4 type 3

116:
 - section 1 type 3
 - section 4 type 2

117:
 - over half the page is broken

204:
 - section 2 type 2
 - section 4 type 2
 - section 6 type 1
 - section 13 ??? (a footnote is missing)
 - section 17 type 2
 - section 23 type 3
 - section 27 type 1

301:
 - section 2 ??? (a footnote is missing)
 - section 5 ??? (fixed with 3x (\n +) for listcount and footer parsing, which
   will break parsing on earlier pages in book 2)
 - section 4 type 3 (extra footnote)

304:
 - section 1 type 2
 - section 2 type 1
 - section 4 type 2
 - section 21-24 type 2
 - section 25 type 3
 - section 26-28 type 2
 - section 32-37 type 2

309:
 - there seem to be tables in the text
 - section 24 type 3 (good)
 - section 35 type 3 (good)
 - section 53 ??? (extra citation in text or footnote is missing)
 - section 94 type 2 (good)
 - section 98 type 2 (good)
 - section 102 type 2 (good)
 - section 103 type 2 (good)
 - section 104 type 2 (good)
 - section 105 ??? (there's  \_+\n in the footer table)
 - section 106 type 2
 - section 107 ??? (there's  \_+\n in the footer table)
 - section 108-125 type 2

314:
 - section 21 (there's a "\_+  \t1 See also 4 Elliot's..." that's not parsed
   correctly)
 - section 127 ???

336:
 - section 10 type 2 (good)
 - section 17 type 2
 - section 19 type 2
 - section 21 type 2
 - section 31 type 2
 - section 45 type 2
 - section 46 type 2

337:
 - section 3 type 2 (good)
 - section 6 ??? (good)
 - section 12 type 2 (good)
 - section 41-46 type 2 (good)
 - section 68 type 2 (good)
 - section 78 ??? (too many citations / footnote is missing)
 - section 81 type 2i
 - section 82 ???
 - section 83-84 type 2

338: centered content breaks the section-splitting code
 - section 1 type 2 (good)
 - section 4-9 type 2 (good)
 - section 10 (good)
 - section 11 ??? broken
 - section 13 type 2 
 - section 16 type 2 (good)
 - section 17 type 2 (good)
 - section 18 broken (lots of centered items)
