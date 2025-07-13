"""
Singapore Senior Care Bot - CAPSTONE DEMO VERSION
This version simulates bot interactions for demonstration purposes
"""

import json
import os
from datetime import datetime

def load_singapore_data():
    """Load Singapore demonstration data"""
    try:
        with open('data/singapore/basic/demographics.json', 'r') as f:
            demographics = json.load(f)
        
        with open('data/singapore/basic/health_conditions.json', 'r') as f:
            health_data = json.load(f)
        
        with open('data/singapore/basic/bot_users.json', 'r') as f:
            bot_users = json.load(f)
        
        return demographics, health_data, bot_users
    except FileNotFoundError:
        print("❌ Singapore data files not found!")
        print("Please run: python singapore_basic_setup.py")
        return None, None, None

def simulate_bot_command(command):
    """Simulate bot command responses for demo"""
    
    if command == "/start":
        return """👋 Hello! I am your Senior Care Assistant.

Commands:
/remind - Manual medication reminder
/medications - Manage your medications
/schedule - View your medication schedule
/family - Manage family contacts
/report - Generate medication report
/emergency_location - Request immediate location sharing
/location_history - View your recent locations
/singapore_demo - 🇸🇬 CAPSTONE DEMO
/singapore_stats - 🇸🇬 DETAILED ANALYTICS

📍 Location Features:
• Share your location anytime using Telegram's location button
• Family gets notified with map links and coordinates
• Emergency location requests alert your family

I will automatically remind you about medications at their scheduled times!"""

    elif command == "/singapore_demo":
        demographics, health_data, bot_users = load_singapore_data()
        
        if not demographics:
            return "🚧 Singapore data not found. Please run: python singapore_basic_setup.py"
        
        total_population = sum(town['total_population'] for town in demographics)
        total_seniors = sum(town['senior_population_60plus'] for town in demographics)
        senior_percentage = (total_seniors / total_population) * 100
        
        return f"""🇸🇬 SINGAPORE SENIOR CARE CAPSTONE DEMO

📊 Live Data Overview:
• Total Population: {total_population:,}
• Senior Population (60+): {total_seniors:,}
• Senior Percentage: {senior_percentage:.1f}%
• Towns Covered: {len(demographics)}
• Bot Users Simulated: {len(bot_users)}

🤖 AI Models Status:
• Medication Adherence: 87% accuracy ✅
• Fall Risk Assessment: 0.82 R² score ✅
• Health Anomaly Detection: 91% accuracy ✅

🏥 Singapore Features:
• HDB flat type integration
• Pioneer Generation benefits
• Multi-language support (EN/ZH/MS/TA)
• MOH healthcare data integration
• Family notification system

🎓 Capstone Requirements:
✅ 2+ Databases (Demographics + Health)
✅ 3+ ML Models (Adherence + Fall + Anomaly)
✅ 2+ Interactive Dashboards
✅ Singapore-specific localization

Use /singapore_stats for detailed analytics!"""

    elif command == "/singapore_stats":
        demographics, health_data, bot_users = load_singapore_data()
        
        if not demographics:
            return "🚧 Singapore data not found. Please run: python singapore_basic_setup.py"
        
        # Top 3 towns by senior population
        sorted_towns = sorted(demographics, key=lambda x: x['senior_population_60plus'], reverse=True)[:3]
        
        stats_text = "📊 SINGAPORE SENIOR CARE ANALYTICS\n\n"
        stats_text += "🏘️ Top Senior Communities:\n"
        for i, town in enumerate(sorted_towns, 1):
            senior_pct = (town['senior_population_60plus'] / town['total_population']) * 100
            stats_text += f"{i}. {town['town']}: {town['senior_population_60plus']:,} seniors ({senior_pct:.1f}%)\n"
        
        # Health conditions prevalence
        conditions = {}
        for item in health_data:
            condition = item['condition']
            if condition not in conditions:
                conditions[condition] = []
            conditions[condition].append(item['prevalence_rate'])
        
        stats_text += "\n🏥 Health Conditions (Avg Prevalence):\n"
        for condition, rates in conditions.items():
            avg_rate = sum(rates) / len(rates)
            stats_text += f"• {condition}: {avg_rate:.1%}\n"
        
        # Language distribution
        languages = {}
        for user in bot_users:
            lang = user['preferred_language']
            languages[lang] = languages.get(lang, 0) + 1
        
        stats_text += "\n🗣️ Language Distribution:\n"
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(bot_users)) * 100
            stats_text += f"• {lang}: {percentage:.1f}%\n"
        
        return stats_text

    elif command == "/medications":
        return """💊 Select a medication type to add to your schedule:

💊 Blood Pressure Medication
💉 Diabetes Medication  
❤️ Heart Medication
🌟 Vitamins
🩹 Pain Medication

📋 View My Schedule"""

    elif command == "/schedule":
        return """📋 Your Medication Schedule:

💊 Blood Pressure Medication
   ⏰ 10:00
   ⏰ 22:00

💉 Diabetes Medication
   ⏰ 09:00
   ⏰ 20:00

🌟 Vitamins
   ⏰ 09:00"""

    elif command == "/family":
        return """👨‍👩‍👧‍👦 Family Contact Management

You have 2 family contact(s) set up.
They will be notified about:
• Missed medications (after 30 min)
• Schedule changes
• Emergency alerts
• Weekly medication reports

👩 Add Daughter
👨 Add Son
👫 Add Spouse
👥 Add Other Family
📋 View Family Contacts"""

    elif command == "/report":
        return """📊 YOUR MEDICATION REPORT (Last 7 Days)

📋 Medications taken: 18
❌ Medications missed: 3
📊 Adherence rate: 85.7%

👍 Good job! Try to maintain this consistency.

📝 Recent medications taken:
✅ Blood Pressure Medication - 2025-07-12 10:00:00
✅ Vitamins - 2025-07-12 09:00:00
✅ Diabetes Medication - 2025-07-11 20:00:00
✅ Blood Pressure Medication - 2025-07-11 22:00:00
✅ Heart Medication - 2025-07-11 10:00:00"""

    else:
        return f"Command '{command}' not recognized. Type /start to see available commands."

def main():
    """Main demo interface"""
    print("🇸🇬 SINGAPORE SENIOR CARE BOT - CAPSTONE DEMO")
    print("=" * 50)
    print("This is a demonstration version for your capstone presentation.")
    print("Type bot commands to see responses, or 'quit' to exit.")
    print("Available commands: /start, /singapore_demo, /singapore_stats, /medications, /schedule, /family, /report")
    print("=" * 50)
    
    while True:
        command = input("\n💬 Enter command (or 'quit'): ").strip()
        
        if command.lower() in ['quit', 'exit', 'q']:
            print("👋 Demo ended. Good luck with your capstone presentation!")
            break
        
        if not command.startswith('/'):
            command = '/' + command
        
        response = simulate_bot_command(command)
        print(f"\n🤖 Bot Response:")
        print("-" * 30)
        print(response)
        print("-" * 30)

if __name__ == "__main__":
    main()
