# Run the Project

Use these steps to run the secure document RAG app locally on Windows.

## 1. Start the backend

Open a terminal in the project root and run:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks script execution, allow it for the current session first:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
```

Copy the example environment file and set your Gemini API key:

```powershell
Copy-Item .env.example .env
```

Edit `backend/.env` and set `GEMINI_API_KEY`.

Start the API server:

```powershell
uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://127.0.0.1:8000`.

## 2. Start the frontend

Open a second terminal in the project root and run:

```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

The frontend will be available at `http://localhost:5173`.

## 3. Open the app

Open the frontend URL in your browser. The frontend is configured to talk to the backend API on port `8000`.

## Notes

- Keep both terminals open while using the app.
- If dependency installation fails on an older Python version, use the Python interpreter that is already configured in the backend virtual environment.
- The backend expects the Google Gemini API key to be present in `backend/.env` before you upload documents or ask questions.
