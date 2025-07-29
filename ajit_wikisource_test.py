####### NEED TO BE TESTED YET on Google colab ################
################# STEP one to run ######################


# ✅ STEP 1: Install system packages and Pywikibot
!sudo apt update
!sudo apt install -y tesseract-ocr tesseract-ocr-hin libtesseract-dev
!pip install git+https://github.com/wikimedia/pywikibot.git

# ✅ STEP 2: Configure Pywikibot
import os
os.makedirs("pywikibot", exist_ok=True)
%cd pywikibot

# Create basic user-config.py for hi.wikisource
with open("user-config.py", "w", encoding="utf-8") as f:
    f.write("""
family = 'wikisource'
mylang = 'hi'
usernames['wikisource']['hi'] = 'अजीत कुमार तिवारी'
""")

print("✅ Pywikibot config ready. Run the login cell next.")

# ✅ STEP 3: Login to your Wikimedia account (manual prompt)
!python3 pwb.py login


################# STEP two to run ######################
import requests
from PIL import Image
from io import BytesIO
import pytesseract
import unicodedata
import re
from urllib.parse import quote
from subprocess import run, PIPE
import time

PDF_FILENAME = "सम्पूर्ण_गाँधी_वांग्मय_Sampurna_Gandhi,_vol._35.pdf"
BASE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0"
PAGE_START = 610
PAGE_END = 612  # ← adjust this range as needed
SIZE = 2000

def get_page_image_url(page):
    encoded = quote(PDF_FILENAME, safe='')
    return f"{BASE_URL}/{encoded}/page{page}-{SIZE}px-{encoded}.jpg"

def download_image(url):
    headers = {'User-Agent': 'MyIPBEUserBot/1.0 (your@email.example)'}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return Image.open(BytesIO(r.content))

def clean_text(txt):
    txt = txt.replace('\x0c', '')
    txt = re.sub(r'[\x00-\x08\x0B\x0E-\x1F\x7F]', '', txt)
    return unicodedata.normalize('NFC', txt)

def to_devanagari(n):
    nums = "०१२३४५६७८९"
    return ''.join(nums[int(d)] for d in str(n))

def ocr_and_upload(page):
    print(f"🔄 Processing page {page}")
    url = get_page_image_url(page)
    try:
        img = download_image(url)
    except Exception as e:
        print(f"❌ Failed to download image: {e}")
        return

    text = pytesseract.image_to_string(img, lang='hin+eng')
    text = clean_text(text)

    dev_page = to_devanagari(page)
    title = f"पृष्ठ:{PDF_FILENAME}/{dev_page}"
    summary = "बॉट: Google Colab से OCR अपडेट"

    cmd = [
        "python3", "pwb.py", "add_text",
        f"-page:{title}",
        f"-text:{text}",
        "-lang:hi",
        "-family:wikisource",
        "-always",
        f"-summary:{summary}"
    ]

    print(f"📤 Uploading page {page}...")
    result = run(cmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

# ✅ Run for desired pages
for page in range(PAGE_START, PAGE_END + 1):
    ocr_and_upload(page)
    time.sleep(8)  # avoid flooding
