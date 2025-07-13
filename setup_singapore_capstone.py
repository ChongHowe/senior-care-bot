# Singapore Capstone Project Startup Script
# Run this script to set up your development environment and begin implementation

import os
import subprocess
import sys
from pathlib import Path

def print_banner():
    """Print project banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🇸🇬 SINGAPORE SENIOR CARE CAPSTONE PROJECT 🇸🇬          ║
    ║                                                              ║
    ║    Advanced AI-Powered Senior Healthcare Analytics Platform   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing Singapore Capstone Project Dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("   Please install manually: pip install -r requirements.txt")
        return False

def create_environment_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("\n🔧 Creating environment configuration file...")
        
        env_content = """# Singapore Senior Care Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
SINGAPORE_DATA_API_KEY=your_data_gov_sg_api_key_here
AWS_REGION=ap-southeast-1
ENVIRONMENT=development

# Singapore-specific settings
DEFAULT_LANGUAGE=English
TIMEZONE=Asia/Singapore
CURRENCY=SGD

# Healthcare API settings (optional)
HEALTHHUB_API_KEY=your_healthhub_api_key
MOH_DATA_ACCESS_TOKEN=your_moh_token

# Database settings
DATABASE_URL=sqlite:///singapore_senior_care.db
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ Created .env file")
        print("   ⚠️  Please update .env with your actual API keys and tokens")
        return True
    else:
        print("✅ Environment file already exists")
        return True

def setup_directory_structure():
    """Create necessary directories"""
    print("\n📁 Setting up project directory structure...")
    
    directories = [
        "data/singapore/moh_data",
        "data/singapore/singstat_data", 
        "data/singapore/processed",
        "data/singapore/raw",
        "models/singapore_models",
        "visualizations/singapore_dashboards",
        "logs",
        "tests",
        "docs/capstone"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    return True

def run_data_setup():
    """Run Singapore data setup"""
    print("\n🇸🇬 Generating Singapore health datasets...")
    
    try:
        subprocess.run([sys.executable, "singapore_data_setup.py"], check=True)
        print("✅ Singapore datasets generated successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating datasets: {e}")
        return False
    except FileNotFoundError:
        print("❌ singapore_data_setup.py not found")
        return False

def train_ml_models():
    """Train the ML models"""
    print("\n🤖 Training Singapore AI models...")
    
    try:
        subprocess.run([sys.executable, "singapore_ml_models.py"], check=True)
        print("✅ All 3 ML models trained successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error training models: {e}")
        return False
    except FileNotFoundError:
        print("❌ singapore_ml_models.py not found")
        return False

def check_singapore_registration():
    """Check Singapore data access requirements"""
    print("\n🇸🇬 Singapore Data Access Checklist:")
    print("   📋 To access real Singapore datasets, you need:")
    print("   1. Register at data.gov.sg for government open data")
    print("   2. Apply for MOH health data access (if required)")
    print("   3. Register for HealthHub developer account (optional)")
    print("   4. Set up AWS account with Singapore region access")
    print("\n   🔗 Useful links:")
    print("   • data.gov.sg - https://data.gov.sg/")
    print("   • HealthHub - https://www.healthhub.sg/")
    print("   • MOH Data - https://www.moh.gov.sg/")
    print("   • AWS Singapore - https://aws.amazon.com/singapore/")

def display_next_steps():
    """Display next steps for the user"""
    print("\n🚀 CAPSTONE PROJECT SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n📋 Next Steps (8-Day Timeline):")
    print("\n   📅 Day 1-2: Data Foundation")
    print("   • Update .env file with your API keys")
    print("   • Register for Singapore data access")
    print("   • Review generated datasets in data/singapore/")
    
    print("\n   📅 Day 3-4: Machine Learning (COMPLETED ✅)")
    print("   • 3 ML models already trained and saved")
    print("   • Check models/singapore_models/ for saved models")
    
    print("\n   📅 Day 5-6: Visualization and Analytics")
    print("   • Run: streamlit run singapore_visualizations.py")
    print("   • Customize dashboards for your presentation")
    
    print("\n   📅 Day 7: Integration and Testing")
    print("   • Test end-to-end system: python bot.py")
    print("   • Connect to real Singapore APIs")
    
    print("\n   📅 Day 8: Deployment and Presentation")
    print("   • Deploy to AWS Singapore region")
    print("   • Prepare 10-15 minute capstone presentation")
    
    print("\n🔧 Available Commands:")
    print("   • python bot.py                              # Start the senior care bot")
    print("   • streamlit run singapore_visualizations.py  # Launch dashboards")
    print("   • python singapore_data_setup.py             # Regenerate datasets")
    print("   • python singapore_ml_models.py              # Retrain ML models")
    
    print("\n📚 Documentation:")
    print("   • SINGAPORE_CAPSTONE_README.md - Complete project guide")
    print("   • singapore_capstone_guide.md   - Implementation strategy")
    print("   • README.md                     - Original bot documentation")

def main():
    """Main setup function"""
    print_banner()
    
    # Step 1: Check Python version
    if not check_python_version():
        return False
    
    # Step 2: Install dependencies
    if not install_requirements():
        print("\n⚠️  Continuing with manual dependency installation required...")
    
    # Step 3: Create environment file
    create_environment_file()
    
    # Step 4: Setup directories
    setup_directory_structure()
    
    # Step 5: Generate Singapore datasets
    print("\n" + "="*60)
    user_input = input("🇸🇬 Generate Singapore datasets now? (y/n): ").lower().strip()
    if user_input in ['y', 'yes']:
        run_data_setup()
        
        # Step 6: Train ML models
        user_input = input("\n🤖 Train ML models now? (y/n): ").lower().strip()
        if user_input in ['y', 'yes']:
            train_ml_models()
    
    # Step 7: Show Singapore data requirements
    check_singapore_registration()
    
    # Step 8: Display next steps
    display_next_steps()
    
    print(f"\n🎉 Singapore Senior Care Capstone Project is ready!")
    print(f"💡 Start with: python bot.py (to test the bot)")
    print(f"📊 Or launch dashboards: streamlit run singapore_visualizations.py")
    
    return True

if __name__ == "__main__":
    main()
