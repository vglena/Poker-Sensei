# Run backend tests
cd app/backend
pip install pytest httpx
pytest tests/ -v
