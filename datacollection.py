from pymongo import MongoClient
from faker import Faker
import random
from datetime import datetime, timedelta
import uuid
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Faker
fake = Faker()

# MongoDB connection using environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'credit_card_sales')

if not MONGODB_URI:
    raise ValueError("MongoDB URI not found in environment variables")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

def export_to_json(collection, filename):
    """Export MongoDB collection to JSON file"""
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Get all documents from collection
    documents = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB _id field
    
    # Write to JSON file
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=4, ensure_ascii=False)
    
    print(f"Exported {len(documents)} records to {filepath}")

def generate_card_id():
    """Generate a realistic credit card ID"""
    return f"CC{fake.random_number(digits=6)}"

def generate_agent_id():
    """Generate a realistic agent ID"""
    return f"AG{fake.random_number(digits=4)}"

def generate_application_id():
    """Generate a realistic application ID"""
    return f"APP{fake.random_number(digits=8)}"

def generate_credit_cards(num_cards=10):
    card_types = [
        "Platinum", "Gold", "Titanium", "Elite", "Premium", "Signature",
        "Travel", "Shopping", "Rewards", "Business", "Student", "Corporate"
    ]
    
    benefits_list = [
        ["Lounge Access", "Reward Points", "Cashback"],
        ["Air Miles", "Hotel Discounts", "Travel Insurance"],
        ["Shopping Points", "EMI Offers", "Movie Tickets"],
        ["Fuel Surcharge Waiver", "Roadside Assistance", "Car Rental Discounts"],
        ["Dining Rewards", "Grocery Cashback", "Online Shopping Discounts"],
        ["Golf Program", "Concierge Service", "Airport Meet & Greet"],
        ["Zero Foreign Transaction Fee", "Global Emergency Assistance", "Lost Card Protection"],
        ["Extended Warranty", "Purchase Protection", "Price Protection"],
        ["Complimentary Airport Transfers", "Priority Pass", "Hotel Status Upgrade"],
        ["Fuel Surcharge Waiver", "Railway Lounge Access", "Movie Ticket Offers"]
    ]
    
    cards = []
    for _ in range(num_cards):
        card_type = random.choice(card_types)
        card = {
            "card_id": generate_card_id(),
            "name": f"{card_type} {random.choice(['Rewards', 'Elite', 'Plus', 'Premium', 'Select'])}",
            "benefits": random.choice(benefits_list),
            "eligibility": f"Income > {random.randint(300000, 1500000)} per annum",
            "joining_fee": random.choice([0, 500, 1000, 2000, 3000, 5000, 10000]),
            "annual_fee": random.choice([0, 500, 1000, 2000, 3000, 5000]),
            "interest_rate": round(random.uniform(15.0, 45.0), 2),
            "credit_limit_range": f"₹{random.randint(50000, 200000)} - ₹{random.randint(200000, 1000000)}",
            "reward_rate": f"{random.randint(1, 5)}% on {random.choice(['all purchases', 'dining', 'travel', 'shopping', 'groceries'])}"
        }
        cards.append(card)
    return cards

def generate_agents(num_agents=20):
    cities = [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata",
        "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur",
        "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara",
        "Ghaziabad", "Ludhiana"
    ]
    
    languages = ["Hindi", "English", "Marathi", "Tamil", "Telugu", "Kannada", "Bengali", "Gujarati"]
    
    agents = []
    for _ in range(num_agents):
        agent = {
            "agent_id": generate_agent_id(),
            "name": fake.name(),
            "location": random.choice(cities),
            "preferred_language": random.choice(languages),
            "experience_years": random.randint(1, 15),
            "specialization": random.choice(["Travel Cards", "Shopping Cards", "Premium Cards", "Business Cards"]),
            "performance_rating": round(random.uniform(3.0, 5.0), 1),
            "contact_number": fake.phone_number(),
            "email": fake.email(),
            "joining_date": (datetime.now() - timedelta(days=random.randint(0, 3650))).isoformat()
        }
        agents.append(agent)
    return agents

