from pydantic import BaseModel, Field
from typing import Optional


class CarCreate(BaseModel):
    owner_name:   str   = Field(..., example="Rahul Sharma")
    brand:        str   = Field(..., example="Maruti")
    model:        str   = Field(..., example="Swift VXI")
    year:         int   = Field(..., ge=1990, le=2024, example=2019)
    fuel_type:    str   = Field(..., example="Petrol")
    transmission: str   = Field(..., example="Manual")
    owner:        str   = Field(..., example="First Owner")
    km_driven:    int   = Field(..., ge=0, le=500000, example=45000)
    mileage:      float = Field(..., ge=0, le=60, example=22.0)
    engine:       float = Field(..., ge=500, le=6000, example=1197.0)
    max_power:    float = Field(..., ge=20, le=700, example=82.0)


class CarUpdate(BaseModel):
    owner_name:   Optional[str]   = None
    brand:        Optional[str]   = None
    model:        Optional[str]   = None
    year:         Optional[int]   = Field(None, ge=1990, le=2024)
    fuel_type:    Optional[str]   = None
    transmission: Optional[str]   = None
    owner:        Optional[str]   = None
    km_driven:    Optional[int]   = Field(None, ge=0, le=500000)
    mileage:      Optional[float] = None
    engine:       Optional[float] = None
    max_power:    Optional[float] = None


class CarOut(BaseModel):
    id:              int
    owner_name:      str
    brand:           str
    model:           str
    year:            int
    fuel_type:       str
    transmission:    str
    owner:           str
    km_driven:       int
    mileage:         float
    engine:          float
    max_power:       float
    predicted_price: Optional[float]

    class Config:
        from_attributes = True


class PredictRequest(BaseModel):
    brand:        str   = Field(..., example="Maruti")
    model:        str   = Field(..., example="Swift VXI")
    year:         int   = Field(..., ge=1990, le=2024, example=2019)
    fuel_type:    str   = Field(..., example="Petrol")
    transmission: str   = Field(..., example="Manual")
    owner:        str   = Field(..., example="First Owner")
    km_driven:    int   = Field(..., ge=0, le=500000, example=45000)
    mileage:      float = Field(..., ge=0, le=60, example=22.0)
    engine:       float = Field(..., ge=500, le=6000, example=1197.0)
    max_power:    float = Field(..., ge=20, le=700, example=82.0)


class PredictResponse(BaseModel):
    predicted_price_lakh: float
    price_range:          str
    condition:            str
    depreciation:         str
    tips:                 str
