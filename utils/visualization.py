"""
GroMo AI Sales Coach - Visualization Utilities

This module provides utility functions for data visualization.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def create_monthly_trend_chart(monthly_df):
    """
    Create a chart showing monthly sales and commission trends.
    
    Args:
        monthly_df: DataFrame with monthly performance data
        
    Returns:
        Matplotlib figure object
    """
    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("viridis")
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Ensure data is sorted by date
    if 'date' in monthly_df.columns:
        monthly_df = monthly_df.sort_values('date')
    elif 'month_year' in monthly_df.columns:
        monthly_df['date'] = pd.to_datetime(monthly_df['month_year'] + '-01')
        monthly_df = monthly_df.sort_values('date')
    
    # Get x-axis labels
    if 'month_year' in monthly_df.columns:
        x_labels = monthly_df['month_year']
    else:
        x_labels = range(len(monthly_df))
    
    # Plot sales trend
    ax1.plot(x_labels, monthly_df['total_sales'], marker='o', linewidth=2, label='Total Applications')
    ax1.plot(x_labels, monthly_df['successful_sales'], marker='s', linewidth=2, label='Approved Applications')
    ax1.set_title('Monthly Sales Volume')
    ax1.set_ylabel('Number of Applications')
    ax1.legend()
    ax1.grid(True)
    
    # Add annotations for last point
    last_idx = len(monthly_df) - 1
    ax1.annotate(f"{monthly_df['total_sales'].iloc[last_idx]}", 
                xy=(last_idx, monthly_df['total_sales'].iloc[last_idx]),
                xytext=(5, 5), textcoords='offset points')
    ax1.annotate(f"{monthly_df['successful_sales'].iloc[last_idx]}", 
                xy=(last_idx, monthly_df['successful_sales'].iloc[last_idx]),
                xytext=(5, 5), textcoords='offset points')
    
    # Plot commission trend
    ax2.bar(x_labels, monthly_df['commission'], color='purple')
    ax2.set_title('Monthly Commission')
    ax2.set_ylabel('Commission (₹)')
    ax2.grid(True, axis='y')
    
    # Add annotations for last point
    ax2.annotate(f"₹{monthly_df['commission'].iloc[last_idx]:,.0f}", 
                xy=(last_idx, monthly_df['commission'].iloc[last_idx]),
                xytext=(0, 5), textcoords='offset points', ha='center')
    
    # Rotate x-axis labels if they are strings
    if 'month_year' in monthly_df.columns:
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    return fig


def create_card_performance_chart(card_df):
    """
    Create a chart showing card performance metrics.
    
    Args:
        card_df: DataFrame with card performance data
        
    Returns:
        Matplotlib figure object
    """
    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("viridis")
    
    # Sort by total commission
    card_df = card_df.sort_values('commission', ascending=False)
    
    # Limit to top 10 cards if there are more
    if len(card_df) > 10:
        card_df = card_df.head(10)
    
    # Get card names or IDs
    if 'name' in card_df.columns:
        labels = card_df['name']
    else:
        labels = card_df['card_id']
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot total commission by card
    bars1 = ax1.barh(labels, card_df['commission'], color='teal')
    ax1.set_title('Total Commission by Card')
    ax1.set_xlabel('Total Commission (₹)')
    ax1.grid(True, axis='x')
    
    # Add value labels
    for bar in bars1:
        width = bar.get_width()
        ax1.text(width + 100, bar.get_y() + bar.get_height()/2, 
                f'₹{width:,.0f}', va='center')
    
    # Plot success rate by card
    bars2 = ax2.barh(labels, card_df['success_rate'], color='orange')
    ax2.set_title('Success Rate by Card')
    ax2.set_xlabel('Success Rate')
    ax2.set_xlim(0, 1)
    ax2.grid(True, axis='x')
    
    # Add percentage labels
    for bar in bars2:
        width = bar.get_width()
        ax2.text(width + 0.03, bar.get_y() + bar.get_height()/2, 
                f'{width:.1%}', va='center')
    
    plt.tight_layout()
    return fig


def create_segment_performance_chart(segment_df, segment_col='income_segment'):
    """
    Create a chart showing performance by customer segment.
    
    Args:
        segment_df: DataFrame with segment performance data
        segment_col: Column name for the segment
        
    Returns:
        Matplotlib figure object
    """
    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("viridis")
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Sort data if applicable
    if segment_col == 'income_segment':
        segment_order = ['Low', 'Medium', 'High', 'Very High']
        segment_df['order'] = segment_df[segment_col].apply(
            lambda x: segment_order.index(x) if x in segment_order else -1
        )
        segment_df = segment_df.sort_values('order')
    
    # Plot success rate by segment
    bars1 = ax1.bar(segment_df[segment_col], segment_df['success_rate'], color='blue')
    ax1.set_title(f'Success Rate by {segment_col.replace("_", " ").title()}')
    ax1.set_ylabel('Success Rate')
    ax1.set_ylim(0, 1)
    ax1.grid(True, axis='y')
    
    # Add percentage labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height + 0.03,
                f'{height:.1%}', ha='center')
    
    # Plot average commission by segment
    bars2 = ax2.bar(segment_df[segment_col], segment_df['avg_commission'], color='green')
    ax2.set_title(f'Avg. Commission by {segment_col.replace("_", " ").title()}')
    ax2.set_ylabel('Average Commission (₹)')
    ax2.grid(True, axis='y')
    
    # Add value labels
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height + 100,
                f'₹{height:,.0f}', ha='center')
    
    plt.tight_layout()
    return fig


def create_forecast_chart(historical_df, forecast_df):
    """
    Create a chart showing historical data and forecast.
    
    Args:
        historical_df: DataFrame with historical performance data
        forecast_df: DataFrame with forecast data
        
    Returns:
        Matplotlib figure object
    """
    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("viridis")
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Prepare X labels
    hist_labels = historical_df['month_year'] if 'month_year' in historical_df.columns else range(len(historical_df))
    forecast_labels = forecast_df['month'] if 'month' in forecast_df.columns else range(len(historical_df), len(historical_df) + len(forecast_df))
    
    # Plot sales trend
    ax1.plot(hist_labels, historical_df['total_sales'], marker='o', linewidth=2, label='Historical Applications')
    ax1.plot(range(len(historical_df) - 1, len(historical_df) + len(forecast_df)), 
             [historical_df['total_sales'].iloc[-1]] + forecast_df['total_sales'].tolist(), 
             marker='s', linewidth=2, color='red', label='Forecast Applications')
    
    # Add vertical line separating historical and forecast
    ax1.axvline(x=len(historical_df) - 0.5, color='black', linestyle='--')
    ax1.text(len(historical_df) - 0.5, ax1.get_ylim()[1] * 0.9, 'Forecast', ha='center', va='top')
    
    ax1.set_title('Sales Volume: Historical and Forecast')
    ax1.set_ylabel('Number of Applications')
    ax1.legend()
    ax1.grid(True)
    
    # Plot commission trend
    ax2.plot(hist_labels, historical_df['commission'], marker='o', linewidth=2, label='Historical Commission')
    ax2.plot(range(len(historical_df) - 1, len(historical_df) + len(forecast_df)), 
             [historical_df['commission'].iloc[-1]] + forecast_df['commission'].tolist(), 
             marker='s', linewidth=2, color='red', label='Forecast Commission')
    
    # Add vertical line separating historical and forecast
    ax2.axvline(x=len(historical_df) - 0.5, color='black', linestyle='--')
    
    # Plot cumulative commission
    ax2.plot(range(len(historical_df), len(historical_df) + len(forecast_df)), 
             forecast_df['cumulative_commission'], 
             marker='d', linewidth=2, color='green', label='Cumulative Forecast Commission')
    
    ax2.set_title('Commission: Historical and Forecast')
    ax2.set_ylabel('Commission (₹)')
    ax2.legend()
    ax2.grid(True)
    
    # Format x-axis labels
    all_labels = list(hist_labels) + list(forecast_labels)
    plt.xticks(range(len(all_labels)), all_labels, rotation=45)
    
    plt.tight_layout()
    return fig


def create_probability_gauge(probability, size=(4, 4)):
    """
    Create a gauge chart showing a probability.
    
    Args:
        probability: Probability value (0 to 1)
        size: Figure size (width, height)
        
    Returns:
        Matplotlib figure object
    """
    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Create figure
    fig, ax = plt.subplots(figsize=size, subplot_kw={'projection': 'polar'})
    
    # Define gauge parameters
    theta = np.linspace(0, 180, 100) * np.pi / 180  # 0 to 180 degrees
    r = 1.0  # radius
    
    # Define color zones (red, yellow, green)
    red_end = 40  # 0-40 degrees (low probability)
    yellow_end = 140  # 40-140 degrees (medium probability)
    # 140-180 degrees (high probability)
    
    # Map probability to angle (0 to 180 degrees)
    needle_angle = probability * 180
    
    # Draw gauge background
    ax.fill_between(theta[:red_end], 0, r, color='red', alpha=0.3)
    ax.fill_between(theta[red_end:yellow_end], 0, r, color='yellow', alpha=0.3)
    ax.fill_between(theta[yellow_end:], 0, r, color='green', alpha=0.3)
    
    # Draw needle
    needle_theta = needle_angle * np.pi / 180
    ax.plot([0, needle_theta], [0, 0.8], color='black', linewidth=3)
    ax.scatter(needle_theta, 0.8, color='black', s=100)
    
    # Add probability text
    ax.text(0, -0.2, f"{probability:.1%}", fontsize=18, ha='center', weight='bold')
    
    # Customize gauge
    ax.set_theta_zero_location('N')  # Adjust orientation 
    ax.set_theta_direction(-1)  # Clockwise
    ax.set_thetagrids([])  # Hide angle labels
    ax.set_rgrids([])  # Hide radius labels
    ax.spines['polar'].set_visible(False)  # Hide circular border
    ax.set_ylim(0, 1.2)  # Set radius limit
    
    plt.tight_layout()
    return fig


def create_comparison_chart(cards_data, metric_name, metric_values):
    """
    Create a comparison chart for multiple cards.
    
    Args:
        cards_data: List of card dictionaries with names
        metric_name: Name of the metric to compare
        metric_values: List of values for each card
        
    Returns:
        Matplotlib figure object
    """
    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("viridis")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get card names
    card_names = [card.get('name', card.get('card_id', f'Card {i}')) for i, card in enumerate(cards_data)]
    
    # Create horizontal bar chart
    bars = ax.barh(card_names, metric_values)
    
    # Color bars based on values (higher is better)
    min_val = min(metric_values)
    max_val = max(metric_values)
    norm = plt.Normalize(min_val, max_val)
    colors = plt.cm.viridis(norm(metric_values))
    
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # Add value labels
    for i, v in enumerate(metric_values):
        ax.text(v + (max_val - min_val) * 0.02, i, f"{v:,.2f}", va='center')
    
    # Set labels and title
    ax.set_title(f'Card Comparison by {metric_name}')
    ax.set_xlabel(metric_name)
    
    plt.tight_layout()
    return fig
