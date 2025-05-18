"""
GroMo AI Sales Coach - Sample Data Generator

This script generates sample data for testing the GroMo AI Sales Coach application.
It creates data for agents, credit cards, and sales data, and saves it to both
JSON files and MongoDB for testing purposes.
"""

import os
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Get MongoDB connection details from environment or use defaults
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'gromo_ai_coach')

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# Connect to MongoDB
def connect_to_mongodb():
    """Connect to MongoDB database."""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Force a connection to verify it works
        client.server_info()
        db = client[DB_NAME]
        print(f"Connected to MongoDB: {MONGODB_URI}, Database: {DB_NAME}")
        return client, db
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        print("Data will only be saved to JSON files.")
        return None, None

# ===== Generate Agent Data =====
def generate_agents(num_agents=50, db=None):
    """Generate sample agent data."""
    
    cities = [
        'Mumbai', 'Delhi', 'Bengaluru', 'Hyderabad', 'Chennai', 
        'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow',
        'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal',
        'Visakhapatnam', 'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana'
    ]
    
    education_levels = ['Graduate', 'Post Graduate', 'Undergraduate', 'High School']
    
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    agents = []
    for i in range(1, num_agents + 1):
        agent_id = f"AG{1000 + i}"
        
        # Generate random joining date
        days_range = (end_date - start_date).days
        random_days = random.randint(0, days_range)
        joining_date = start_date + timedelta(days=random_days)
        
        # Calculate experience in months
        today = datetime.now()
        experience_months = ((today.year - joining_date.year) * 12 + 
                            today.month - joining_date.month)
        
        # Generate random agent data
        agent = {
            'agent_id': agent_id,
            'name': f"Agent {i}",
            'email': f"agent{i}@gromo.com",
            'phone': f"+91 {random.randint(7000000000, 9999999999)}",
            'location': {
                'city': random.choice(cities),
                'state': 'State',  # Simplified for sample data
                'pincode': f"{random.randint(100000, 999999)}"
            },
            'education': random.choice(education_levels),
            'joining_date': joining_date.strftime('%Y-%m-%d'),
            'experience_months': experience_months,
            'active': random.random() > 0.1,  # 90% active rate
            'rating': round(random.uniform(3.0, 5.0), 1)
        }
        
        agents.append(agent)
    
    # Write to JSON file
    with open('data/agents.json', 'w') as f:
        json.dump(agents, f, indent=2)
    
    # Save to MongoDB if available
    if db is not None:
        try:
            # Clear existing data
            db.agents.delete_many({})
            # Insert new data
            if agents:
                db.agents.insert_many(agents)
                print(f"Saved {len(agents)} agents to MongoDB")
        except Exception as e:
            print(f"Error saving agents to MongoDB: {str(e)}")
    
    return agents

