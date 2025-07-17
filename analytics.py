"""
analytics.py

This module contains data analysis and statistics functions for the Singapore Senior Care Bot project.
Import and use these functions in bot.py or reporting.py as needed.
"""

def calculate_senior_statistics(demographics, bot_users):
    """Example: Calculate senior population stats."""
    total_population = sum(town['total_population'] for town in demographics)
    total_seniors = sum(town['senior_population_60plus'] for town in demographics)
    senior_percentage = (total_seniors / total_population) * 100 if total_population else 0
    return {
        'total_population': total_population,
        'total_seniors': total_seniors,
        'senior_percentage': senior_percentage,
        'num_towns': len(demographics),
        'num_bot_users': len(bot_users)
    }

# Add more analytics functions as needed
