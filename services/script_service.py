"""
GroMo AI Sales Coach - Script Service

This module provides services for generating sales scripts and 
objection handling techniques for credit cards.
"""

import random
import pandas as pd
import numpy as np

from data.data_loader import DataLoader


class ScriptService:
    """Service for script-related operations."""
    
    def __init__(self):
        """Initialize the Script Service."""
        self.data_loader = DataLoader()
    
    def create_script(self, card_id, agent_id=None):
        """
        Create a complete sales script for a specific card.
        
        Args:
            card_id: ID of the card
            agent_id: ID of the agent (optional, for personalization)
            
        Returns:
            Complete sales script with sections
        """
        # Load data
        cards_data = self.data_loader.load_cards_data()
        sales_data = self.data_loader.load_sales_data()
        
        if cards_data is None:
            return None
            
        # Get card details
        card_details = cards_data[cards_data['card_id'] == card_id]
        if len(card_details) == 0:
            return None
            
        card_detail = card_details.iloc[0].to_dict()
        
        # Analyze sales data for this card if available
        card_sales = None
        if sales_data is not None:
            card_sales = sales_data[sales_data['card_id'] == card_id].copy()
        
        # Get agent's sales for this card if agent_id provided
        agent_card_sales = None
        if agent_id is not None and sales_data is not None:
            agent_card_sales = sales_data[
                (sales_data['agent_id'] == agent_id) & 
                (sales_data['card_id'] == card_id)
            ].copy()
        
        # Analyze card performance and rejection reasons
        successful_sales = 0
        unsuccessful_sales = 0
        rejection_reasons = {}
        
        if card_sales is not None and len(card_sales) > 0:
            successful_sales = card_sales['success_flag'].sum()
            unsuccessful_sales = len(card_sales) - successful_sales
            
            # Extract rejection reasons
            if 'application_details' in card_sales.columns:
                for _, sale in card_sales[card_sales['success_flag'] == False].iterrows():
                    if 'application_details' in sale and isinstance(sale['application_details'], dict):
                        reason = sale['application_details'].get('rejection_reason')
                        if reason:
                            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
        
        # Create script sections
        card_name = card_detail.get('name', card_id)
        benefits = card_detail.get('benefits', []) if isinstance(card_detail.get('benefits', []), list) else []
        joining_fee = card_detail.get('joining_fee', 'N/A')
        annual_fee = card_detail.get('annual_fee', 'N/A')
        interest_rate = card_detail.get('interest_rate', 'N/A')
        eligibility = card_detail.get('eligibility', 'N/A')
        reward_rate = card_detail.get('reward_rate', 'N/A')
        
        script = {
            "card_name": card_name,
            "introduction": {
                "greeting": f"Hello, this is [Your Name] from GroMo. How are you doing today? I'd like to tell you about a fantastic credit card that might be perfect for your needs.",
                "opening": self._generate_card_introduction(card_detail),
                "transition": "May I take a few minutes to explain how this card can benefit you?"
            },
            "qualification": {
                "income": f"To ensure this card is right for you, may I ask about your approximate annual income? The minimum income requirement is {eligibility}.",
                "employment": "What type of employment are you currently in?",
                "spending": "Could you tell me a bit about your monthly spending patterns? Which categories do you spend the most on?"
            },
            "benefits_presentation": {
                "primary_benefits": [],
                "additional_benefits": [],
                "fees_and_charges": f"The card comes with a joining fee of ₹{joining_fee} and an annual fee of ₹{annual_fee}. The interest rate is {interest_rate}% should you carry a balance."
            },
            "objection_handling": {
                "common_objections": []
            },
            "closing": {
                "trial_close": "Based on what I've shared, how does this card sound for your needs?",
                "closing_options": []
            },
            "application_process": {
                "documents": "To proceed with the application, we'll need your ID proof, address proof, income proof such as salary slips or IT returns, and PAN card.",
                "timeline": "The application process is quick and straightforward. Once submitted, approval typically takes 3-7 working days, and you'll receive your card within 7-10 days after approval.",
                "support": "I'll be your point of contact throughout the application process. Feel free to reach out to me directly if you have any questions or need assistance."
            }
        }
        
        # Add benefits
        for i, benefit in enumerate(benefits):
            description = self._elaborate_benefit(benefit)
            
            if i < 3:  # Primary benefits (top 3)
                script['benefits_presentation']['primary_benefits'].append({
                    "benefit": benefit,
                    "description": description,
                    "script": f"One of the standout features of this card is {benefit}. This means {description}"
                })
            else:  # Additional benefits
                script['benefits_presentation']['additional_benefits'].append({
                    "benefit": benefit,
                    "description": description
                })
        
        # Add objection handling
        # Add common objections first
        common_objections = [
            "Annual Fee",
            "Interest Rate",
            "Already Have Too Many Cards",
            "Credit Score Concerns",
            "Income Requirements"
        ]
        
        # Add observed rejection reasons
        for reason, count in sorted(rejection_reasons.items(), key=lambda x: x[1], reverse=True):
            if reason not in common_objections:
                common_objections.append(reason)
        
        # Add objection handling scripts
        for objection in common_objections:
            script['objection_handling']['common_objections'].append({
                "objection": objection,
                "response": self._generate_objection_response(objection, card_detail)
            })
        
        # Add closing strategies
        closing_strategies = self._generate_closing_strategies(card_detail)
        script['closing']['closing_options'] = closing_strategies
        
        return script
    
    def get_objection_handling(self, card_id):
        """
        Get objection handling suggestions for a specific card.
        
        Args:
            card_id: ID of the card
            
        Returns:
            Dictionary with objection handling scripts
        """
        # Load data
        cards_data = self.data_loader.load_cards_data()
        sales_data = self.data_loader.load_sales_data()
        
        if cards_data is None:
            return None
            
        # Get card details
        card_details = cards_data[cards_data['card_id'] == card_id]
        if len(card_details) == 0:
            return None
            
        card_detail = card_details.iloc[0].to_dict()
        
        # Analyze rejection reasons if sales data is available
        rejection_reasons = {}
        if sales_data is not None:
            card_sales = sales_data[sales_data['card_id'] == card_id].copy()
            
            # Extract rejection reasons
            if 'application_details' in card_sales.columns:
                for _, sale in card_sales[card_sales['success_flag'] == False].iterrows():
                    if 'application_details' in sale and isinstance(sale['application_details'], dict):
                        reason = sale['application_details'].get('rejection_reason')
                        if reason:
                            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
        
        # Common objections
        common_objections = [
            "Annual Fee",
            "Interest Rate",
            "Already Have Too Many Cards",
            "Credit Score Concerns",
            "Income Requirements",
            "Better Offers Available",
            "Documentation Requirements",
            "Rewards Not Relevant"
        ]
        
        # Add observed rejection reasons
        for reason, count in sorted(rejection_reasons.items(), key=lambda x: x[1], reverse=True):
            if reason not in common_objections:
                common_objections.append(reason)
        
        # Generate objection handling scripts
        objections = []
        for objection in common_objections:
            objections.append({
                "objection": objection,
                "response": self._generate_objection_response(objection, card_detail),
                "frequency": rejection_reasons.get(objection, 0)
            })
        
        # Sort by frequency
        objections.sort(key=lambda x: x['frequency'], reverse=True)
        
        return {
            "card_name": card_detail.get('name', card_id),
            "objections": objections
        }
    
    def _generate_card_introduction(self, card_details):
        """Generate introduction for a card pitch."""
        card_name = card_details.get('name', "this credit card")
        card_type = "premium" if any(keyword in card_name for keyword in ["Premium", "Elite", "Platinum"]) else "standard"
        benefits = card_details.get('benefits', []) if isinstance(card_details.get('benefits', []), list) else []
        
        benefits_phrase = ""
        if benefits:
            top_benefits = benefits[:2]
            benefits_phrase = f" with excellent {' and '.join(top_benefits)}"
        
        intros = [
            f"Let me tell you about {card_name}, which offers exceptional benefits designed for your lifestyle.",
            f"{card_name} is a {card_type} card that can elevate your financial flexibility and rewards experience{benefits_phrase}.",
            f"I'd like to introduce you to {card_name}, one of our most popular options with excellent benefits that match your spending habits."
        ]
        
        return random.choice(intros)
    
    def _elaborate_benefit(self, benefit):
        """Elaborate on a specific card benefit."""
        benefit_descriptions = {
            "Lounge Access": "Complimentary access to airport lounges, making your travel experience more comfortable and relaxing.",
            "Reward Points": "Earn points on every purchase that can be redeemed for a wide range of products, services, or cashback.",
            "Cashback": "Get money back on your purchases automatically, putting cash directly back in your pocket.",
            "Air Miles": "Earn miles with every purchase that can be redeemed for flights, upgrades, or travel-related expenses.",
            "Hotel Discounts": "Enjoy special discounts at partner hotels, making your stays more affordable.",
            "Travel Insurance": "Complimentary travel insurance coverage for you and your family when you book tickets with this card.",
            "Shopping Points": "Earn extra points when shopping at partner retailers, allowing you to maximize your rewards.",
            "EMI Offers": "Convert large purchases into easy monthly installments at low or zero interest rates.",
            "Movie Tickets": "Discounted or buy-one-get-one-free offers on movie tickets at partner theaters.",
            "Fuel Surcharge Waiver": "Save on fuel surcharges at petrol pumps across the country.",
            "Roadside Assistance": "24/7 emergency roadside assistance for your vehicle when needed.",
            "Car Rental Discounts": "Special rates and offers on car rentals with partner companies.",
            "Dining Rewards": "Extra rewards or discounts when dining at partner restaurants.",
            "Grocery Cashback": "Special cashback rates on grocery purchases, helping you save on everyday essentials.",
            "Online Shopping Discounts": "Exclusive discounts and offers when shopping at partner online retailers.",
            "Golf Program": "Complimentary golf games or discounted green fees at premium golf courses.",
            "Concierge Service": "Personal assistance for bookings, recommendations, and arrangements.",
            "Airport Meet & Greet": "VIP treatment with personalized greeting and assistance at select airports.",
            "Zero Foreign Transaction Fee": "No additional charges when making purchases in foreign currencies during international travel.",
            "Global Emergency Assistance": "24/7 support for emergencies while traveling internationally.",
            "Lost Card Protection": "Quick card blocking and replacement with limited or zero liability for unauthorized transactions.",
            "Extended Warranty": "Additional warranty coverage beyond the manufacturer's warranty on eligible purchases.",
            "Purchase Protection": "Coverage against damage or theft for eligible items purchased with the card.",
            "Price Protection": "Refund of the difference if an item's price drops within a specific period after purchase.",
            "Complimentary Airport Transfers": "Free transportation to or from the airport when traveling.",
            "Priority Pass": "Access to a global network of airport lounges regardless of airline or class of travel.",
            "Hotel Status Upgrade": "Automatic status upgrade in partner hotel loyalty programs.",
            "Railway Lounge Access": "Access to premium lounges at major railway stations.",
            "Movie Ticket Offers": "Discounts or buy-one-get-one-free offers on movie tickets."
        }
        
        return benefit_descriptions.get(benefit, f"Exclusive {benefit.lower()} for cardholders.")
    
    def _generate_objection_response(self, objection, card_details):
        """Generate response to a common objection."""
        joining_fee = card_details.get('joining_fee', None)
        annual_fee = card_details.get('annual_fee', None)
        interest_rate = card_details.get('interest_rate', None)
        benefits = card_details.get('benefits', []) if isinstance(card_details.get('benefits', []), list) else []
        
        objection = objection.lower()
        
        if "fee" in objection or "expensive" in objection:
            if joining_fee == 0 or annual_fee == 0:
                return (
                    f"I understand your concern about fees. The good news is that this card has "
                    f"{joining_fee == 0 and 'no joining fee' or annual_fee == 0 and 'no annual fee'}. "
                    f"The benefits you'll receive far outweigh the costs, including "
                    f"{', '.join(benefits[:2]) if benefits else 'excellent rewards and savings opportunities'}."
                )
            else:
                return (
                    f"I understand your concern about the fees. Consider this as an investment - "
                    f"the card's benefits like {benefits[0] if benefits else 'rewards'} can save you much more than the fee annually. "
                    f"Plus, many customers qualify for fee waivers based on their spending patterns."
                )
                
        elif "interest" in objection or "rate" in objection:
            return (
                f"I understand your concern about interest rates. The good news is that if you pay your "
                f"balance in full each month, you won't pay any interest at all. Plus, this card offers "
                f"an interest-free period of up to 50 days on purchases."
            )
            
        elif "credit score" in objection or "credit history" in objection:
            return (
                "I understand your concern about credit requirements. While a good score helps, "
                "we have options for different credit profiles. Let's focus on finding the right fit for your situation, "
                "and I can guide you through ways to strengthen your application."
            )
            
        elif "income" in objection or "eligibility" in objection:
            return (
                "I understand your concern about eligibility. Let's review the requirements together - "
                "often there are alternative ways to qualify based on your overall financial profile, not just income. "
                "I can help you determine the best approach for your situation."
            )
            
        elif "documentation" in objection or "paperwork" in objection:
            return (
                "I understand paperwork can be overwhelming. The good news is that our application process is "
                "largely digital, and I'll personally help you every step of the way to make it as smooth as possible. "
                "We'll need just a few basic documents that you likely already have on hand."
            )
            
        elif "approval" in objection or "rejection" in objection:
            return (
                "I understand your concern about approval. Before we apply, I'll help assess your eligibility to "
                "maximize your chances. Even if you're not approved for this specific card, we have several "
                "alternatives that might be a better fit for your current situation."
            )
            
        elif "too many cards" in objection or "already have" in objection:
            return (
                f"I understand you already have other cards. What makes this card different is "
                f"{', '.join(benefits[:2]) if benefits else 'its unique benefits'}. Many customers find it "
                f"valuable to have different cards for different purposes - this one could complement your "
                f"existing cards by giving you advantages in specific spending categories."
            )
            
        elif "benefits" in objection or "rewards" in objection or "relevant" in objection:
            benefits_text = ", ".join(benefits[:3]) if benefits else "rewards"
            return (
                f"I understand you're looking for valuable benefits. This card offers {benefits_text} "
                f"that are specifically designed to match your lifestyle and spending patterns. "
                f"Based on your typical monthly expenses, you could earn significant value from these rewards."
            )
            
        elif "better offer" in objection or "competing" in objection:
            return (
                "I appreciate that you're comparing options - that's smart. While other offers might seem attractive, "
                "let's compare the total value proposition. When you consider the joining benefits, ongoing rewards, "
                "and the service we provide, many customers find this card offers better overall value. "
                "I'd be happy to do a side-by-side comparison with any other offer you're considering."
            )
            
        else:
            return (
                "I understand your concern. Let me address that specifically and show you how this card "
                "might still be a great fit for your needs. Many of our customers had similar questions initially "
                "but have been very satisfied with their decision."
            )
    
    def _generate_closing_strategies(self, card_details):
        """Generate effective closing strategies for the card."""
        card_name = card_details.get('name', "this credit card")
        benefits = card_details.get('benefits', []) if isinstance(card_details.get('benefits', []), list) else []
        top_benefits = ", ".join(benefits[:2]) if benefits else "excellent benefits"
        
        closings = [
            {
                "strategy": "Benefit Summary",
                "script": f"Based on what you've shared about your needs, {card_name} with {top_benefits} seems like an excellent fit. Shall we proceed with the application now?"
            },
            {
                "strategy": "Limited Time Offer",
                "script": f"Currently, we have a special promotion for this card with {benefits[0] if benefits else 'enhanced rewards'}. This offer is available for a limited time. Would you like to take advantage of it today?"
            },
            {
                "strategy": "Future Value",
                "script": f"By starting with this card today, you'll begin accumulating rewards immediately. Over the next year, based on your spending patterns, you could earn rewards worth thousands of rupees. Shall we get started so you can begin enjoying these benefits?"
            },
            {
                "strategy": "Comparison Close",
                "script": f"Compared to similar cards in the market, {card_name} offers {benefits[0] if benefits else 'superior rewards'} and {benefits[1] if len(benefits) > 1 else 'excellent service'}. This makes it one of the best options for your needs. Would you like to proceed with the application?"
            },
            {
                "strategy": "Assumptive Close",
                "script": f"Great! I'll need just a few details to complete your application for {card_name}. Could you please share your PAN card number and current residential address so we can proceed?"
            }
        ]
        
        return closings
