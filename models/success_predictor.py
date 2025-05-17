"""
GroMo AI Sales Coach - Success Predictor Model

This module provides a machine learning model for predicting
the success probability of credit card applications.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import joblib


class SuccessPredictor:
    """Prediction model for application success probability."""
    
    def __init__(self):
        """Initialize the Success Predictor model."""
        self.model = None
        self.features = None
    
    def train(self, sales_data, cards_data=None):
        """
        Train the success prediction model.
        
        Args:
            sales_data: DataFrame with sales data
            cards_data: DataFrame with credit card data (optional)
        
        Returns:
            True if training successful, False otherwise
        """
        if sales_data is None or len(sales_data) < 50:
            # Not enough data for training
            return False
            
        # Extract features for prediction
        try:
            # Check if necessary columns exist
            required_cols = ['success_flag', 'card_id']
            if not all(col in sales_data.columns for col in required_cols):
                return False
                
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
            y = sales_data['success_flag']
            
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
                ('classifier', RandomForestClassifier(
                    n_estimators=100, 
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                ))
            ])
            
            self.model.fit(X, y)
            
            return True
        except Exception as e:
            print(f"Error training success prediction model: {str(e)}")
            return False
    
    def predict_probability(self, customer_data, card_id):
        """
        Predict success probability for a potential sale.
        
        Args:
            customer_data: Dictionary with customer information
            card_id: ID of the card
            
        Returns:
            Success probability (float)
        """
        if not self.is_trained():
            # Model not trained
            return self._basic_prediction(customer_data, card_id)
            
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
            prob = self.model.predict_proba(X)[0, 1]  # Probability of class 1 (success)
            
            return prob
        except Exception as e:
            print(f"Error predicting success probability: {str(e)}")
            return self._basic_prediction(customer_data, card_id)
    
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
            
            # Save model and features
            model_data = {
                'model': self.model,
                'features': self.features
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
    
    def _basic_prediction(self, customer_data, card_id):
        """
        Make a basic prediction without ML model.
        
        Args:
            customer_data: Customer information
            card_id: Card ID
            
        Returns:
            Success probability estimate
        """
        # Calculate credit score factor (0 to 1)
        credit_score = customer_data.get('credit_score', 650)
        credit_factor = min(1.0, max(0.0, (credit_score - 600) / 300))  # 600 to 900 range
        
        # Calculate income factor
        income = customer_data.get('income', 300000)
        income_factor = min(1.0, max(0.0, (income - 200000) / 800000))  # 200k to 1M range
        
        # Calculate age factor (adults between 25-55 get highest score)
        age = customer_data.get('age', 35)
        if age < 21:
            age_factor = 0.5
        elif age < 25:
            age_factor = 0.8
        elif age <= 55:
            age_factor = 1.0
        elif age <= 65:
            age_factor = 0.9
        else:
            age_factor = 0.7
            
        # Calculate final probability
        probability = 0.3 + (credit_factor * 0.3 + income_factor * 0.3 + age_factor * 0.1)
        
        # Cap at 0.1 to 0.9 range since this is a basic estimate
        return min(0.9, max(0.1, probability))
