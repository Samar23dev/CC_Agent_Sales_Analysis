from pymongo import MongoClient, ASCENDING, IndexModel
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np
import math
from collections import defaultdict
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Faker
fake = Faker()

# MongoDB connection using environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'credit_card_sales')

if not MONGODB_URI:
    raise ValueError("MongoDB URI not found in environment variables. Please set it in your .env file.")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# --- Global lists for generated data (populated in main) ---
# These are made global for easier access in generate_random_sales
# It's generally better to pass them as arguments if functions become more complex
credit_cards_list = []
agents_list = []


def export_to_json(collection_name, filename):
    """Export MongoDB collection to JSON file"""
    collection = db[collection_name]
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # Get all documents from collection
    # For very large collections, consider batching or mongoexport
    documents = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB _id field

    # Write to JSON file
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=4, ensure_ascii=False, default=str) # Add default=str for datetime etc.

    print(f"Exported {len(documents)} records from '{collection_name}' to {filepath}")

def generate_card_id():
    """Generate a realistic credit card ID"""
    return f"CC{fake.random_number(digits=6, fix_len=True)}"

def generate_agent_id():
    """Generate a realistic agent ID"""
    return f"AG{fake.random_number(digits=4, fix_len=True)}"

def generate_application_id():
    """Generate a realistic application ID"""
    return f"APP{fake.random_number(digits=8, fix_len=True)}"

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
    for i in range(num_cards): # Use a unique element for ID generation if needed
        card_type = random.choice(card_types)
        card_id = f"CC{100000 + i}" # Simpler unique ID for controlled generation
        card = {
            "card_id": card_id, # Use generated ID
            "name": f"{card_type} {random.choice(['Rewards', 'Elite', 'Plus', 'Premium', 'Select'])} Card",
            "benefits": random.sample(random.choice(benefits_list), k=random.randint(1,3)), # Sample benefits
            "eligibility": f"Income > {random.randint(3, 15) * 100000} per annum",
            "joining_fee": random.choice([0, 499, 999, 1999, 2999, 4999, 9999]),
            "annual_fee": random.choice([0, 499, 999, 1999, 2999, 4999]),
            "interest_rate": round(random.uniform(15.0, 45.0), 2),
            "credit_limit_range": f"₹{random.randint(5, 20) * 10000} - ₹{random.randint(20, 100) * 10000}",
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
    for i in range(num_agents): # Simpler unique ID
        agent_id = f"AG{1000 + i}"
        agent = {
            "agent_id": agent_id, # Use generated ID
            "name": fake.name(),
            "location": random.choice(cities),
            "preferred_language": random.choice(languages),
            "experience_years": random.randint(1, 15),
            "specialization": random.choice(["Travel Cards", "Shopping Cards", "Premium Cards", "Business Cards", "All Rounder"]),
            "performance_rating": round(random.uniform(3.0, 5.0), 1),
            "contact_number": fake.phone_number(),
            "email": fake.unique.email(), # Ensure unique emails if needed
            "joining_date": (datetime.now() - timedelta(days=random.randint(30, 3650))).isoformat()
        }
        agents.append(agent)
    return agents

def generate_random_sales(num_sales):
    """Generate random sales data using global credit_cards_list and agents_list"""
    global credit_cards_list, agents_list # Access global lists

    if not credit_cards_list or not agents_list:
        raise ValueError("Credit cards or agents list is empty. Generate them first.")

    sales_data = []
    start_date = datetime.now() - timedelta(days=365) # Sales within the last year

    for i in range(num_sales):
        agent = random.choice(agents_list)
        card = random.choice(credit_cards_list)
        sale_date = start_date + timedelta(days=random.randint(0, 364), seconds=random.randint(0, 86399))
        application_date = sale_date - timedelta(days=random.randint(0, 5)) # App date before or on sale date
        is_successful = random.random() > 0.2 # 80% success rate

        sale = {
            "sale_id": f"SALE{1000000 + i}", # Unique sale ID
            "agent_id": agent["agent_id"],
            "card_id": card["card_id"],
            "location": {
                "city": agent["location"], # Sale location is agent's location
                "pincode": fake.postcode_in_state() if hasattr(fake, 'postcode_in_state') else fake.postcode(), # More realistic pincode if available
                "coordinates": {
                    "latitude": float(fake.latitude()),
                    "longitude": float(fake.longitude())
                }
            },
            "date": sale_date.isoformat(),
            "success_flag": is_successful,
            "commission": random.randint(500, 5000) if is_successful else 0, # Commission only on success
            "customer_details": {
                "name": fake.name(),
                "age": random.randint(18, 70),
                "income": random.randint(25, 200) * 10000,
                "employment_type": random.choice(["Salaried", "Self-Employed", "Business", "Student", "Retired"]),
                "credit_score": random.randint(300, 900)
            },
            "application_details": {
                "application_id": f"APP{50000000 + i}", # Unique app ID
                "application_date": application_date.isoformat(),
                "processing_time_days": random.randint(1, 15) if is_successful else random.randint(1,7),
                "rejection_reason": None if is_successful else random.choice([
                    "Low Credit Score", "Insufficient Income", "Existing Debt",
                    "Employment Verification Failed", "Incomplete Application", "High Risk Profile"
                ])
            }
        }
        sales_data.append(sale)

    return sales_data

def calculate_card_performance(location_city):
    """
    Calculate the best performing credit card in a given location
    Formula: score = (approval_rate * 0.5) + (normalized_avg_commission * 0.3) + (normalized_volume_sold * 0.2)
    """
    pipeline = [
        {"$match": {"location.city": location_city}},
        {"$group": {
            "_id": "$card_id",
            "total_sales": {"$sum": 1},
            "successful_sales": {"$sum": {"$cond": ["$success_flag", 1, 0]}},
            "total_commission": {"$sum": "$commission"} # Sums commission only for successful sales if data is clean
        }},
        {"$project": {
            "_id": 1, # Keep card_id
            "approval_rate": {
                "$cond": {
                    "if": {"$eq": ["$total_sales", 0]},
                    "then": 0, # Avoid division by zero
                    "else": {"$divide": ["$successful_sales", "$total_sales"]}
                }
            },
            "avg_commission": {
                "$cond": {
                    "if": {"$eq": ["$successful_sales", 0]}, # Avg commission on successful sales
                    "then": 0,
                    "else": {"$divide": ["$total_commission", "$successful_sales"]}
                }
            },
            "volume_sold": "$total_sales" # Or successful_sales if that's the intended volume
        }}
    ]

    results = list(db.sales.aggregate(pipeline))

    if not results:
        print(f"No sales data found for location: {location_city}")
        return None

    # Normalize avg_commission and volume_sold (0 to 1 range)
    # Handle cases where all values might be zero or max is zero
    max_commission = max(r["avg_commission"] for r in results) if any(r["avg_commission"] > 0 for r in results) else 0
    max_volume = max(r["volume_sold"] for r in results) if any(r["volume_sold"] > 0 for r in results) else 0

    scored_results = []
    for r in results:
        norm_avg_commission = (r["avg_commission"] / max_commission) if max_commission > 0 else 0
        norm_volume_sold = (r["volume_sold"] / max_volume) if max_volume > 0 else 0

        score = (
            (r["approval_rate"] * 0.5) +
            (norm_avg_commission * 0.3) +
            (norm_volume_sold * 0.2)
        )
        r["final_score"] = score
        scored_results.append(r)

    if not scored_results:
        return None

    return sorted(scored_results, key=lambda x: x["final_score"], reverse=True)[0]


def setup_indexes():
    """Create indexes for better query performance."""
    # Index for sales collection
    sales_indexes = [
        IndexModel([("location.city", ASCENDING)], name="location_city_idx"),
        IndexModel([("card_id", ASCENDING)], name="sales_card_id_idx"),
        IndexModel([("agent_id", ASCENDING)], name="sales_agent_id_idx"),
        IndexModel([("date", ASCENDING)], name="sales_date_idx")
    ]
    try:
        db.sales.create_indexes(sales_indexes)
        print("Sales collection indexes created/ensured.")
    except Exception as e:
        print(f"Error creating sales indexes: {e}")

    # Index for credit_cards collection
    credit_cards_indexes = [
        IndexModel([("card_id", ASCENDING)], name="card_id_idx", unique=True)
    ]
    try:
        db.credit_cards.create_indexes(credit_cards_indexes)
        print("Credit cards collection indexes created/ensured.")
    except Exception as e:
        print(f"Error creating credit_cards indexes: {e}")

    # Index for agents collection
    agents_indexes = [
        IndexModel([("agent_id", ASCENDING)], name="agent_id_idx", unique=True),
        IndexModel([("location", ASCENDING)], name="agent_location_idx")
    ]
    try:
        db.agents.create_indexes(agents_indexes)
        print("Agents collection indexes created/ensured.")
    except Exception as e:
        print(f"Error creating agents indexes: {e}")

def calculate_time_decay_weight(sale_date_str, reference_date=None):
    """
    Calculate time decay weight giving more importance to recent sales
    
    Parameters:
    - sale_date_str: ISO format date string
    - reference_date: Date to compare against (defaults to current date)
    
    Returns:
    - weight between 0 and 1, where 1 is most recent
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    sale_date = datetime.fromisoformat(sale_date_str)
    days_diff = (reference_date - sale_date).days
    
    # Exponential decay function: weight = e^(-λ * days)
    # λ controls decay rate - 0.005 means sales from ~140 days ago have half the weight
    decay_factor = 0.005
    weight = math.exp(-decay_factor * max(0, days_diff))
    
    return weight

def calculate_demographic_fit_score(card_id, customer_details):
    """
    Calculate how well a card fits customer demographics
    
    Returns:
    - Score between 0 and 1
    """
    # Get card details
    card = db.credit_cards.find_one({"card_id": card_id})
    if not card:
        return 0.5  # Default middle score if card not found
    
    score = 0.5  # Base score
    
    # Parse income eligibility from card
    try:
        min_income_str = card.get("eligibility", "").split(">")[1].strip().split()[0]
        min_income = float(min_income_str.replace(",", ""))
    except (IndexError, ValueError, AttributeError):
        min_income = 300000  # Default if parsing fails
    
    # Income fit - higher score if customer income is well above minimum
    customer_income = customer_details.get("income", 0)
    income_ratio = customer_income / min_income if min_income > 0 else 1
    income_score = min(1.0, income_ratio / 2)  # Cap at 1.0
    
    # Age-based card match
    age = customer_details.get("age", 30)
    age_score = 0.5  # Default
    if "Student" in card.get("name", "") and age < 25:
        age_score = 0.9
    elif "Business" in card.get("name", "") and 25 <= age <= 55:
        age_score = 0.8
    elif "Premium" in card.get("name", "") and age > 40:
        age_score = 0.8
    
    # Employment type match
    emp_type = customer_details.get("employment_type", "")
    emp_score = 0.5  # Default
    if "Business" in card.get("name", "") and emp_type in ["Business", "Self-Employed"]:
        emp_score = 0.9
    elif "Corporate" in card.get("name", "") and emp_type == "Salaried":
        emp_score = 0.8
    
    # Calculate weighted average of all factors
    final_score = (income_score * 0.5) + (age_score * 0.3) + (emp_score * 0.2)
    return final_score

def get_monthly_sales_trend(card_id, location_city, months_back=6):
    """
    Calculate monthly sales trend metrics for a specific card at a location
    
    Returns:
    - Dictionary with monthly_growth and consistency_score
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months_back)
    
    # Get sales within time range for the location and card
    sales = list(db.sales.find({
        "card_id": card_id,
        "location.city": location_city,
        "date": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
    }))
    
    if not sales:
        return {"monthly_growth": 0, "consistency_score": 0}
    
    # Group sales by month
    monthly_counts = defaultdict(int)
    for sale in sales:
        sale_date = datetime.fromisoformat(sale["date"])
        month_key = f"{sale_date.year}-{sale_date.month:02d}"
        monthly_counts[month_key] += 1
    
    # Sort months chronologically
    months = sorted(monthly_counts.keys())
    if len(months) <= 1:
        return {"monthly_growth": 0, "consistency_score": 0}
    
    # Calculate month-over-month growth
    monthly_volumes = [monthly_counts[m] for m in months]
    growth_rates = [(monthly_volumes[i] - monthly_volumes[i-1]) / max(1, monthly_volumes[i-1]) 
                    for i in range(1, len(monthly_volumes))]
    
    # Average growth rate (last 3 months weighted higher)
    if len(growth_rates) >= 3:
        weighted_growth = (sum(growth_rates[:-3]) + 2 * sum(growth_rates[-3:])) / (len(growth_rates) + 3)
    else:
        weighted_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0
    
    # Consistency score - lower variance means more consistent performance
    consistency = 1.0 - min(1.0, np.std(monthly_volumes) / max(1, np.mean(monthly_volumes)))
    
    return {
        "monthly_growth": weighted_growth,
        "consistency_score": consistency
    }

