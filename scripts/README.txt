TITLE: Epstein-ai 

DESCRIPTION:
    This is a project to digest all epstein data, starting with PDFs, into an AI vector database to be fed to an LLM.
    This is allow people to check statements and explore the files without navigating the 1M+ PDFs that are available.
    This project ingests DOJ PDF datasets, extracts structured text, chunks documents, builds semantic vector indexes (BGE-large), and builds entity indexes for investigative querying.


Steps From ZERO:

1. Install Python 3.11 (64-bit) https://www.python.org/downloads/release/python-31114/ ## 3.11 is required as some libraries will not support newer versions ##
2. Run install_env.bat
3. Gain access to all PDF zips from Datasets
4. In each Dataset is an IMAGES folder. Within this folder are the sub-folders numbered 0001 and up. Make a folder for each Dataset in 
    raw_pdf/ and place the IMAGES sub-folder in the given Dataset. Structure should be raw_pdf/dataset 1/0001 and so on.
5. Enter the venv and run ingest_pdf.py
6. Once complete, run chunk_documents.py
7. Run verify_gpu.bat
8. 







Steps:

1. Install Python 3.11 (64-bit) https://www.python.org/downloads/release/python-31114/ ## 3.11 is required as some libraries will not support newer versions ##
2. Run install_env.bat
3. Run verify_gpu.bat (confirm CUDA is detected) If not, it will run on CPU and that will suck ass.
4. Run run_vector.bat
5. Let it run overnight if needed.
6. If interrupted, just run run_vector.bat again. It resumes automatically.

Do NOT modify chunks.jsonl during embedding. Set it and forget it.

