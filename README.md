PublishingTools
===============

Some simple, lightweight scripts for converting one document format to another.

Files:

GenerateGitbook.py (Python 2.x): Run from the command line, accepts a markdown filename as an argument, then parses it into the file/folder structure required by GitBook, including SUMMARY.md file. Initialize git in the main folder, and it is immediately ready to publish to GitBook. Especially handy if you have a single pandoc-generated markdown file that you'd like to publish via GitBook.
> Note: 
>       Assumes chapter headings indicated by "=" and section headings by "-" markdown format.
>       Rewrites any markdown superscripts (e.g. ^...^) to html superscripts (e.g. <sup>...</sup>)

***Usage: python GenerateGitbook.py "MarkdownFileName.md"***

Txt2LaTex.py (Python 2.x): Run from the command line, accepts the name of a text file, a running hed to look for, and an optional "endnote location"; outputs a largely corrected/escaped .tex file, including detecting and linking footnotes to said endnote locations (or "#endnotes" by default), with a preference for false positives. 
Files will still need to have chapter/section heading tags and graphics manually added, but a reasonable amount of kruft brought in by copying text from a .pdf (yikes) is eliminated. Unlikely to be very useful to anyone else.

***Usage: python Txt2LaTeX.py "TextFileName.txt" "Random running hed" -endnote_loc "endnotes_1"***
