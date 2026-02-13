@echo off
echo =========================================
echo Setting up Epstein AI Environment
echo =========================================

py -3.11 -m venv venv

call venv\Scripts\activate

python -m pip install --upgrade pip

echo Installing PyMuPDF
pip install pymupdf

:: cu128 is used for 50 series cards. Change the cu type at the end of the download URL to retreive the version that supports your card
echo Installing latest CUDA-enabled PyTorch...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

echo Installing dependencies...
pip install sentence-transformers faiss-cpu numpy tqdm

echo =========================================
echo Environment setup complete.
echo =========================================
pause
