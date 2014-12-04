PublishingTools
===============

Some simple, lightweight scripts for converting one document format to another.

Files:

GenerateGitbook.py (Python 2.x): Run from the command line, accepts a markdown filename as an argument, then parses it into the file/folder structure required by GitBook, including SUMMARY.md file. Initialize git in the main folder, and it is immediately ready to publish to GitBook. Especially handy if you have a pandoc-generated markdown file that you'd like to publish via GitBook.
> Note: 
>       Assumes chapter headings indicated by "=" and section headings by "-" markdown format.
>       Treats markdown superscripts (e.g. ^...^) as endnote references, rewriting to HTML and linking to "endnotes/README"  

***Usage: python GenerateGitbook.py "Pandoc_Markdown_Output.md"***

Txt2LaTex.py (Python 2.x): Run from the command line, accepts the name of a text file, a running hed to look for, and an optional "endnote location"; outputs a largely corrected/escaped .tex file, including detecting and linking footnotes to said endnote locations (or "#endnotes" by default), with a preference for false positives. 
Files will still need to have chapter/section heading tags and graphics manually added, but a reasonable amount of kruft brought in by copying text from a .pdf (yikes) is eliminated. Unlikely to be very useful to anyone else.

***Usage: python Txt2LaTeX.py "TextFileName.txt" "Random running hed" -endnote_loc "endnotes_1"***

CreateRigthRail.py (Python 2.x): Run from the command line, accepts the name of an html file, and generates two files: _web.html which contains includes rewritten header anchors above each chapter heading to provide clean jumps when the page has a floating header, nad _rr.html, which is a link list to all chapters in the file. Good for porting to WP with a custom-HTML right widget for navigation through sections.

***Usage: python CreateRightRail.py "Pandoc_HTML_Output.html"***
