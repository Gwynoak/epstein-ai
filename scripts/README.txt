TITLE: Epstein-ai 

DESCRIPTION:
    This is a project to digest all epstein data, starting with PDFs, into an AI vector database to be fed to an LLM.
    This is allow people to check statements and explore the files without navigating the 1M+ PDFs that are available.
    This project ingests DOJ PDF datasets, extracts structured text, chunks documents, builds semantic vector indexes (BGE-large), and builds entity indexes for investigative querying.


Processed Dataset Link:
https://drive.google.com/drive/folders/1n6zRCRZk87O5dvGH2Z7F5MaytmaHMFot?usp=sharing

==============================================================================================================================================

Steps From ZERO:

1. Install Python 3.11 (64-bit) https://www.python.org/downloads/release/python-31114/ ## 3.11 is required as some libraries will not support newer versions ##
2. Run install_env.bat
3. Gain access to all PDF zips from Datasets
4. In each Dataset is an IMAGES folder. Within this folder are the sub-folders numbered 0001 and up. Make a folder for each Dataset in 
    raw_pdf/ and place the IMAGES sub-folder in the given Dataset. Structure should be raw_pdf/dataset 1/0001 and so on.
5. Enter the venv and run ingest_pdf.py
6. Once complete, run chunk_documents.py
7. Run verify_gpu.bat
    It will spit out your GPU type and CUDA version. install_env will use pytorch cu128 for 50 series cards, you may need to adjust this
    If it does not send this information it means you are running on CPU, this is possible but will take too long. Troubleshoot this process
8. Run run_vector.bat
    This creates the vectorized index for the LLM
9. TBC...

==============================================================================================================================================




If you have documents.jsonl and chunks.jsonl already
==============================================================================================================================================

Steps:

1. Install Python 3.11 (64-bit) https://www.python.org/downloads/release/python-31114/ ## 3.11 is required as some libraries will not support newer versions ##
2. Run install_env.bat
3. Run verify_gpu.bat (confirm CUDA is detected) If not, it will run on CPU and that will suck ass.
4. Run run_vector.bat
5. Let it run overnight if needed.
6. If interrupted, just run run_vector.bat again. It resumes automatically.

Do NOT modify chunks.jsonl during embedding. Set it and forget it.

==============================================================================================================================================

Tool Scripts:

analyze_discarded.py
    This was to pass through discarded.jsonl and see what word counts we had to determine how much data was worth retrieving.

inspect_warc.py
    When dealing with the copy of database 9 I got, the files came as warc.gz I needed a way to read what was in them before scripting
    for the unpacking (ChatGPT did the script, not me, I'm just along for the ride here).

recover_discarded_documents.py
    This is used to scrub through the discarded.jsonl file. ingest_pdf.py discards anything < 300 words. This is great for initial pass
    but for data integrity I decided to go back through with more complex value detection to catch short but valued information.

test_dupe.py
    This was used on Dataset 9 to ensure there were no duplicate PDFs. Could be used on any root folder though.

warc_test_extract.py
    This was used to extract a Dataset 9 warc file and determine what the crawler's layout was so it could be adapted.

SERVER SCRIPT vs NON-SERVER
==============================================================================================================================================
Half way through this project I gained access to a well equipped DELL server with 44 cores and over 300GB of RAM. At this point I needed to re-ingest all of my PDF
to preserve white-space. ingest_pdf.py collapses all white space but I needed to iterate through to remove boilerplate text like headers and confidentiality notices.
The problem is that this is hard to hash without white-space preserved. This means that ingest_preserved_server.py is optimal for ingestion. If you are reading this, you will 
need to adjust this script for your own hardware unless you have 88 logic cores and 300GB of RAM laying around (like I miraculously did).