# ===== Generate Credit Card Data =====
def generate_credit_cards(num_cards=20, db=None):
    """Generate sample credit card data."""
    
    card_types = ['Basic', 'Gold', 'Platinum', 'Premium', 'Business', 'Student', 'Travel', 'Cashback', 'Rewards']
    
    bank_names = [
        'State Bank', 'HDFC Bank', 'ICICI Bank', 'Axis Bank', 'Kotak Bank',
        'Yes Bank', 'IndusInd Bank', 'Federal Bank', 'RBL Bank', 'Citi Bank'
    ]
    
    benefits_pool = [
        'Lounge Access', 'Reward Points', 'Cashback', 'Air Miles', 'Hotel Discounts',
        'Travel Insurance', 'Shopping Points', 'EMI Offers', 'Movie Tickets', 'Fuel Surcharge Waiver',
        'Roadside Assistance', 'Car Rental Discounts', 'Dining Rewards', 'Grocery Cashback',
        'Online Shopping Discounts', 'Golf Program', 'Concierge Service', 'Airport Meet & Greet',
        'Zero Foreign Transaction Fee', 'Global Emergency Assistance', 'Lost Card Protection',
        'Extended Warranty', 'Purchase Protection', 'Price Protection', 'Complimentary Airport Transfers'
    ]
    
    cards = []
    for i in range(1, num_cards + 1):
        card_id = f"CC{100000 + i}"
        
        # Generate random card type
        card_type = random.choice(card_types)
        bank_name = random.choice(bank_names)
        
        # Generate card fees based on card type
        if card_type in ['Premium', 'Platinum', 'Business']:
            joining_fee = random.choice([0, 999, 1999, 2999, 4999])
            annual_fee = random.choice([999, 1999, 2999, 4999, 9999])
            min_income = random.choice([600000, 800000, 1000000, 1500000])
        elif card_type in ['Gold', 'Travel', 'Rewards']:
            joining_fee = random.choice([0, 499, 999, 1499])
            annual_fee = random.choice([499, 999, 1499, 1999])
            min_income = random.choice([300000, 400000, 500000, 600000])
        else:
            joining_fee = random.choice([0, 199, 499, 999])
            annual_fee = random.choice([199, 499, 999])
            min_income = random.choice([200000, 250000, 300000, 350000])
        
        # Generate random benefits
        num_benefits = random.randint(4, 8)
        benefits = random.sample(benefits_pool, num_benefits)
        
        # Generate reward rate
        reward_rate = round(random.uniform(0.5, 5.0), 1)
        
        # Generate interest rate
        interest_rate = round(random.uniform(24.0, 42.0), 1)
        
        # Generate credit limit range
        if card_type in ['Premium', 'Platinum', 'Business']:
            credit_limit_min = random.choice([200000, 300000, 500000])
            credit_limit_max = random.choice([1000000, 1500000, 2000000])
        elif card_type in ['Gold', 'Travel', 'Rewards']:
            credit_limit_min = random.choice([100000, 150000, 200000])
            credit_limit_max = random.choice([500000, 750000, 1000000])
        else:
            credit_limit_min = random.choice([20000, 50000, 75000])
            credit_limit_max = random.choice([100000, 150000, 200000])
        
        credit_limit_range = f"₹{credit_limit_min:,} - ₹{credit_limit_max:,}"
        
        # Create card object
        card = {
            'card_id': card_id,
            'name': f"{bank_name} {card_type} Card",
            'issuer': bank_name,
            'type': card_type,
            'joining_fee': joining_fee,
            'annual_fee': annual_fee,
            'interest_rate': interest_rate,
            'eligibility': f"Income > ₹{min_income}",
            'reward_rate': f"{reward_rate}%",
            'credit_limit_range': credit_limit_range,
            'benefits': benefits,
            'feature_summary': f"The {bank_name} {card_type} Card offers {', '.join(benefits[:3])} and more.",
        }
        
        cards.append(card)
    
    # Write to JSON file
    with open('data/credit_cards.json', 'w') as f:
        json.dump(cards, f, indent=2)
    
    # Save to MongoDB if available
    if db is not None:
        try:
            # Clear existing data
            db.credit_cards.delete_many({})
            # Insert new data
            if cards:
                db.credit_cards.insert_many(cards)
                print(f"Saved {len(cards)} credit cards to MongoDB")
        except Exception as e:
            print(f"Error saving credit cards to MongoDB: {str(e)}")
    
    return cards

