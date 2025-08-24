import re
import argparse
import pywikibot
from pywikibot.proofreadpage import IndexPage, ProofreadPage

def is_effectively_empty(page, max_bytes=30):
    try:
        text = page.text
        text = re.sub(r'<noinclude>.*?</noinclude>', '', text, flags=re.DOTALL)
        text = re.sub(r'\{\{[^\}]+\}\}', '', text)
        text = text.strip()
        return len(text.encode('utf-8')) < max_bytes
    except Exception as e:
        print(f"Error processing {page.title()}: {e}")
        return False

def clear_and_mark_as_blank(proofread_page):
    try:
        proofread_page.text = ''  # clear the content
        proofread_page.without_text()  # mark as रिक्त
        proofread_page.save(summary="बॉट: पृष्ठ खाली करके स्थिति 'रिक्त' के रूप में सेट की")
        print(f"✔ Cleared and marked as रिक्त: {proofread_page.title()}")
    except Exception as e:
        print(f"❌ Failed to update {proofread_page.title()}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Empty small Wikisource pages and mark as रिक्त.")
    parser.add_argument("--file", type=str, default="सम्पूर्ण गाँधी वांग्मय Sampurna Gandhi, vol. 39.pdf",
                        help="PDF file name (without 'Index:' prefix)")
    parser.add_argument("--size", type=int, default=30,
                        help="Max effective byte size to consider page as empty (default: 30)")

    args = parser.parse_args()

    site = pywikibot.Site("hi", "wikisource")
    site.login()

    index_title = f"Index:{args.file}"
    max_bytes = args.size

    index_page = IndexPage(site, index_title)

    if not index_page.exists():
        print(f"❌ Index page not found: {index_title}")
        return

    print(f"🔍 Scanning pages from: {index_title} (size threshold: {max_bytes} bytes)")
    pages = list(index_page.page_gen())

    for page in pages:
        prp = ProofreadPage(page)
        prp._index = index_page

        if is_effectively_empty(prp, max_bytes):
            if prp.text.strip():  # something to remove
                clear_and_mark_as_blank(prp)
            else:
                if prp.quality != 0:
                    prp.quality = 0
                    prp.save(summary="बॉट: स्थिति 'रिक्त' पर अपडेट की गई।", minor=False)
                    print(f"🟢 Marked as रिक्त (was already empty): {prp.title()}")
        else:
            print(f"⏭ Skipped (has text): {prp.title()}")

if __name__ == "__main__":
    main()
