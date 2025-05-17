"""
GroMo AI Sales Coach - Card Service

This module provides services for analyzing card performance,
recommending cards to agents, and comparing different cards.
"""

import pandas as pd
import numpy as np

from data.data_loader import DataLoader
from utils.metrics import calculate_success_rate, calculate_avg_commission


class CardService:
    """Service for card-related operations."""
    
    def __init__(self):
        """Initialize the Card Service."""
        self.data_loader = DataLoader()
    
    def analyze_all_cards(self):
        """
        Analyze performance metrics for all cards.
        
        Returns:
            List of cards with performance metrics
        """
        # Load data
        sales_data = self.data_loader.load_sales_data()
        cards_data = self.data_loader.load_cards_data()
        
        if sales_data is None or cards_data is None:
            return None
        
        # Calculate card performance metrics
        card_metrics = sales_data.groupby('card_id').agg({
            'sale_id': 'count',
            'success_flag': 'sum',
            'commission': 'sum'
        }).reset_index()
        
        card_metrics = card_metrics.rename(columns={
            'sale_id': 'total_applications',
            'success_flag': 'successful_sales'
        })
        
        # Calculate derived metrics
        card_metrics['approval_rate'] = card_metrics.apply(
            lambda row: calculate_success_rate(row['successful_sales'], row['total_applications']),
            axis=1
        )
        
        card_metrics['avg_commission'] = card_metrics.apply(
            lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
            axis=1
        )
        
        # Add card details
        result = card_metrics.merge(cards_data, on='card_id', how='left')
        
        # Sort by total commission
        result = result.sort_values('commission', ascending=False)
        
        return result.to_dict('records')
    
    def recommend_cards(self, agent_id, limit=5):
        """
        Recommend cards for a specific agent based on their performance.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended cards with explanations
        """
        # Load data
        sales_data = self.data_loader.load_sales_data()
        cards_data = self.data_loader.load_cards_data()
        
        if sales_data is None or cards_data is None:
            return None
        
        # Get agent's sales
        agent_sales = sales_data[sales_data['agent_id'] == agent_id].copy()
        
        # If agent has no sales, recommend based on overall performance
        if len(agent_sales) == 0:
            return self._recommend_for_new_agent(limit)
        
        # Analyze agent's sales patterns
        agent_card_performance = agent_sales.groupby('card_id').agg({
            'sale_id': 'count',
            'success_flag': 'sum',
            'commission': 'sum'
        }).reset_index()
        
        agent_card_performance = agent_card_performance.rename(columns={
            'sale_id': 'total_sales',
            'success_flag': 'successful_sales'
        })
        
        agent_card_performance['success_rate'] = agent_card_performance.apply(
            lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
            axis=1
        )
        
        agent_card_performance['avg_commission'] = agent_card_performance.apply(
            lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
            axis=1
        )
        
        # Calculate overall card performance
        card_performance = sales_data.groupby('card_id').agg({
            'sale_id': 'count',
            'success_flag': 'sum',
            'commission': 'sum'
        }).reset_index()
        
        card_performance = card_performance.rename(columns={
            'sale_id': 'total_sales',
            'success_flag': 'successful_sales'
        })
        
        card_performance['success_rate'] = card_performance.apply(
            lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
            axis=1
        )
        
        card_performance['avg_commission'] = card_performance.apply(
            lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
            axis=1
        )
        
        # Add card details
        card_performance = card_performance.merge(cards_data, on='card_id', how='left')
        
        # Identify agent's strengths
        if 'customer_income' in agent_sales.columns:
            # Create income segments
            agent_sales['income_segment'] = pd.cut(
                agent_sales['customer_income'],
                bins=[0, 300000, 600000, 1000000, float('inf')],
                labels=['Low', 'Medium', 'High', 'Very High']
            )
            
            # Calculate success rate by income segment
            segment_success = agent_sales.groupby('income_segment').agg({
                'success_flag': ['count', 'mean']
            })
            
            segment_success.columns = ['count', 'success_rate']
            segment_success = segment_success.reset_index()
            
            # Get best income segments (min 3 sales, success rate > 50%)
            best_segments = segment_success[
                (segment_success['count'] >= 3) &
                (segment_success['success_rate'] > 0.5)
            ].sort_values('success_rate', ascending=False)
            
            best_segment_list = best_segments['income_segment'].tolist() if len(best_segments) > 0 else []
        else:
            best_segment_list = []
        
        # Agent's best employment types
        if 'customer_employment' in agent_sales.columns:
            employment_success = agent_sales.groupby('customer_employment').agg({
                'success_flag': ['count', 'mean']
            })
            
            employment_success.columns = ['count', 'success_rate']
            employment_success = employment_success.reset_index()
            
            # Get best employment types (min 3 sales, success rate > 50%)
            best_employment = employment_success[
                (employment_success['count'] >= 3) &
                (employment_success['success_rate'] > 0.5)
            ].sort_values('success_rate', ascending=False)
            
            best_employment_list = best_employment['customer_employment'].tolist() if len(best_employment) > 0 else []
        else:
            best_employment_list = []
        
        # Calculate card fit score based on agent's strengths
        card_performance['fit_score'] = self._calculate_card_fit_score(
            card_performance,
            agent_card_performance,
            best_segment_list,
            best_employment_list
        )
        
        # Sort by fit score and get top recommendations
        recommendations = card_performance.sort_values('fit_score', ascending=False).head(limit)
        
        # Format recommendations with explanations
        result = []
        for _, card in recommendations.iterrows():
            # Generate explanation for this recommendation
            explanation = self._generate_card_recommendation_explanation(
                card,
                agent_card_performance,
                best_segment_list,
                best_employment_list
            )
            
            result.append({
                'card_id': card['card_id'],
                'name': card['name'],
                'success_rate': card['success_rate'],
                'avg_commission': card['avg_commission'],
                'total_sales': card['total_sales'],
                'benefits': card.get('benefits', []),
                'fit_score': card['fit_score'],
                'explanation': explanation
            })
        
        return result
    
    def compare_cards(self, card_ids):
        """
        Compare multiple cards based on their performance and features.
        
        Args:
            card_ids: List of card IDs to compare
            
        Returns:
            Dictionary with comparison data
        """
        # Load data
        sales_data = self.data_loader.load_sales_data()
        cards_data = self.data_loader.load_cards_data()
        
        if cards_data is None:
            return None
        
        # Filter cards data to include only the specified cards
        comparison_cards = cards_data[cards_data['card_id'].isin(card_ids)].copy()
        
        if len(comparison_cards) == 0:
            return None
        
        # Get performance metrics if sales data is available
        if sales_data is not None:
            card_performance = sales_data.groupby('card_id').agg({
                'sale_id': 'count',
                'success_flag': 'sum',
                'commission': 'sum'
            }).reset_index()
            
            card_performance = card_performance.rename(columns={
                'sale_id': 'total_sales',
                'success_flag': 'successful_sales'
            })
            
            card_performance['success_rate'] = card_performance.apply(
                lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
                axis=1
            )
            
            card_performance['avg_commission'] = card_performance.apply(
                lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
                axis=1
            )
            
            # Merge with comparison cards
            comparison_cards = comparison_cards.merge(
                card_performance[card_performance['card_id'].isin(card_ids)],
                on='card_id',
                how='left'
            )
            
            # Fill NaN values with 0
            for col in ['total_sales', 'successful_sales', 'success_rate', 'commission', 'avg_commission']:
                if col in comparison_cards.columns:
                    comparison_cards[col] = comparison_cards[col].fillna(0)
        
        # Extract common features for comparison
        features = []
        
        # Basic card details
        features.append({
            'category': 'Basic Details',
            'features': [
                {'name': 'Card Name', 'values': comparison_cards['name'].tolist()},
                {'name': 'Joining Fee', 'values': comparison_cards['joining_fee'].tolist() if 'joining_fee' in comparison_cards.columns else []},
                {'name': 'Annual Fee', 'values': comparison_cards['annual_fee'].tolist() if 'annual_fee' in comparison_cards.columns else []},
                {'name': 'Interest Rate', 'values': comparison_cards['interest_rate'].tolist() if 'interest_rate' in comparison_cards.columns else []}
            ]
        })
        
        # Benefits
        if 'benefits' in comparison_cards.columns:
            # Create a set of all unique benefits across all cards
            all_benefits = set()
            for benefits_list in comparison_cards['benefits']:
                if isinstance(benefits_list, list):
                    all_benefits.update(benefits_list)
            
            # Create a feature row for each benefit
            benefit_features = []
            for benefit in sorted(all_benefits):
                values = []
                for benefits_list in comparison_cards['benefits']:
                    if isinstance(benefits_list, list) and benefit in benefits_list:
                        values.append('Yes')
                    else:
                        values.append('No')
                        
                benefit_features.append({'name': benefit, 'values': values})
                
            features.append({
                'category': 'Benefits',
                'features': benefit_features
            })
            
        # Eligibility
        features.append({
            'category': 'Eligibility',
            'features': [
                {'name': 'Income Requirement', 'values': comparison_cards['eligibility'].tolist() if 'eligibility' in comparison_cards.columns else []}
            ]
        })
        
        # Rewards
        features.append({
            'category': 'Rewards',
            'features': [
                {'name': 'Reward Rate', 'values': comparison_cards['reward_rate'].tolist() if 'reward_rate' in comparison_cards.columns else []},
                {'name': 'Credit Limit Range', 'values': comparison_cards['credit_limit_range'].tolist() if 'credit_limit_range' in comparison_cards.columns else []}
            ]
        })
        
        # Sales Performance
        if sales_data is not None:
            features.append({
                'category': 'Sales Performance',
                'features': [
                    {'name': 'Total Applications', 'values': comparison_cards['total_sales'].tolist() if 'total_sales' in comparison_cards.columns else []},
                    {'name': 'Success Rate', 'values': [f"{rate:.1%}" for rate in comparison_cards['success_rate'].tolist()] if 'success_rate' in comparison_cards.columns else []},
                    {'name': 'Average Commission', 'values': [f"₹{comm:.0f}" for comm in comparison_cards['avg_commission'].tolist()] if 'avg_commission' in comparison_cards.columns else []}
                ]
            })
            
        # Compile comparison data
        comparison = {
            'cards': comparison_cards['name'].tolist() if 'name' in comparison_cards.columns else comparison_cards['card_id'].tolist(),
            'card_ids': comparison_cards['card_id'].tolist(),
            'features': features
        }
        
        return comparison
    
    def _recommend_for_new_agent(self, limit=5):
        """
        Recommend cards for a new agent with no sales history.
        
        Args:
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended cards with explanations
        """
        # Load data
        sales_data = self.data_loader.load_sales_data()
        cards_data = self.data_loader.load_cards_data()
        
        if sales_data is None or cards_data is None:
            return None
            
        # Calculate card performance
        card_performance = sales_data.groupby('card_id').agg({
            'sale_id': 'count',
            'success_flag': 'sum',
            'commission': 'sum'
        }).reset_index()
        
        card_performance = card_performance.rename(columns={
            'sale_id': 'total_sales',
            'success_flag': 'successful_sales'
        })
        
        card_performance['success_rate'] = card_performance.apply(
            lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
            axis=1
        )
        
        card_performance['avg_commission'] = card_performance.apply(
            lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
            axis=1
        )
        
        # Add card details
        card_performance = card_performance.merge(cards_data, on='card_id', how='left')
        
        # Calculate a score based on success rate and commission
        # For new agents, we prioritize cards with high success rates
        card_performance['beginner_score'] = (
            card_performance['success_rate'] * 0.7 + 
            (card_performance['avg_commission'] / card_performance['avg_commission'].max()) * 0.3
        )
        
        # Sort by beginner score and get top cards
        top_cards = card_performance.sort_values('beginner_score', ascending=False).head(limit)
        
        # Format recommendations with explanations
        result = []
        for _, card in top_cards.iterrows():
            result.append({
                'card_id': card['card_id'],
                'name': card['name'],
                'success_rate': card['success_rate'],
                'avg_commission': card['avg_commission'],
                'total_sales': card['total_sales'],
                'benefits': card.get('benefits', []),
                'fit_score': card['beginner_score'],
                'explanation': f"This card has a high approval rate of {card['success_rate']:.1%} and generates an average commission of ₹{card['avg_commission']:.0f}, making it an excellent choice for new partners to build confidence and experience."
            })
            
        return result
    
    def _calculate_card_fit_score(self, card_performance, agent_card_performance, best_segments, best_employment_types):
        """
        Calculate a fit score for each card based on agent's strengths.
        
        Args:
            card_performance: DataFrame with overall card performance
            agent_card_performance: DataFrame with agent's card performance
            best_segments: List of agent's best performing income segments
            best_employment_types: List of agent's best performing employment types
            
        Returns:
            Series with fit scores for each card
        """
        # Initialize the score with base metrics
        # Higher success rate and commission are better
        card_performance['base_score'] = (
            card_performance['success_rate'] * 0.4 + 
            (card_performance['avg_commission'] / card_performance['avg_commission'].max()) * 0.6
        )
        
        # Give bonus for cards the agent already sells well
        if len(agent_card_performance) > 0:
            # Create a lookup for agent's performance
            agent_success_dict = dict(zip(agent_card_performance['card_id'], agent_card_performance['success_rate']))
            agent_comm_dict = dict(zip(agent_card_performance['card_id'], agent_card_performance['avg_commission']))
            
            # Calculate agent performance bonus
            def calc_agent_bonus(row):
                card_id = row['card_id']
                if card_id in agent_success_dict:
                    agent_success = agent_success_dict[card_id]
                    agent_comm = agent_comm_dict[card_id]
                    
                    # If agent is doing well with this card, give a bonus
                    if agent_success > 0.5 and agent_comm > 0:
                        return 0.2
                    # If agent is doing poorly with this card, penalize
                    elif agent_success < 0.3 and len(agent_card_performance) > 2:
                        return -0.1
                return 0
                
            card_performance['agent_bonus'] = card_performance.apply(calc_agent_bonus, axis=1)
        else:
            card_performance['agent_bonus'] = 0
        
        # Calculate fit score
        card_performance['fit_score'] = card_performance['base_score'] + card_performance['agent_bonus']
        
        # Normalize to 0-1 range
        min_score = card_performance['fit_score'].min()
        max_score = card_performance['fit_score'].max()
        if max_score > min_score:
            card_performance['fit_score'] = (card_performance['fit_score'] - min_score) / (max_score - min_score)
        
        return card_performance['fit_score']
    
    def _generate_card_recommendation_explanation(self, card, agent_card_performance, best_segments, best_employment_types):
        """
        Generate an explanation for a card recommendation.
        
        Args:
            card: Card data
            agent_card_performance: DataFrame with agent's card performance
            best_segments: List of agent's best performing income segments
            best_employment_types: List of agent's best performing employment types
            
        Returns:
            Explanation string
        """
        card_id = card['card_id']
        card_name = card['name']
        success_rate = card['success_rate']
        avg_commission = card['avg_commission']
        
        # Check if agent is already selling this card
        agent_experience = None
        if len(agent_card_performance) > 0:
            agent_card = agent_card_performance[agent_card_performance['card_id'] == card_id]
            if len(agent_card) > 0:
                agent_success = agent_card['success_rate'].iloc[0]
                agent_commission = agent_card['avg_commission'].iloc[0]
                agent_experience = {
                    'success_rate': agent_success,
                    'avg_commission': agent_commission
                }
        
        # Generate explanation based on card's metrics and agent's experience
        explanation_parts = []
        
        # Basic performance explanation
        explanation_parts.append(
            f"{card_name} has an approval rate of {success_rate:.1%} and generates an average commission of ₹{avg_commission:.0f} per successful sale."
        )
        
        # Agent's experience with this card
        if agent_experience:
            if agent_experience['success_rate'] >= 0.5:
                explanation_parts.append(
                    f"You've had success with this card, achieving a {agent_experience['success_rate']:.1%} approval rate."
                )
            elif agent_experience['success_rate'] < 0.3:
                explanation_parts.append(
                    f"While you've sold this card before, your approval rate of {agent_experience['success_rate']:.1%} suggests you might need to better qualify customers."
                )
            else:
                explanation_parts.append(
                    f"You have some experience with this card, with a {agent_experience['success_rate']:.1%} approval rate."
                )
        
        # Suggestion based on card details
        if 'joining_fee' in card and 'annual_fee' in card:
            joining_fee = card['joining_fee']
            annual_fee = card['annual_fee']
            
            if joining_fee == 0 and annual_fee == 0:
                explanation_parts.append(
                    "This card has no joining or annual fee, making it easy to pitch to price-sensitive customers."
                )
            elif joining_fee == 0:
                explanation_parts.append(
                    "With no joining fee, this card has a lower barrier to entry for new customers."
                )
        
        # Benefits highlight
        if 'benefits' in card and isinstance(card['benefits'], list) and len(card['benefits']) > 0:
            top_benefits = card['benefits'][:2]
            explanation_parts.append(
                f"Highlight its key benefits like {' and '.join(top_benefits)} when pitching to customers."
            )
        
        return " ".join(explanation_parts)