def generate_random_sales(num_sales):
    sales_data = []
    
    for _ in range(num_sales):
        agent = random.choice(agents)
        card = random.choice(credit_cards)
        
        sale = {
            "agent_id": agent["agent_id"],
            "card_id": card["card_id"],
            "location": {
                "city": agent["location"],
                "pincode": fake.postcode(),
                "coordinates": {
                    "latitude": float(fake.latitude()),
                    "longitude": float(fake.longitude())
                }
            },
            "date": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
            "success_flag": random.choice([True, False]),
            "commission": random.randint(1000, 5000),
            "customer_details": {
                "name": fake.name(),
                "age": random.randint(18, 70),
                "income": random.randint(300000, 2000000),
                "employment_type": random.choice(["Salaried", "Self-Employed", "Business"]),
                "credit_score": random.randint(300, 900)
            },
            "application_details": {
                "application_id": generate_application_id(),
                "application_date": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                "processing_time_days": random.randint(1, 15),
                "rejection_reason": None if random.random() > 0.3 else random.choice([
                    "Low Credit Score", "Insufficient Income", "Existing Debt", "Employment Verification Failed"
                ])
            }
        }
        sales_data.append(sale)
    
    return sales_data

def calculate_card_performance(location):
    """
    Calculate the best performing credit card in a given location
    Formula: score = (approval_rate * 0.5) + (avg_commission * 0.3) + (volume_sold * 0.2)
    """
    pipeline = [
        {"$match": {"location.city": location}},
        {"$group": {
            "_id": "$card_id",
            "total_sales": {"$sum": 1},
            "successful_sales": {"$sum": {"$cond": ["$success_flag", 1, 0]}},
            "total_commission": {"$sum": "$commission"}
        }},
        {"$project": {
            "approval_rate": {"$divide": ["$successful_sales", "$total_sales"]},
            "avg_commission": {"$divide": ["$total_commission", "$total_sales"]},
            "volume_sold": "$total_sales"
        }}
    ]
    
    results = list(db.sales.aggregate(pipeline))
    
    # Normalize and calculate final scores
    if results:
        max_commission = max(r["avg_commission"] for r in results)
        max_volume = max(r["volume_sold"] for r in results)
        
        for r in results:
            score = (
                (r["approval_rate"] * 0.5) +
                ((r["avg_commission"] / max_commission) * 0.3) +
                ((r["volume_sold"] / max_volume) * 0.2)
            )
            r["final_score"] = score
        
        return sorted(results, key=lambda x: x["final_score"], reverse=True)[0]
    
    return None

def main():
    try:
        # Clear existing collections
        db.credit_cards.drop()
        db.agents.drop()
        db.sales.drop()
        
        # Generate and insert sample data
        global credit_cards, agents
        credit_cards = generate_credit_cards(15)  # Generate 15 credit cards
        agents = generate_agents(30)  # Generate 30 agents
        
        # Insert sample data
        db.credit_cards.insert_many(credit_cards)
        db.agents.insert_many(agents)
        
        # Generate and insert random sales data
        sales_data = generate_random_sales(2000)  # Generate 2000 sales records
        db.sales.insert_many(sales_data)
        
        # Export collections to JSON files
        export_to_json(db.credit_cards, 'credit_cards.json')
        export_to_json(db.agents, 'agents.json')
        export_to_json(db.sales, 'sales.json')
        
        # Example: Calculate best performing card in Mumbai
        best_card = calculate_card_performance("Mumbai")
        if best_card:
            card_details = db.credit_cards.find_one({"card_id": best_card["_id"]})
            print(f"\nBest performing card in Mumbai:")
            print(f"Card Name: {card_details['name']}")
            print(f"Approval Rate: {best_card['approval_rate']*100:.2f}%")
            print(f"Average Commission: ₹{best_card['avg_commission']:.2f}")
            print(f"Volume Sold: {best_card['volume_sold']}")
            print(f"Final Score: {best_card['final_score']:.3f}")
            
            # Print some statistics
            print("\nDatabase Statistics:")
            print(f"Total Credit Cards: {len(credit_cards)}")
            print(f"Total Agents: {len(agents)}")
            print(f"Total Sales Records: {len(sales_data)}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
