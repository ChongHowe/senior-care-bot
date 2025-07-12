# Deploy Senior Care Bot

This document provides deployment instructions for different platforms.

## 🚀 Quick Deployment Options

### 1. **Heroku (Recommended for Beginners)**
```bash
# Install Heroku CLI
# Create Heroku app
heroku create senior-care-bot-app

# Set environment variables
heroku config:set BOT_TOKEN=your_bot_token_here

# Deploy
git add .
git commit -m "Deploy senior care bot"
git push heroku main
```

### 2. **Railway (Easy & Fast)**
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Set environment variable: `BOT_TOKEN=your_token`
4. Deploy automatically

### 3. **DigitalOcean App Platform**
```bash
# Create app.yaml
spec:
  name: senior-care-bot
  services:
  - name: bot
    source_dir: /
    github:
      repo: your-username/senior-care-bot
      branch: main
    run_command: python bot.py
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
    - key: BOT_TOKEN
      value: your_bot_token_here
```

### 4. **AWS Lambda (Serverless)**
- Use AWS Lambda with API Gateway
- Set up triggers for webhook mode
- Configure environment variables in Lambda

### 5. **Local Deployment**
```bash
# Clone repository
git clone your-repo-url
cd senior-care-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your bot token

# Run the bot
python bot.py
```

## 🔧 Environment Variables Required

- `BOT_TOKEN`: Your Telegram bot token from @BotFather
- `LOG_LEVEL`: INFO (or DEBUG for development)
- `MISSED_MEDICATION_WINDOW`: 30 (minutes)
- `DAILY_CHECKIN_HOURS`: 24 (hours)

## 📝 Pre-Deployment Checklist

- [ ] Bot token obtained from @BotFather
- [ ] Environment variables configured
- [ ] Requirements.txt includes all dependencies
- [ ] .gitignore excludes sensitive files
- [ ] README.md documentation complete

## 🔒 Security Notes

- Never commit bot tokens to version control
- Use environment variables for sensitive data
- Enable webhook mode for production (optional)
- Monitor logs for suspicious activity

## 📊 Monitoring & Maintenance

- Monitor bot uptime and responses
- Check family notification delivery
- Backup user data regularly
- Update dependencies periodically

## 🆘 Support

If you need help with deployment:
1. Check the logs for error messages
2. Verify environment variables are set
3. Test bot token with a simple script
4. Contact platform support if needed
