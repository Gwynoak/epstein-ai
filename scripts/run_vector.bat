@echo off
echo =========================================
echo Starting Vector Embedding
echo =========================================

call venv\Scripts\activate

python scripts\build_vector_index_streaming.py

echo =========================================
echo Embedding Complete
echo =========================================
pause
