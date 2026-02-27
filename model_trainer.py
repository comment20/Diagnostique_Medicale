
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib
import numpy as np

# 1. Load Data
try:
    df = pd.read_csv('heart_disease_uci.csv')
except FileNotFoundError:
    print("Error: 'heart_disease_uci.csv' not found. Make sure the file is in the correct directory.")
    exit()

# 2. Clean and Preprocess Data
# Drop identifier columns
df = df.drop(['id', 'dataset'], axis=1)

# Handle missing values represented by '?'
df = df.replace('?', np.nan)

# Correct data types that might be object due to '?'
for col in ['trestbps', 'chol', 'fbs', 'restecg', 'thalch', 'exang', 'oldpeak', 'slope', 'ca', 'thal']:
    if df[col].dtype == 'object':
        try:
            df[col] = pd.to_numeric(df[col])
        except ValueError:
            print(f"Could not convert column {col} to numeric. It may contain non-numeric values other than '?'.")


# Define the target variable: 0 for no heart disease, 1 for presence
df['target'] = (df['num'] > 0).astype(int)
df = df.drop('num', axis=1)

# Separate features and target
X = df.drop('target', axis=1)
y = df['target']

# 3. Define Preprocessing Pipelines for Column Types
# Identify categorical and numerical features
categorical_features = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
numerical_features = ['age', 'trestbps', 'chol', 'thalch', 'oldpeak', 'ca']

# Create preprocessing pipelines for both numerical and categorical data
numerical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Create a preprocessor object using ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)
    ],
    remainder='passthrough' # Keep other columns if any (should not be the case here)
)

# 4. Create and Train the Model
# Define the model pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train the model
model_pipeline.fit(X_train, y_train)

# 5. Evaluate the Model (Optional, for verification)
y_pred = model_pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model trained with accuracy: {accuracy:.2f}")

# 6. Save the Model
joblib.dump(model_pipeline, 'heart_disease_model.pkl')
print("Model successfully saved as 'heart_disease_model.pkl'")

