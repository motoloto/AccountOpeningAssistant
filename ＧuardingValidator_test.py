import requests
import os
import sys
import cgi
import logging
from lxml import html

import urllib.request as request
import urllib.parse as parse
import xhtml2pdf.pisa as pisa

target_page = 'http://domestic.judicial.gov.tw/abbs/wkw/WHD9HN02.jsp?from=WHD9HN01.jsp'
dest = "test.pdf"


def getTargetPage(url):
    page = requests.get(url)
    tree = html.fromstring(page.text)
    return tree


# getTargetPage(target_page)
#
session_requests = requests.session()
result = session_requests.get(target_page)
tree = html.fromstring(result.text)


payload = {
    'kd_id': '02',
    'kd': None,
    'idnoyn': 'N',
    'crtid': '',
    'Button': None,
    'kdid': None,
    'clnm': '鐘子皓',
    'idno': 'E124277446',
    'sddtStart': '',
    'sddtEnd': ''
}

# result = session_requests.post(target_page)
result = session_requests.post(target_page, data=payload)

# result = request.urlopen(target_page, parse.urlencode(payload).encode('utf-8'))

print("result>>>",result.text)

# resultTree = html.fromstring(result.text)



# Utility function
def convertHtmlToPdf(sourceHtml, outputFilename):
    # open output file for writing (truncated binary)
    resultFile = open(outputFilename, "w+b")

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
        sourceHtml,  # the HTML to convert
        dest=resultFile)  # file handle to recieve result

    # close output file
    resultFile.close()  # close output file

    # return True on success and False on errors
    return pisaStatus.err



pdf = convertHtmlToPdf(result.text, dest)

if pdf.err:
    print("PDF Created failed! Reson:%d" % pdf.err)
else:
    print("File exist?",os.path.isfile(dest))