def get_top_performing_cards(location_city, top_n=3):
    """
    Calculate the top N performing credit cards in a given location
    Using advanced metrics and algorithms
    """
    reference_date = datetime.now()
    
    # First, get all cards sold in this location
    cards_in_location = db.sales.distinct("card_id", {"location.city": location_city})
    
    if not cards_in_location:
        print(f"No sales data found for location: {location_city}")
        return []
    
    # Calculate base metrics for each card
    card_metrics = []
    
    for card_id in cards_in_location:
        # Get all sales for this card in this location
        sales = list(db.sales.find({"card_id": card_id, "location.city": location_city}))
        if not sales:
            continue
        
        # Base metrics
        total_sales = len(sales)
        successful_sales = sum(1 for sale in sales if sale.get("success_flag", False))
        total_commission = sum(sale.get("commission", 0) for sale in sales)
        
        # Approval rate
        approval_rate = successful_sales / total_sales if total_sales > 0 else 0
        
        # Average commission
        avg_commission = total_commission / successful_sales if successful_sales > 0 else 0
        
        # Time-weighted metrics - recent sales matter more
        time_weighted_sales = sum(calculate_time_decay_weight(sale["date"], reference_date) 
                                 for sale in sales)
        
        time_weighted_success = sum(calculate_time_decay_weight(sale["date"], reference_date) 
                                   for sale in sales if sale.get("success_flag", False))
        
        recent_performance = time_weighted_success / time_weighted_sales if time_weighted_sales > 0 else 0
        
        # Customer demographic fitness - average score across all sales
        demographic_scores = [calculate_demographic_fit_score(card_id, sale.get("customer_details", {})) 
                             for sale in sales]
        avg_demographic_fit = sum(demographic_scores) / len(demographic_scores) if demographic_scores else 0.5
        
        # Monthly sales trends
        trend_metrics = get_monthly_sales_trend(card_id, location_city)
        
        # Calculate card's profitability - commission per application
        profitability = total_commission / total_sales if total_sales > 0 else 0
        
        # Store metrics
        card_metrics.append({
            "card_id": card_id,
            "base_metrics": {
                "total_sales": total_sales,
                "successful_sales": successful_sales,
                "approval_rate": approval_rate,
                "avg_commission": avg_commission
            },
            "advanced_metrics": {
                "time_weighted_performance": recent_performance,
                "demographic_fit": avg_demographic_fit,
                "monthly_growth": trend_metrics["monthly_growth"],
                "consistency_score": trend_metrics["consistency_score"],
                "profitability": profitability
            }
        })
    
    if not card_metrics:
        return []
    
    # Calculate final score - weighted combination of all metrics
    for card in card_metrics:
        # Get base metrics
        approval_rate = card["base_metrics"]["approval_rate"]
        avg_commission = card["base_metrics"]["avg_commission"]
        total_sales = card["base_metrics"]["total_sales"]
        
        # Get advanced metrics
        recent_perf = card["advanced_metrics"]["time_weighted_performance"]
        demo_fit = card["advanced_metrics"]["demographic_fit"]
        growth = card["advanced_metrics"]["monthly_growth"]
        consistency = card["advanced_metrics"]["consistency_score"]
        profitability = card["advanced_metrics"]["profitability"]
        
        # Normalize avg_commission and total_sales
        max_commission = max(c["base_metrics"]["avg_commission"] for c in card_metrics)
        max_sales = max(c["base_metrics"]["total_sales"] for c in card_metrics)
        
        norm_commission = avg_commission / max_commission if max_commission > 0 else 0
        norm_sales = total_sales / max_sales if max_sales > 0 else 0
        
        # Weighted final score - weights can be adjusted based on business priorities
        card["final_score"] = (
            (approval_rate * 0.15) +                  # Approval rate
            (norm_commission * 0.15) +                # Normalized commission
            (norm_sales * 0.10) +                     # Normalized sales volume
            (recent_perf * 0.20) +                    # Time-weighted performance
            (demo_fit * 0.15) +                       # Demographic fit
            (max(0, growth) * 0.10) +                 # Growth trend (only positive growth counts)
            (consistency * 0.10) +                    # Consistency score
            (profitability / max_commission * 0.05 if max_commission > 0 else 0)  # Normalized profitability
        )
    
    # Sort by final score and get top N
    top_cards = sorted(card_metrics, key=lambda x: x["final_score"], reverse=True)[:top_n]
    
    # Fetch full card details for the top cards
    result = []
    for card in top_cards:
        card_details = db.credit_cards.find_one({"card_id": card["card_id"]})
        if card_details:
            result.append({
                "metrics": card,
                "details": card_details
            })
    
    return result

