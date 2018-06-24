# Account Opening Assistant

### Function 1:  GuardingValidator
Login 'http://domestic.judicial.gov.tw/abbs/wkw/WHD9HN01.jsp'
Input information and print PDF file.

### Function 2:  IDCardValidator
Login 'https://www.ris.gov.tw/id_card/'
Input information
Get captcha image and use OpenCv to solve
Submit and print PDF


Strongly recommand to use conda to set up virtual environment and make sure you install tensorflow in it.

You may also need execute
    - brew install tesseract


Captcha resolver Reference:
 https://medium.com/@ageitgey/how-to-break-a-captcha-system-in-15-minutes-with-machine-learning-dbebb035a710