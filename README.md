<<<<<<< HEAD
# 🚗 AutoValue — Car Price Predictor
### FastAPI + SQLite + Gradient Boosting ML (No Docker — runs directly with Python)

---

## 🚀 Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt --only-binary=:all:

# 2. (Optional) Retrain model — already trained, skip if model.pkl exists
python train_model.py

# 3. Start server
python -m uvicorn main:app --reload

# 4. Open browser
http://127.0.0.1:8000
```

---

## 📁 Project Structure

```
autovalue_local/
├── main.py            ← FastAPI app (serves API + UI)
├── database.py         ← SQLite via SQLAlchemy
├── schemas.py           ← Pydantic models
├── train_model.py       ← Dataset cleaning + model training
├── requirements.txt
├── models/
│   └── model.pkl         ← Trained Gradient Boosting model
├── data/
│   └── car_dataset.csv   ← 7,897 cleaned CarDekho listings
└── static/
    └── index.html        ← Full Web UI (served by FastAPI itself)
```

---

## 🔗 URLs

| What | URL |
|------|-----|
| 🎨 Web UI | http://127.0.0.1:8000 |
| 📋 Swagger Docs | http://127.0.0.1:8000/docs |

> No separate frontend server needed — FastAPI serves the UI directly, so there's no CORS / `file://` issue.

---

## 🤖 ML Model

| Property | Value |
|---|---|
| Algorithm | Gradient Boosting Regressor |
| Training Data | 7,897 real CarDekho listings |
| R² Score | **0.97** |
| MAE | ₹0.67 Lakh |
| Features | brand, model, year, fuel, transmission, owner, km_driven, mileage, engine, max_power |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/meta` | Brands, models, fuel types for dropdowns |
| POST | `/predict` | Predict price (no DB save) |
| POST | `/cars` | Create car + auto-predict |
| GET | `/cars` | List all cars |
| GET | `/cars/{id}` | Get one car |
| PUT | `/cars/{id}` | Update + re-predict |
| DELETE | `/cars/{id}` | Delete car |
| GET | `/stats` | Analytics summary |
=======
# mlops_divyansh
MLOPS project
>>>>>>> f19aeb4c76800b26fafdda7b48d2d8372834c21d
