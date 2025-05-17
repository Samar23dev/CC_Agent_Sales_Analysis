"""
GroMo AI Sales Coach - Metrics Utilities

This module provides utility functions for calculating performance metrics.
"""


def calculate_success_rate(successful_sales, total_sales):
    """
    Calculate the success rate for sales.
    
    Args:
        successful_sales: Number of successful sales
        total_sales: Total number of sales
        
    Returns:
        Success rate (0 to 1)
    """
    if total_sales == 0:
        return 0
    return successful_sales / total_sales


def calculate_avg_commission(total_commission, successful_sales):
    """
    Calculate the average commission per successful sale.
    
    Args:
        total_commission: Total commission earned
        successful_sales: Number of successful sales
        
    Returns:
        Average commission per successful sale
    """
    if successful_sales == 0:
        return 0
    return total_commission / successful_sales


def calculate_growth_rate(current_value, previous_value):
    """
    Calculate the growth rate between two values.
    
    Args:
        current_value: Current value
        previous_value: Previous value
        
    Returns:
        Growth rate
    """
    if previous_value == 0:
        return 0
    return (current_value - previous_value) / previous_value


def calculate_monthly_run_rate(monthly_value):
    """
    Calculate the annual run rate based on a monthly value.
    
    Args:
        monthly_value: Monthly value
        
    Returns:
        Annual run rate
    """
    return monthly_value * 12


def calculate_conversion_ratio(successful_sales, total_sales):
    """
    Calculate the conversion ratio for sales.
    
    Args:
        successful_sales: Number of successful sales
        total_sales: Total number of sales
        
    Returns:
        Conversion ratio (0 to 1)
    """
    return calculate_success_rate(successful_sales, total_sales)


def calculate_profitability_score(success_rate, avg_commission):
    """
    Calculate a profitability score based on success rate and average commission.
    
    Args:
        success_rate: Success rate (0 to 1)
        avg_commission: Average commission per successful sale
        
    Returns:
        Profitability score (0 to 1)
    """
    # Normalize commission to 0-1 range (assuming 5000 is max commission)
    norm_commission = min(1.0, avg_commission / 5000)
    
    # Calculate weighted score (60% commission, 40% success rate)
    return (norm_commission * 0.6) + (success_rate * 0.4)


def calculate_performance_index(sales_volume, success_rate, avg_commission):
    """
    Calculate a comprehensive performance index.
    
    Args:
        sales_volume: Number of sales
        success_rate: Success rate (0 to 1)
        avg_commission: Average commission per successful sale
        
    Returns:
        Performance index
    """
    # Normalize sales volume (assuming 100 is a good monthly volume)
    norm_volume = min(1.0, sales_volume / 100)
    
    # Normalize commission to 0-1 range (assuming 5000 is max commission)
    norm_commission = min(1.0, avg_commission / 5000)
    
    # Calculate weighted score
    return (norm_volume * 0.3) + (success_rate * 0.3) + (norm_commission * 0.4)


def calculate_roi(total_commission, marketing_cost):
    """
    Calculate return on investment.
    
    Args:
        total_commission: Total commission earned
        marketing_cost: Total marketing cost
        
    Returns:
        ROI (ratio)
    """
    if marketing_cost == 0:
        return 0
    return total_commission / marketing_cost - 1


def calculate_profit_margin(total_commission, total_cost):
    """
    Calculate profit margin.
    
    Args:
        total_commission: Total commission earned
        total_cost: Total cost
        
    Returns:
        Profit margin (0 to 1)
    """
    if total_commission == 0:
        return 0
    return (total_commission - total_cost) / total_commission
