"""
GroMo AI Sales Coach - Commission Predictor Model

This module provides a machine learning model for predicting
the commission amount for successful credit card applications.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import joblib


class CommissionPredictor:
    """Prediction model for commission amount."""
    
    def __init__(self):
        """Initialize the Commission Predictor model."""
        self.model = None
        self.features = None
        self.avg_commission = 1000  # Default average commission
    
    def train(self, sales_data, cards_data=None):
        """
        Train the commission prediction model.
        
        Args:
            sales_data: DataFrame with sales data (should only include successful sales)
            cards_data: DataFrame with credit card data (optional)
        
        Returns:
            True if training successful, False otherwise
        """
        if sales_data is None or len(sales_data) < 30:
            # Not enough data for training
            return False
            
        # Extract features for prediction
        try:
            # Check if necessary columns exist
            required_cols = ['commission', 'card_id']
            if not all(col in sales_data.columns for col in required_cols):
                return False
                
            # Store average commission for fallback predictions
            self.avg_commission = sales_data['commission'].mean()
                
            # Define features to use
            features = []
            
            # Customer features
            customer_features = ['customer_age', 'customer_income', 'customer_credit_score']
            for feat in customer_features:
                if feat in sales_data.columns:
                    features.append(feat)
                    
            # Categorical features
            cat_features = ['customer_employment', 'card_id']
            for feat in cat_features:
                if feat in sales_data.columns:
                    features.append(feat)
                    
            if not features:
                # No usable features
                return False
                
            # Store feature list for prediction
            self.features = features
                
            # Prepare training data
            X = sales_data[features].copy()
            y = sales_data['commission']
            
            # Define preprocessing for numerical and categorical features
            numerical_features = [f for f in features if f in customer_features]
            categorical_features = [f for f in features if f in cat_features]
            
            # Preprocessing pipeline
            numeric_transformer = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ])
            
            categorical_transformer = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(handle_unknown='ignore'))
            ])
            
            preprocessor = ColumnTransformer(
                transformers=[
                    ('num', numeric_transformer, numerical_features),
                    ('cat', categorical_transformer, categorical_features)
                ]
            )
            
            # Create and train the model
            self.model = Pipeline(steps=[
                ('preprocessor', preprocessor),
                ('regressor', GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=4,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                ))
            ])
            
            self.model.fit(X, y)
            
            return True
        except Exception as e:
            print(f"Error training commission prediction model: {str(e)}")
            return False
    
    def predict_commission(self, customer_data, card_id):
        """
        Predict commission amount for a potential sale.
        
        Args:
            customer_data: Dictionary with customer information
            card_id: ID of the card
            
        Returns:
            Predicted commission amount (float)
        """
        if not self.is_trained():
            # Model not trained
            return self.avg_commission
            
        try:
            # Prepare input data
            input_data = {}
            
            # Add customer features
            if 'customer_age' in self.features:
                input_data['customer_age'] = customer_data.get('age', 35)
                
            if 'customer_income' in self.features:
                input_data['customer_income'] = customer_data.get('income', 500000)
                
            if 'customer_credit_score' in self.features:
                input_data['customer_credit_score'] = customer_data.get('credit_score', 700)
                
            if 'customer_employment' in self.features:
                input_data['customer_employment'] = customer_data.get('employment_type', 'Salaried')
                
            # Add card ID
            if 'card_id' in self.features:
                input_data['card_id'] = card_id
                
            # Create DataFrame
            X = pd.DataFrame([input_data])
            
            # Make prediction
            commission = self.model.predict(X)[0]
            
            # Ensure prediction is positive
            return max(0, commission)
        except Exception as e:
            print(f"Error predicting commission: {str(e)}")
            return self.avg_commission
    
    def save_model(self, filepath):
        """
        Save the trained model to a file.
        
        Args:
            filepath: Path to save the model
            
        Returns:
            True if saving successful, False otherwise
        """
        if not self.is_trained():
            return False
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save model, features, and average commission
            model_data = {
                'model': self.model,
                'features': self.features,
                'avg_commission': self.avg_commission
            }
            
            joblib.dump(model_data, filepath)
            return True
        except Exception as e:
            print(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, filepath):
        """
        Load a trained model from a file.
        
        Args:
            filepath: Path to the model file
            
        Returns:
            True if loading successful, False otherwise
        """
        try:
            if os.path.exists(filepath):
                model_data = joblib.load(filepath)
                
                if isinstance(model_data, dict):
                    self.model = model_data.get('model')
                    self.features = model_data.get('features')
                    self.avg_commission = model_data.get('avg_commission', 1000)
                else:
                    self.model = model_data
                    self.features = None
                    
                return self.is_trained()
            else:
                return False
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def is_trained(self):
        """
        Check if the model is trained.
        
        Returns:
            True if model is trained, False otherwise
        """
        return self.model is not None