def display_top_cards(location_city, top_n=3):
    """
    Display the top N performing credit cards for a specific location
    with detailed metrics
    """
    top_cards = get_top_performing_cards(location_city, top_n)
    
    if not top_cards:
        print(f"No card performance data available for {location_city}")
        return
    
    print(f"\n===== TOP {len(top_cards)} PERFORMING CREDIT CARDS IN {location_city.upper()} =====")
    
    for i, card_data in enumerate(top_cards, 1):
        card_details = card_data["details"]
        metrics = card_data["metrics"]
        
        print(f"\n{i}. {card_details.get('name', 'Unknown Card')}")
        print(f"   Card ID: {metrics['card_id']}")
        print(f"   Final Score: {metrics['final_score']:.4f}")
        
        print("\n   Base Metrics:")
        print(f"   - Approval Rate: {metrics['base_metrics']['approval_rate']*100:.2f}%")
        print(f"   - Average Commission: ₹{metrics['base_metrics']['avg_commission']:.2f}")
        print(f"   - Total Applications: {metrics['base_metrics']['total_sales']}")
        print(f"   - Successful Sales: {metrics['base_metrics']['successful_sales']}")
        
        print("\n   Advanced Metrics:")
        print(f"   - Recent Performance: {metrics['advanced_metrics']['time_weighted_performance']:.4f}")
        print(f"   - Demographic Fit: {metrics['advanced_metrics']['demographic_fit']:.4f}")
        print(f"   - Monthly Growth: {metrics['advanced_metrics']['monthly_growth']*100:.2f}%")
        print(f"   - Consistency Score: {metrics['advanced_metrics']['consistency_score']:.4f}")
        print(f"   - Profitability: ₹{metrics['advanced_metrics']['profitability']:.2f} per application")
        
        print("\n   Card Features:")
        print(f"   - Type: {card_details.get('name', 'N/A')}")
        print(f"   - Benefits: {', '.join(card_details.get('benefits', ['N/A']))}")
        print(f"   - Eligibility: {card_details.get('eligibility', 'N/A')}")
        print(f"   - Joining Fee: ₹{card_details.get('joining_fee', 'N/A')}")
        print(f"   - Annual Fee: ₹{card_details.get('annual_fee', 'N/A')}")
        print(f"   - Interest Rate: {card_details.get('interest_rate', 'N/A')}%")
        print(f"   - Reward Rate: {card_details.get('reward_rate', 'N/A')}")
        
        print("\n   ---------------------------------------------------")


