"""
GroMo AI Sales Coach - Lead Service

This module provides services for recommending potential leads to agents
and predicting success probability for potential sales.
"""

import random
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

from data.data_loader import DataLoader
from models.success_predictor import SuccessPredictor
from models.commission_predictor import CommissionPredictor
from utils.metrics import calculate_success_rate, calculate_avg_commission
from config import Config


class LeadService:
    """Service for lead-related operations."""
    
    def __init__(self):
        """Initialize the Lead Service."""
        self.data_loader = DataLoader()
        self.success_predictor = SuccessPredictor()
        self.commission_predictor = CommissionPredictor()
        
        # Try to load trained models if available
        model_dir = Config.MODEL_DIR
        success_model_path = os.path.join(model_dir, 'success_model.pkl')
        commission_model_path = os.path.join(model_dir, 'commission_model.pkl')
        
        if os.path.exists(success_model_path) and os.path.exists(commission_model_path):
            self.success_predictor.load_model(success_model_path)
            self.commission_predictor.load_model(commission_model_path)
        else:
            # Train models if not available
            self._train_models()
    
    def recommend_leads(self, agent_id, limit=5):
        """
        Recommend potential leads for an agent based on their performance history.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of lead recommendations (default: 5)
            
        Returns:
            List of lead recommendations with customer profiles and product matches
        """
        # Load data
        sales_data = self.data_loader.load_sales_data()
        cards_data = self.data_loader.load_cards_data()
        agents_data = self.data_loader.load_agents_data()
        
        if sales_data is None or cards_data is None:
            return None
        
        # Filter data for the specific agent
        agent_sales = sales_data[sales_data['agent_id'] == agent_id].copy()
        
        # Get agent info if available
        agent_info = None
        if agents_data is not None:
            agent_row = agents_data[agents_data['agent_id'] == agent_id]
            if len(agent_row) > 0:
                agent_info = agent_row.iloc[0].to_dict()
        
        # For new agents, generate leads based on network-wide performance
        if len(agent_sales) == 0:
            return self._recommend_leads_for_new_agent(limit, agent_info)
        
        # Calculate agent's success rate by card
        card_success = agent_sales.groupby('card_id').agg({
            'sale_id': 'count',
            'success_flag': 'sum',
            'commission': 'sum'
        }).reset_index()
        
        card_success = card_success.rename(columns={
            'sale_id': 'total_sales',
            'success_flag': 'successful_sales'
        })
        
        card_success['success_rate'] = card_success.apply(
            lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
            axis=1
        )
        
        card_success['avg_commission'] = card_success.apply(
            lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
            axis=1
        )
        
        # Find agent's best performing cards (min 3 sales, success rate > 50%)
        best_cards = card_success[
            (card_success['total_sales'] >= 3) &
            (card_success['success_rate'] >= 0.5)
        ].sort_values('commission', ascending=False).head(3)
        
        # If no best cards found, use overall top-performing cards
        if len(best_cards) == 0:
            network_card_success = sales_data.groupby('card_id').agg({
                'sale_id': 'count',
                'success_flag': 'sum',
                'commission': 'sum'
            }).reset_index()
            
            network_card_success = network_card_success.rename(columns={
                'sale_id': 'total_sales',
                'success_flag': 'successful_sales'
            })
            
            network_card_success['success_rate'] = network_card_success.apply(
                lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
                axis=1
            )
            
            network_card_success['avg_commission'] = network_card_success.apply(
                lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
                axis=1
            )
            
            best_cards = network_card_success.sort_values(
                ['success_rate', 'avg_commission'], ascending=False
            ).head(3)
        
        # Calculate agent's success rate by customer segment
        if 'customer_income' in agent_sales.columns:
            # Create income segments
            agent_sales['income_segment'] = pd.cut(
                agent_sales['customer_income'],
                bins=[0, 300000, 600000, 1000000, float('inf')],
                labels=['Low', 'Medium', 'High', 'Very High']
            )
            
            segment_success = agent_sales.groupby('income_segment').agg({
                'success_flag': ['count', 'mean']
            })
            
            segment_success.columns = ['count', 'success_rate']
            segment_success = segment_success.reset_index()
            
            # Get best income segments (min 3 sales, success rate > 50%)
            best_segments = segment_success[
                (segment_success['count'] >= 3) &
                (segment_success['success_rate'] >= 0.5)
            ].sort_values('success_rate', ascending=False)
            
            best_segment_list = best_segments['income_segment'].tolist() if len(best_segments) > 0 else []
        else:
            best_segment_list = []
            
        # Calculate agent's success rate by employment type
        if 'customer_employment' in agent_sales.columns:
            employment_success = agent_sales.groupby('customer_employment').agg({
                'success_flag': ['count', 'mean']
            })
            
            employment_success.columns = ['count', 'success_rate']
            employment_success = employment_success.reset_index()
            
            # Get best employment types (min 3 sales, success rate > 50%)
            best_employment = employment_success[
                (employment_success['count'] >= 3) &
                (employment_success['success_rate'] >= 0.5)
            ].sort_values('success_rate', ascending=False)
            
            best_employment_list = best_employment['customer_employment'].tolist() if len(best_employment) > 0 else []
        else:
            best_employment_list = []
            
        # Generate leads based on agent's best performing cards and segments
        leads = []
        
        # Get card details
        card_ids = best_cards['card_id'].tolist()
        card_details = {}
        
        for card_id in card_ids:
            card_row = cards_data[cards_data['card_id'] == card_id]
            if len(card_row) > 0:
                card_details[card_id] = card_row.iloc[0].to_dict()
        
        # Generate leads for each best card
        lead_allocation = {card_id: max(1, limit // len(card_ids)) for card_id in card_ids}
        
        for card_id, num_leads in lead_allocation.items():
            if card_id in card_details:
                card_detail = card_details[card_id]
                
                for i in range(num_leads):
                    # Generate a customer profile based on agent's strengths
                    customer = self._generate_customer_profile(
                        card_detail, 
                        best_segment_list, 
                        best_employment_list
                    )
                    
                    # Predict success and commission
                    prediction = self.predict_success(customer, card_id, agent_id)
                    
                    # Only include if success probability is good
                    if prediction and prediction['success_probability'] >= 0.4:
                        leads.append({
                            'customer': customer,
                            'card_id': card_id,
                            'card_details': card_detail,
                            'success_probability': prediction['success_probability'],
                            'expected_commission': prediction['expected_commission'],
                            'key_factors': prediction['key_factors']
                        })
        
        # Sort leads by expected commission and success probability
        leads.sort(key=lambda x: (
            x['expected_commission'] if x['expected_commission'] is not None else 0,
            x['success_probability']
        ), reverse=True)
        
        # Return top leads, limited to the requested number
        return leads[:limit]
    
    def predict_success(self, customer_data, card_id, agent_id=None):
        """
        Predict success probability for a potential sale.
        
        Args:
            customer_data: Dictionary with customer information
            card_id: ID of the card to be sold
            agent_id: ID of the agent (optional)
            
        Returns:
            Dictionary with success probability, expected commission, and key factors
        """
        # Load card details
        cards_data = self.data_loader.load_cards_data()
        if cards_data is None:
            return None
            
        card_details = cards_data[cards_data['card_id'] == card_id]
        if len(card_details) == 0:
            return None
            
        card_detail = card_details.iloc[0].to_dict()
        
        # Ensure the success predictor is trained
        if not self.success_predictor.is_trained():
            self._train_models()
            
        if not self.success_predictor.is_trained():
            # If still not trained, return a basic prediction
            return self._basic_prediction(customer_data, card_detail)
        
        # Make predictions
        success_prob = self.success_predictor.predict_probability(customer_data, card_id)
        expected_commission = None
        
        if success_prob > 0 and self.commission_predictor.is_trained():
            expected_commission = self.commission_predictor.predict_commission(customer_data, card_id)
        
        # Identify key factors affecting the prediction
        key_factors = self._identify_key_factors(customer_data, card_detail, success_prob)
        
        return {
            'success_probability': success_prob,
            'expected_commission': expected_commission,
            'key_factors': key_factors
        }
    
    def _train_models(self):
        """Train the success prediction and commission prediction models."""
        # Load data
        sales_data = self.data_loader.load_sales_data()
        cards_data = self.data_loader.load_cards_data()
        
        if sales_data is None or cards_data is None or len(sales_data) < 50:
            # Not enough data to train reliable models
            return
        
        # Train success prediction model
        self.success_predictor.train(sales_data, cards_data)
        
        # Train commission prediction model using only successful sales
        successful_sales = sales_data[sales_data['success_flag'] == True].copy()
        if len(successful_sales) >= 30:  # Minimum data for commission model
            self.commission_predictor.train(successful_sales, cards_data)
        
        # Save models
        try:
            model_dir = Config.MODEL_DIR
            os.makedirs(model_dir, exist_ok=True)
            
            success_model_path = os.path.join(model_dir, 'success_model.pkl')
            commission_model_path = os.path.join(model_dir, 'commission_model.pkl')
            
            self.success_predictor.save_model(success_model_path)
            if self.commission_predictor.is_trained():
                self.commission_predictor.save_model(commission_model_path)
        except Exception as e:
            # Log but continue if models can't be saved
            print(f"Error saving models: {str(e)}")
    
    def _recommend_leads_for_new_agent(self, limit, agent_info=None):
        """
        Generate lead recommendations for a new agent with no sales history.
        
        Args:
            limit: Maximum number of recommendations
            agent_info: Agent information (optional)
            
        Returns:
            List of lead recommendations
        """
        # Load data
        sales_data = self.data_loader.load_sales_data()
        cards_data = self.data_loader.load_cards_data()
        
        if sales_data is None or cards_data is None:
            return None
        
        # Find top-performing cards across the network
        # Focus on cards with high success rates for new agents
        card_success = sales_data.groupby('card_id').agg({
            'sale_id': 'count',
            'success_flag': 'sum',
            'commission': 'sum'
        }).reset_index()
        
        card_success = card_success.rename(columns={
            'sale_id': 'total_sales',
            'success_flag': 'successful_sales'
        })
        
        card_success['success_rate'] = card_success.apply(
            lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
            axis=1
        )
        
        card_success['avg_commission'] = card_success.apply(
            lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
            axis=1
        )
        
        # Score cards based on success rate (70% weight) and commission (30% weight)
        card_success['beginner_score'] = (
            card_success['success_rate'] * 0.7 +
            (card_success['avg_commission'] / card_success['avg_commission'].max()) * 0.3
        )
        
        # Get top 3 cards for beginners
        top_cards = card_success.sort_values('beginner_score', ascending=False).head(3)
        
        # Generate leads for each top card
        leads = []
        
        for _, card_row in top_cards.iterrows():
            card_id = card_row['card_id']
            
            # Get card details
            card_details = cards_data[cards_data['card_id'] == card_id]
            if len(card_details) == 0:
                continue
                
            card_detail = card_details.iloc[0].to_dict()
            
            # Generate 2 leads per card
            for i in range(2):
                # Generate a customer profile
                customer = self._generate_customer_profile(card_detail, [], [])
                
                # Predict success and commission
                prediction = self.predict_success(customer, card_id)
                
                if prediction and prediction['success_probability'] >= 0.5:
                    leads.append({
                        'customer': customer,
                        'card_id': card_id,
                        'card_details': card_detail,
                        'success_probability': prediction['success_probability'],
                        'expected_commission': prediction['expected_commission'],
                        'key_factors': prediction['key_factors']
                    })
        
        # Sort leads by success probability (more important for new agents)
        leads.sort(key=lambda x: x['success_probability'], reverse=True)
        
        # Return top leads, limited to the requested number
        return leads[:limit]
    
    def _generate_customer_profile(self, card_details, best_segments=None, best_employment_types=None):
        """
        Generate a realistic customer profile suitable for a given card.
        
        Args:
            card_details: Details of the card
            best_segments: List of best performing income segments (optional)
            best_employment_types: List of best performing employment types (optional)
            
        Returns:
            Dictionary with customer profile
        """
        # Parse eligibility criteria for income requirements
        min_income = 300000  # Default
        try:
            if 'eligibility' in card_details and card_details['eligibility']:
                eligibility = card_details['eligibility']
                if '>' in eligibility:
                    min_income_str = eligibility.split('>')[1].strip().split()[0]
                    min_income = float(min_income_str.replace(',', ''))
        except (IndexError, ValueError, AttributeError):
            # Use default if parsing fails
            pass
            
        # Determine income based on best segments or card requirements
        if best_segments and len(best_segments) > 0:
            # Pick a random segment from best_segments
            segment = random.choice(best_segments)
            
            # Generate income based on segment
            if segment == 'Low':
                income = random.randint(min_income, 300000)
            elif segment == 'Medium':
                income = random.randint(300001, 600000)
            elif segment == 'High':
                income = random.randint(600001, 1000000)
            elif segment == 'Very High':
                income = random.randint(1000001, 3000000)
            else:
                # Default to slightly above minimum
                income = int(min_income * random.uniform(1.1, 2.0))
        else:
            # Generate income above minimum requirement with some buffer
            income = int(min_income * random.uniform(1.1, 2.5))
        
        # Choose employment type
        if best_employment_types and len(best_employment_types) > 0:
            employment_type = random.choice(best_employment_types)
        else:
            # Use card name to determine appropriate employment types
            card_name = card_details.get('name', '').lower()
            
            if 'business' in card_name:
                employment_type = random.choice(['Business', 'Self-Employed'])
            elif 'corporate' in card_name:
                employment_type = 'Salaried'
            elif 'student' in card_name:
                employment_type = random.choice(['Student', 'Salaried'])
            else:
                employment_type = random.choice(['Salaried', 'Self-Employed', 'Business'])
        
        # Choose appropriate age based on card type and employment
        if employment_type == 'Student':
            age = random.randint(21, 28)
        elif employment_type in ['Business', 'Self-Employed']:
            age = random.randint(30, 55)
        elif 'premium' in card_name or 'elite' in card_name:
            age = random.randint(35, 65)
        else:
            age = random.randint(25, 50)
            
        # Generate credit score - higher for premium cards
        if 'premium' in card_name or 'elite' in card_name or 'platinum' in card_name:
            credit_score = random.randint(700, 900)
        else:
            credit_score = random.randint(650, 850)
            
        # Create customer profile
        customer = {
            'name': f"Lead {random.randint(1000, 9999)}",
            'age': age,
            'income': income,
            'employment_type': employment_type,
            'credit_score': credit_score,
            'contact_number': f"+91 9{random.randint(100000000, 999999999)}",
            'email': f"lead{random.randint(1000, 9999)}@example.com"
        }
        
        return customer
    
    def _basic_prediction(self, customer_data, card_details):
        """
        Make a basic prediction without using ML models.
        
        Args:
            customer_data: Customer information
            card_details: Card details
            
        Returns:
            Basic prediction dictionary
        """
        # Parse eligibility criteria for income requirements
        min_income = 300000  # Default
        try:
            if 'eligibility' in card_details and card_details['eligibility']:
                eligibility = card_details['eligibility']
                if '>' in eligibility:
                    min_income_str = eligibility.split('>')[1].strip().split()[0]
                    min_income = float(min_income_str.replace(',', ''))
        except (IndexError, ValueError, AttributeError):
            # Use default if parsing fails
            pass
        
        # Calculate income ratio (customer income / minimum required income)
        income = customer_data.get('income', 0)
        income_ratio = income / min_income if min_income > 0 else 1
        
        # Calculate credit score factor (0 to 1)
        credit_score = customer_data.get('credit_score', 0)
        credit_factor = min(1.0, max(0.0, (credit_score - 600) / 300))  # 600 to 900 range
        
        # Calculate employment factor
        employment_type = customer_data.get('employment_type', '')
        employment_factor = 0.7  # Default
        
        card_name = card_details.get('name', '').lower()
        if 'business' in card_name and employment_type in ['Business', 'Self-Employed']:
            employment_factor = 0.9
        elif 'corporate' in card_name and employment_type == 'Salaried':
            employment_factor = 0.9
        elif 'student' in card_name and employment_type == 'Student':
            employment_factor = 0.9
        
        # Calculate age factor
        age = customer_data.get('age', 30)
        age_factor = 0.7  # Default
        
        if 'student' in card_name and age < 30:
            age_factor = 0.9
        elif ('premium' in card_name or 'elite' in card_name) and age > 35:
            age_factor = 0.9
        
        # Calculate overall success probability
        success_prob = (
            (income_ratio * 0.4) + 
            (credit_factor * 0.3) + 
            (employment_factor * 0.2) + 
            (age_factor * 0.1)
        )
        
        # Cap at 0.95 since this is a simple heuristic
        success_prob = min(0.95, success_prob)
        
        # Estimate expected commission
        # Use average commission based on card tier
        if 'premium' in card_name or 'elite' in card_name or 'platinum' in card_name:
            expected_commission = 3000
        elif 'gold' in card_name or 'titanium' in card_name:
            expected_commission = 2000
        else:
            expected_commission = 1000
        
        # Identify key factors
        key_factors = self._identify_key_factors(customer_data, card_details, success_prob)
        
        return {
            'success_probability': success_prob,
            'expected_commission': expected_commission,
            'key_factors': key_factors
        }
    
    def _identify_key_factors(self, customer_data, card_details, success_prob):
        """
        Identify key factors affecting success probability.
        
        Args:
            customer_data: Customer information
            card_details: Card details
            success_prob: Predicted success probability
            
        Returns:
            List of factor dictionaries with impact assessment
        """
        factors = []
        
        # Parse eligibility criteria for income requirements
        min_income = 300000  # Default
        try:
            if 'eligibility' in card_details and card_details['eligibility']:
                eligibility = card_details['eligibility']
                if '>' in eligibility:
                    min_income_str = eligibility.split('>')[1].strip().split()[0]
                    min_income = float(min_income_str.replace(',', ''))
        except (IndexError, ValueError, AttributeError):
            # Use default if parsing fails
            pass
        
        # Check income impact
        income = customer_data.get('income', 0)
        income_ratio = income / min_income if min_income > 0 else 1
        
        if income_ratio < 1:
            factors.append({
                'factor': 'Income below requirement',
                'impact': 'negative',
                'description': f"Customer income (₹{income:,}) is below the minimum requirement of ₹{min_income:,}"
            })
        elif income_ratio > 1.5:
            factors.append({
                'factor': 'Income well above requirement',
                'impact': 'positive',
                'description': f"Customer income (₹{income:,}) exceeds the minimum requirement of ₹{min_income:,}"
            })
        
        # Check credit score impact
        credit_score = customer_data.get('credit_score', 0)
        
        if credit_score < 650:
            factors.append({
                'factor': 'Low credit score',
                'impact': 'negative',
                'description': f"Credit score of {credit_score} is below the recommended minimum of 650"
            })
        elif credit_score >= 750:
            factors.append({
                'factor': 'Excellent credit score',
                'impact': 'positive',
                'description': f"Credit score of {credit_score} is excellent (750+)"
            })
        
        # Check employment type impact
        employment_type = customer_data.get('employment_type', '')
        card_name = card_details.get('name', '').lower()
        
        if 'business' in card_name:
            if employment_type in ['Business', 'Self-Employed']:
                factors.append({
                    'factor': 'Ideal employment type',
                    'impact': 'positive',
                    'description': f"{employment_type} employment type is perfect for this business card"
                })
            else:
                factors.append({
                    'factor': 'Employment type mismatch',
                    'impact': 'negative',
                    'description': f"{employment_type} employment type is not ideal for a business card"
                })
        
        # Check age impact
        age = customer_data.get('age', 0)
        
        if 'student' in card_name and age > 30:
            factors.append({
                'factor': 'Age mismatch for student card',
                'impact': 'negative',
                'description': f"Customer age ({age}) is outside typical range for student cards"
            })
        elif ('premium' in card_name or 'elite' in card_name) and age < 30:
            factors.append({
                'factor': 'Young age for premium card',
                'impact': 'negative',
                'description': f"Customer age ({age}) is younger than typical premium card holders"
            })
        
        return factors
