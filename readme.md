[![Open Courses](http://www.wikinotes.ca/header.png)](http://www.wikinotes.ca)

Google Docs to Wikicode Converter
=================================

Converts an html file produced by google docs to wikicode (add more?)

Usage instructions
==================

1.  Obtain .html formatted Google Doc with File/Download as../HTML
2.  Run wikicode.py
3.  You will be prompted for the .html input file and the .txt output file to be created
(Since we're betatesting, the input and output files are already set to save time. Scroll down to the bottom of "wikicodify.py" to change the file I/O to your convenience) 

Status
======
*   Works for very simple Google Docs e.g. https://docs.google.com/document/d/1P63dmJHDk_35OVpix5Cd8zHxKaMmi_8Bo9o7Pdkm6M0/edit?hl=en&authkey=CMyc-aYF#
*   Has a Wikidict class that creates a dictionary with wikicode/html element pairs
*   Can convert: 
**  Lists (ordered and unordered) 
**  Tables (defaults to 'class="wikitable" width="100%"')
**  Bold, underlined and italicized text
**  Headers
**  Hyperlinks (ignores bookmarks though)

To do
=====
*   Create a web app that takes the url of the google doc and outputs the wikicode format
*   Parse html prior to conversion to delete empty tag-content. e.g. <span class="c3"> </span> or <h4></h4>. It is completely useless and fucks up the formatting.

About Open Courses
==================

We need boilerplate text. Someone?
