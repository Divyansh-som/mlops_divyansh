import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error
import pickle, re

df = pd.read_csv('/mnt/user-data/uploads/Car_details_v3.csv')
print(f"Raw data: {df.shape}")

df['brand'] = df['name'].apply(lambda x: x.split()[0])
df['model'] = df['name'].apply(lambda x: ' '.join(x.split()[1:3]) if len(x.split()) > 1 else x.split()[0])

def extract_num(s):
    if pd.isna(s): return np.nan
    m = re.search(r'[\d.]+', str(s))
    return float(m.group()) if m else np.nan

df['mileage_num']   = df['mileage'].apply(extract_num)
df['engine_num']    = df['engine'].apply(extract_num)
df['max_power_num'] = df['max_power'].apply(extract_num)

df['price_lakh'] = (df['selling_price'] / 100000).round(2)

df = df.dropna(subset=['mileage_num','engine_num','max_power_num'])
df = df[df['price_lakh'] <= 80]
df = df[df['km_driven'] <= 400000]
print(f"Clean data: {df.shape}")

le_brand  = LabelEncoder()
le_model  = LabelEncoder()
le_fuel   = LabelEncoder()
le_trans  = LabelEncoder()
le_owner  = LabelEncoder()

df['brand_enc'] = le_brand.fit_transform(df['brand'])
df['model_enc'] = le_model.fit_transform(df['model'])
df['fuel_enc']  = le_fuel.fit_transform(df['fuel'])
df['trans_enc'] = le_trans.fit_transform(df['transmission'])
df['owner_enc'] = le_owner.fit_transform(df['owner'])
df['car_age']   = 2024 - df['year']

FEATURES = ['brand_enc','model_enc','car_age','fuel_enc','trans_enc',
            'owner_enc','km_driven','mileage_num','engine_num','max_power_num']

X = df[FEATURES]
y = df['price_lakh']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = GradientBoostingRegressor(n_estimators=300, max_depth=5, learning_rate=0.08, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"\nR²  = {r2_score(y_test, y_pred):.4f}")
print(f"MAE = ₹{mean_absolute_error(y_test, y_pred):.2f} Lakh")

brand_models = df.groupby('brand')['model'].unique().to_dict()
brand_models = {b: sorted(list(set(m))) for b, m in brand_models.items()}

df[['brand','model','year','fuel','transmission','owner','km_driven',
    'mileage_num','engine_num','max_power_num','price_lakh']].to_csv(
    'data/car_dataset.csv', index=False)

with open('models/model.pkl','wb') as f:
    pickle.dump({
        'model': model,
        'le_brand': le_brand, 'le_model': le_model,
        'le_fuel': le_fuel,   'le_trans': le_trans,
        'le_owner': le_owner,
        'brand_models': brand_models,
        'features': FEATURES
    }, f)

print(f"\n✅ Saved {len(df)} rows + model.pkl")
