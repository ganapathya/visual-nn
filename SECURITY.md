# 🔒 Security Guidelines for Visual-NN

## 🚨 Critical: API Key Protection

### ✅ What's Protected

Your API keys are **automatically protected** from Git commits:

- **`.env`** files are ignored by `.gitignore`
- **`.env.*`** patterns (like `.env.local`, `.env.prod`) are ignored
- Additional patterns like `*.key`, `*_secret` are also protected

### 🔑 How to Set API Keys Safely

#### **Local Development (Mac)**

```bash
# Option 1: Environment variable (temporary)
export GEMINI_API_KEY="AIzaSy...your_key_here"
python app.py

# Option 2: .env file (persistent)
cp env.example .env
# Edit .env with your real key
nano .env
python app.py
```

#### **EC2 Deployment**

```bash
# Method 1: Environment variable
export GEMINI_API_KEY="AIzaSy...your_key_here"
echo 'export GEMINI_API_KEY="AIzaSy...your_key_here"' >> ~/.bashrc
source ~/.bashrc

# Method 2: .env file
cp env.example .env
nano .env  # Add your real key
```

#### **Systemd Service (EC2)**

```bash
# Add to your service file
sudo nano /etc/systemd/system/visual-nn.service

[Service]
Environment="GEMINI_API_KEY=AIzaSy...your_key_here"
Environment="FLASK_ENV=production"
```

## ✅ Security Verification Checklist

### Before Committing Code:

```bash
# 1. Check Git status (should NOT see .env files)
git status

# 2. Verify .env is ignored
echo "test" > .env
git status  # Should not show .env
rm .env

# 3. Search for accidental hardcoded keys
grep -r "AIzaSy" . --exclude-dir=.git
grep -r "api.*key.*=" . --exclude-dir=.git
```

### Production Deployment:

```bash
# 1. Verify environment variables
echo $GEMINI_API_KEY  # Should show your key

# 2. Test app startup
python app.py  # Should not show API key errors

# 3. Check app logs
tail -f app.log  # Should not contain API keys
```

## 🛡️ Security Best Practices

### ✅ DO:

- Use environment variables or .env files
- Keep API keys out of code
- Use different keys for dev/staging/prod
- Rotate keys periodically
- Set up API usage quotas
- Monitor API usage

### ❌ DON'T:

- Hardcode keys in source code
- Commit .env files to Git
- Share keys via email/chat
- Use production keys in development
- Ignore rate limits

## 🚨 If You Accidentally Commit an API Key

1. **Immediately revoke the key** in Google AI Studio
2. **Generate a new key**
3. **Remove from Git history:**

   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch .env' \
   --prune-empty --tag-name-filter cat -- --all

   git push origin --force --all
   ```

## 🔍 Environment Variables Used

| Variable         | Purpose           | Required | Default        |
| ---------------- | ----------------- | -------- | -------------- |
| `GEMINI_API_KEY` | Gemini AI access  | Yes      | None           |
| `FLASK_ENV`      | Flask environment | No       | development    |
| `SECRET_KEY`     | Flask sessions    | No       | auto-generated |

## 📞 Support

If you suspect a security issue:

1. DO NOT create a public GitHub issue
2. Revoke any exposed credentials immediately
3. Generate new credentials
4. Update your deployment

## 🔄 Key Rotation Schedule

- **Development**: Rotate every 6 months
- **Production**: Rotate every 3 months
- **After incidents**: Rotate immediately

---

**Remember**: The application works perfectly without API keys - it just falls back to manual mode. Security first! 🛡️
