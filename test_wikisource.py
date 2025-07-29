import pywikibot
import requests
import time

OCR_API = 'https://tools.wmflabs.org/indic-ocr/api/ocr'

def get_ocr_text(image_title, lang='hin'):
    """
    Use IndicOCR Toolforge API to get OCR text.
    """
    params = {
        'image': image_title,
        'lang': lang
    }

    response = requests.get(OCR_API, params=params)
    if response.status_code == 200:
        return response.text.strip()
    else:
        print(f"OCR failed for {image_title}: {response.status_code}")
        return None

def main():
    site = pywikibot.Site('hi', 'wikisource')
    page = pywikibot.Page(site, 'पृष्ठ:सम्पूर्ण गाँधी वांग्मय Sampurna Gandhi, vol. 31.pdf/६१६')  # replace with actual page

    # if not page.exists():
    #     print("Page does not exist.")
    #     return

    # Get the image file used by this page
    image_title = page.data_item().get()['claims']['P996'][0].getTarget().title()  # fallback if needed
    file_page = pywikibot.FilePage(site, image_title)

    # Get the OCR text from the Toolforge API
    ocr_text = get_ocr_text(file_page.title().replace('File:', ''))
    if ocr_text:
        page.text = ocr_text
        page.save(summary='Bot: Added OCR text from Indic OCR')

if __name__ == '__main__':
    main()