# ===== Generate Sales Data =====
def generate_sales(agents, cards, num_sales=1000, db=None):
    """Generate sample sales data."""
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now()
    
    rejection_reasons = [
        'Low Credit Score', 'Insufficient Income', 'Incomplete Documentation',
        'High Debt-to-Income Ratio', 'Employment Verification Failed', 'Identity Verification Failed',
        'Existing Card Default', 'Address Verification Failed', 'Incorrect Information'
    ]
    
    employment_types = ['Salaried', 'Self-Employed', 'Business', 'Professional', 'Government', 'Student']
    
    sales = []
    for i in range(1, num_sales + 1):
        sale_id = f"S{100000 + i}"
        
        # Select random agent and card
        agent = random.choice(agents)
        card = random.choice(cards)
        
        # Ensure agent joined before sale date
        agent_joining = datetime.strptime(agent['joining_date'], '%Y-%m-%d')
        max_date = min(end_date, datetime.now())
        
        if agent_joining > max_date:
            # Skip if agent joined after max date
            continue
            
        # Random date between agent joining date and now
        days_range = (max_date - agent_joining).days
        if days_range <= 0:
            continue
            
        random_days = random.randint(0, days_range)
        sale_date = agent_joining + timedelta(days=random_days)
        
        # Generate customer data
        customer_age = random.randint(21, 65)
        
        # Determine income based on card eligibility
        min_income_str = card['eligibility'].split('>')[1].strip().split()[0]
        min_income = int(min_income_str.replace('₹', '').replace(',', ''))
        
        # Generate income somewhat above the minimum
        income_multiplier = random.uniform(1.0, 3.0)
        customer_income = int(min_income * income_multiplier)
        
        # Randomly determine success
        # Higher probability of success if income is much higher than minimum
        success_prob = 0.5 + ((income_multiplier - 1.0) / 4)  # Scale to 0.5-1.0 range
        success_flag = random.random() < success_prob
        
        # Generate commission for successful sales
        commission = 0
        if success_flag:
            # Base commission tied to card type
            if card['type'] in ['Premium', 'Platinum', 'Business']:
                base_commission = random.randint(2500, 5000)
            elif card['type'] in ['Gold', 'Travel', 'Rewards']:
                base_commission = random.randint(1500, 3000)
            else:
                base_commission = random.randint(500, 1500)
                
            # Add some random variation
            commission = max(500, base_commission + random.randint(-500, 500))
        
        # Generate customer profile
        customer_data = {
            'age': customer_age,
            'income': customer_income,
            'employment_type': random.choice(employment_types),
            'credit_score': random.randint(550, 900)
        }
        
        # Generate application details
        application_details = {
            'application_date': sale_date.strftime('%Y-%m-%d'),
            'processing_time_days': random.randint(3, 14)
        }
        
        if not success_flag:
            application_details['rejection_reason'] = random.choice(rejection_reasons)
        
        # Build sale record
        sale = {
            'sale_id': sale_id,
            'agent_id': agent['agent_id'],
            'card_id': card['card_id'],
            'date': sale_date.strftime('%Y-%m-%d'),
            'success_flag': success_flag,
            'commission': commission,
            'customer_details': customer_data,
            'location': agent['location'],
            'application_details': application_details
        }
        
        sales.append(sale)
    
    # Write to JSON file
    with open('data/sales.json', 'w') as f:
        json.dump(sales, f, indent=2)
    
    # Save to MongoDB if available
    if db is not None:
        try:
            # Clear existing data
            db.sales.delete_many({})
            # Insert new data
            if sales:
                db.sales.insert_many(sales)
                print(f"Saved {len(sales)} sales records to MongoDB")
        except Exception as e:
            print(f"Error saving sales data to MongoDB: {str(e)}")
    
    return sales

# ===== Generate All Sample Data =====
def generate_all_sample_data():
    """Generate all sample data for testing."""
    
    # Connect to MongoDB
    mongo_client, db = connect_to_mongodb()
    
    try:
        print("Generating sample agent data...")
        agents = generate_agents(num_agents=50, db=db)
        print(f"Generated {len(agents)} agents.")
        
        print("Generating sample credit card data...")
        cards = generate_credit_cards(num_cards=20, db=db)
        print(f"Generated {len(cards)} credit cards.")
        
        print("Generating sample sales data...")
        sales = generate_sales(agents, cards, num_sales=2000, db=db)
        print(f"Generated {len(sales)} sales records.")
        
        print("Sample data generation complete.")
        print("Data files saved in the 'data' directory.")
        
        if db is not None:
            print("Data also saved to MongoDB database.")
    finally:
        # Close MongoDB connection if open
        if mongo_client is not None:
            mongo_client.close()
            print("MongoDB connection closed.")

# Run the generator
if __name__ == "__main__":
    generate_all_sample_data()
