import os
import gzip
from warcio.archiveiterator import ArchiveIterator

WARC_PATH = r"C:\Users\Devin McGuire\Downloads\www.justice.gov_epstein_files_DataSet_9_individual_pdf_bruteforce\www.justice.gov_epstein_files_DataSet_9-individual-pdfs-bruteforce-00000.warc\www.justice.gov_epstein_files_DataSet_9-individual-pdfs-bruteforce-00000.warc"
OUTPUT_DIR = "raw_pdf/Dataset 9/Dataset 9 test"

os.makedirs(OUTPUT_DIR, exist_ok=True)

pdf_count = 0
bad_pdf_count = 0

if WARC_PATH.endswith(".gz"):
    stream = gzip.open(WARC_PATH, 'rb')
else:
    stream = open(WARC_PATH, 'rb')

with stream:
    for record in ArchiveIterator(stream):
        if record.rec_type != 'response':
            continue

        content_type = record.http_headers.get_header('Content-Type')

        if content_type and 'application/pdf' in content_type:
            pdf_data = record.content_stream().read()

            # Save using incremental naming for now
            filename = f"extracted_{pdf_count}.pdf"
            output_path = os.path.join(OUTPUT_DIR, filename)

            try:
                with open(output_path, "wb") as f:
                    f.write(pdf_data)
                pdf_count += 1
            except:
                bad_pdf_count += 1

print("Extracted PDFs:", pdf_count)
print("Failed Writes:", bad_pdf_count)
