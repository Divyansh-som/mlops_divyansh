from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import pickle, numpy as np, os

from database import get_db, CarDB
from schemas import CarCreate, CarUpdate, CarOut, PredictRequest, PredictResponse

# ── Load ML Model ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "models", "model.pkl"), "rb") as f:
    bundle = pickle.load(f)

model        = bundle["model"]
le_brand     = bundle["le_brand"]
le_model     = bundle["le_model"]
le_fuel      = bundle["le_fuel"]
le_trans     = bundle["le_trans"]
le_owner     = bundle["le_owner"]
brand_models = bundle["brand_models"]

BRANDS       = sorted(list(le_brand.classes_))
FUEL_TYPES   = sorted(list(le_fuel.classes_))
TRANS_TYPES  = sorted(list(le_trans.classes_))
OWNER_TYPES  = list(le_owner.classes_)

def safe_encode(le, val):
    return le.transform([val])[0] if val in le.classes_ else 0

def predict_price(d: dict) -> float:
    X = np.array([[
        safe_encode(le_brand, d["brand"]),
        safe_encode(le_model, d["model"]),
        2024 - d["year"],
        safe_encode(le_fuel,  d["fuel_type"]),
        safe_encode(le_trans, d["transmission"]),
        safe_encode(le_owner, d["owner"]),
        d["km_driven"],
        d["mileage"],
        d["engine"],
        d["max_power"],
    ]])
    return round(float(max(0.5, model.predict(X)[0])), 2)

def car_condition(km: int, year: int) -> str:
    age = 2024 - year
    if km < 30000 and age <= 3:   return "🟢 Excellent"
    if km < 70000 and age <= 6:   return "🟡 Good"
    if km < 120000 and age <= 10: return "🟠 Fair"
    return "🔴 High Usage"

def depreciation_info(year: int) -> str:
    age = 2024 - year
    dep = min(85, age * 8)
    return f"~{dep}% depreciated from original price"

def price_tips(price: float, brand: str, transmission: str) -> str:
    luxury = ["BMW", "Audi", "Mercedes-Benz", "Jaguar", "Volvo", "Lexus", "Land"]
    if brand in luxury:
        return "💎 Luxury segment — high maintenance expected. Verify full service history."
    if transmission == "Automatic":
        return "⚙️ Automatic transmission — higher resale value. Check gearbox condition carefully."
    if price < 3:
        return "✅ Budget pick — ideal for first-time buyers. Verify RC transfer & insurance."
    if price < 8:
        return "👍 Mid-range — good value. Negotiate 5-8% if km driven is high."
    return "🚀 Premium segment — get an independent inspection before buying."

# ── FastAPI App ────────────────────────────────────────────────
app = FastAPI(
    title="🚗 AutoValue — Car Price Predictor",
    description="Real CarDekho data · Gradient Boosting · R²=0.97 · CRUD + ML",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# ── Static Files (UI) ──────────────────────────────────────────
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", include_in_schema=False)
def serve_ui():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))

# ── Meta ───────────────────────────────────────────────────────
@app.get("/meta", tags=["Meta"])
def get_meta():
    return {
        "brands":        BRANDS,
        "brand_models":  brand_models,
        "fuel_types":    FUEL_TYPES,
        "transmissions": TRANS_TYPES,
        "owner_types":   OWNER_TYPES,
    }

# ── ML Predict (no DB save) ────────────────────────────────────
@app.post("/predict", response_model=PredictResponse, tags=["ML Prediction"])
def predict(req: PredictRequest):
    price = predict_price(req.dict())
    return PredictResponse(
        predicted_price_lakh=price,
        price_range=f"₹{max(0.5, price - 1.0):.1f}L – ₹{price + 1.0:.1f}L",
        condition=car_condition(req.km_driven, req.year),
        depreciation=depreciation_info(req.year),
        tips=price_tips(price, req.brand, req.transmission),
    )

# ── CREATE ─────────────────────────────────────────────────────
@app.post("/cars", response_model=CarOut, status_code=201, tags=["CRUD"])
def create_car(car: CarCreate, db: Session = Depends(get_db)):
    price  = predict_price(car.dict())
    db_car = CarDB(**car.dict(), predicted_price=price)
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# ── READ ALL ───────────────────────────────────────────────────
@app.get("/cars", response_model=List[CarOut], tags=["CRUD"])
def get_all_cars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(CarDB).offset(skip).limit(limit).all()

# ── READ ONE ───────────────────────────────────────────────────
@app.get("/cars/{car_id}", response_model=CarOut, tags=["CRUD"])
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(CarDB).filter(CarDB.id == car_id).first()
    if not car:
        raise HTTPException(404, f"Car ID {car_id} not found")
    return car

# ── UPDATE ─────────────────────────────────────────────────────
@app.put("/cars/{car_id}", response_model=CarOut, tags=["CRUD"])
def update_car(car_id: int, updates: CarUpdate, db: Session = Depends(get_db)):
    car = db.query(CarDB).filter(CarDB.id == car_id).first()
    if not car:
        raise HTTPException(404, f"Car ID {car_id} not found")
    for field, val in updates.dict(exclude_unset=True).items():
        setattr(car, field, val)
    car.predicted_price = predict_price({
        "brand": car.brand, "model": car.model, "year": car.year,
        "fuel_type": car.fuel_type, "transmission": car.transmission,
        "owner": car.owner, "km_driven": car.km_driven,
        "mileage": car.mileage, "engine": car.engine, "max_power": car.max_power,
    })
    db.commit()
    db.refresh(car)
    return car

# ── DELETE ─────────────────────────────────────────────────────
@app.delete("/cars/{car_id}", tags=["CRUD"])
def delete_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(CarDB).filter(CarDB.id == car_id).first()
    if not car:
        raise HTTPException(404, f"Car ID {car_id} not found")
    db.delete(car)
    db.commit()
    return {"message": f"Car ID {car_id} deleted successfully ✅"}

# ── ANALYTICS ──────────────────────────────────────────────────
@app.get("/stats", tags=["Analytics"])
def get_stats(db: Session = Depends(get_db)):
    cars = db.query(CarDB).all()
    if not cars:
        return {"message": "No cars in database yet."}
    prices = [c.predicted_price for c in cars if c.predicted_price]
    brands = {}
    fuels  = {}
    for c in cars:
        brands[c.brand] = brands.get(c.brand, 0) + 1
        fuels[c.fuel_type] = fuels.get(c.fuel_type, 0) + 1
    return {
        "total_cars":         len(cars),
        "avg_price_lakh":     round(sum(prices) / len(prices), 2),
        "max_price_lakh":     round(max(prices), 2),
        "min_price_lakh":     round(min(prices), 2),
        "brand_distribution": dict(sorted(brands.items(), key=lambda x: -x[1])),
        "fuel_distribution":  fuels,
    }