def main():
    global credit_cards_list, agents_list # To assign generated data

    run_data_generation = True # Set to False to skip regeneration and use existing DB data

    try:
        if run_data_generation:
            # Clear existing collections (optional, use with caution)
            # print("Dropping existing collections...")
            # db.credit_cards.drop()
            # db.agents.drop()
            # db.sales.drop()
            # print("Collections dropped.")

            # Generate and insert sample data
            print("Generating data...")
            credit_cards_list = generate_credit_cards(15)  # Generate 15 credit cards
            agents_list = generate_agents(30)      # Generate 30 agents

            # Insert sample data
            if credit_cards_list:
                db.credit_cards.insert_many(credit_cards_list)
                print(f"Inserted {len(credit_cards_list)} credit cards.")
            if agents_list:
                db.agents.insert_many(agents_list)
                print(f"Inserted {len(agents_list)} agents.")

            # Generate and insert random sales data
            # Ensure credit_cards_list and agents_list are populated before calling this
            sales_data = generate_random_sales(500)  # Generate 500 sales records
            if sales_data:
                db.sales.insert_many(sales_data)
                print(f"Inserted {len(sales_data)} sales records.")

            # Export collections to JSON files
            export_to_json('credit_cards', 'credit_cards.json')
            export_to_json('agents', 'agents.json')
            export_to_json('sales', 'sales.json')
        else:
            print("Skipping data generation. Using existing data in MongoDB.")
            # If not generating, populate lists from DB for generate_random_sales if it were to be called
            # or for other functions that might rely on these lists.
            # However, calculate_card_performance queries DB directly, so these lists aren't strictly needed
            # if generation is skipped and analysis is the only goal.
            credit_cards_list = list(db.credit_cards.find({}))
            agents_list = list(db.agents.find({}))


        # Setup database indexes (idempotent, safe to run multiple times)
        print("\nSetting up database indexes...")
        setup_indexes()

        # Example: Calculate best performing card in a specific city
        target_city = "Mumbai" # Or pick one from your generated agent locations    
        print(f"\nCalculating top 3 performing cards in {target_city}...")
        display_top_cards(target_city, top_n=3)

        print("--------------------------------")
        # Print some statistics
        print("\n--- Database Statistics ---")
        print(f"Total Credit Cards in DB: {db.credit_cards.count_documents({})}")
        print(f"Total Agents in DB: {db.agents.count_documents({})}")
        print(f"Total Sales Records in DB: {db.sales.count_documents({})}")

    except ValueError as ve:
        print(f"Configuration Error: {str(ve)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc() # For more detailed error info during development

if __name__ == "__main__":
    main()