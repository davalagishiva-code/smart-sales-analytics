# Smart Sales Analytics

Smart Sales Analytics is a professional sales analytics system for tracking sales, understanding customer and product performance, and generating machine learning-based sales predictions.

## Project purpose

The system includes:

- Sales recording and management
- Dashboard analytics
- Product and customer reports
- Sales history and filtering
- Machine learning-based prediction
- SQLite-backed persistence

## Folder structure

```text
smart-sales-analytics/
├── backend/
│   ├── __init__.py
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
├── src/
│   ├── __init__.py
│   ├── analytics.py
│   ├── database.py
│   └── ml_model.py
├── data/
│   └── sales.db
├── models/
│   └── sales_model.pkl
├── requirements.txt
├── .gitignore
├── README.md
└── .venv/
```

## Create virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Start FastAPI backend

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8080
```

## Start frontend

```bash
cd frontend
python -m http.server 5500
```

## Backend URL

http://127.0.0.1:8080

## Frontend URL

http://127.0.0.1:5500

## Swagger URL

http://127.0.0.1:8080/docs

## Frontend and backend communication

The static frontend uses a single API configuration in `frontend/js/api.js` and calls the FastAPI server using JavaScript `fetch` requests.

## How to use the application

1. Open the frontend in the browser.
2. Add sales data from the "Add Sale" section.
3. Review dashboard and analytics sections.
4. View product, customer, and sales reports.
5. Generate predictions from the prediction module when enough sales data exists.

## Notes

- The backend uses SQLite for persistent storage.
- The machine learning model is trained when there are enough sales records.
- The frontend is static and deployable to Netlify.
