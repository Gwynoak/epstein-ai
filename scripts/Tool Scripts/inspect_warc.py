import gzip
from warcio.archiveiterator import ArchiveIterator

WARC_PATH = r"C:\Users\Devin McGuire\Downloads\www.justice.gov_epstein_files_DataSet_9_individual_pdf_bruteforce\www.justice.gov_epstein_files_DataSet_9-individual-pdfs-bruteforce-00000.warc\www.justice.gov_epstein_files_DataSet_9-individual-pdfs-bruteforce-00000.warc"
pdf_count = 0
total_records = 0

if WARC_PATH.endswith(".gz"):
    stream = gzip.open(WARC_PATH, 'rb')
else:
    stream = open(WARC_PATH, 'rb')

with stream:
    for record in ArchiveIterator(stream):
        total_records += 1

        if record.rec_type != 'response':
            continue

        content_type = record.http_headers.get_header('Content-Type')

        if content_type:
            if 'application/pdf' in content_type:
                pdf_count += 1

        if total_records % 10000 == 0:
            print(f"Records scanned: {total_records}")

print("Total records:", total_records)
print("PDF responses:", pdf_count)
