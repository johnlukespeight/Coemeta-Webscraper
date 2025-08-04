# Security Guide for Coemeta WebScraper

## 🔒 Overview

This comprehensive security guide covers both **credential security** and **web scraping security measures** for the Coemeta WebScraper project. It addresses past security issues and provides best practices for safe operation.

---

## 🚨 Critical Security Issues & Fixes

### **Exposed Credentials (RESOLVED)**

**Issue**: Google service account credentials were exposed in the public repository.

**✅ Actions Taken**:

- ❌ Deleted `spartan-rhino-434020-h1-a244eeb7b709.json` from repository
- ✅ Enhanced `.gitignore` protection for all credential files
- ✅ Removed hardcoded paths from all source files
- ✅ Created secure configuration system with environment variables
- ✅ Added credential validation and setup helpers

### **Immediate Actions Required**

1. **🔄 Rotate Your Service Account Key**

   ```bash
   # Go to Google Cloud Console > IAM & Admin > Service Accounts
   # Delete the exposed key and create a new one
   # Update your application with new credentials
   ```

2. **📊 Monitor for Abuse**

   - Check Google Cloud Console for unusual activity
   - Review billing and usage logs
   - Set up alerts for unusual API usage

3. **🔍 Review Repository History**
   ```bash
   # Check if credentials were in git history
   git log --all --full-history -- "*.json"
   ```

---

## 🛡️ Credential Security

### **Secure Configuration Management**

#### **Environment Variables (Recommended)**

```bash
# Set environment variable
export GOOGLE_SERVICE_ACCOUNT_PATH="/path/to/your/service_account.json"

# For permanent setup (macOS/Linux)
echo 'export GOOGLE_SERVICE_ACCOUNT_PATH="/path/to/your/service_account.json"' >> ~/.zshrc
```

#### **Local File Method**

```bash
# Place service_account.json in project directory
# File is automatically protected by .gitignore
```

#### **Configuration Validation**

```python
from config import validate_credentials, get_service_account_path

# Validate credentials
if validate_credentials():
    print("✅ Credentials are secure")
else:
    print("❌ Credentials need attention")
```

### **Security Best Practices**

#### **✅ Do's**

- ✅ Use environment variables for production
- ✅ Rotate credentials regularly
- ✅ Validate JSON structure before use
- ✅ Use the setup script for configuration
- ✅ Monitor for unusual activity

#### **❌ Don'ts**

- ❌ Never commit credentials to version control
- ❌ Don't hardcode paths in source code
- ❌ Don't share credentials in public repositories
- ❌ Don't use the same credentials across projects

### **Setup Script Usage**

```bash
# Run the secure setup script
python setup.py

# This will guide you through secure credential setup
```

---

## 🤖 Web Scraping Security

### **Anti-Detection Techniques**

#### **1. Undetected Chrome Driver**

```python
# Uses undetected-chromedriver to bypass bot detection
import undetected_chromedriver as uc

driver = uc.Chrome()
driver.get("https://shopgoodwill.com")
```

#### **2. Stealth Browser Configuration**

```python
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
```

#### **3. Random User Agents**

```python
user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    # ... more realistic user agents
]
```

### **Human Behavior Simulation**

#### **Random Delays**

```python
import time
import random

# Random delays between actions
time.sleep(random.uniform(2, 5))
```

#### **Random Scrolling**

```python
# Simulate human scrolling behavior
driver.execute_script(f"window.scrollTo(0, {random.randint(100, 800)});")
```

#### **Mouse Movement Simulation**

```python
# Simulate natural mouse movements
from selenium.webdriver.common.action_chains import ActionChains

actions = ActionChains(driver)
actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50))
actions.perform()
```

### **Captcha Handling**

#### **Automatic Detection**

```python
captcha_selectors = [
    "iframe[src*='captcha']",
    "iframe[src*='recaptcha']",
    "iframe[src*='hcaptcha']",
    ".captcha",
    ".recaptcha"
]
```

#### **Manual Resolution**

```python
# When automatic solving fails
input("Please solve the captcha manually and press Enter to continue...")
```

### **Blocking Detection**

#### **Blocking Indicators**

```python
blocking_keywords = [
    "blocked", "captcha", "verify", "robot",
    "automation", "access denied", "forbidden",
    "rate limit", "too many requests"
]
```

#### **Response Strategy**

1. **Detect blocking** in page content
2. **Attempt captcha resolution**
3. **Retry with different method**
4. **Report detailed error**

---

## 🔄 Retry Logic & Fallback Methods

### **Multi-Method Approach**

```python
def scrape_with_retry(keyword, max_retries=3):
    methods = [
        "undetected_chrome",
        "regular_chrome_stealth",
        "cloudscraper"
    ]

    for attempt in range(max_retries):
        for method in methods:
            try:
                return scrape_with_method(method, keyword)
            except Exception as e:
                continue
        time.sleep(random.uniform(5, 15))

    raise Exception("All methods failed")
```

### **Exponential Backoff**

```python
# Wait longer between retries
delay = min(30, (2 ** attempt) + random.uniform(0, 1))
time.sleep(delay)
```

---

## 📊 Database Security

### **DuckDB Security Measures**

#### **Connection Safety**

```python
# Thread-safe database connections
import threading

class AuctionDatabase:
    def __init__(self):
        self._lock = threading.Lock()
        self.conn = None

    def _connect(self):
        with self._lock:
            self.conn = duckdb.connect(self.db_path, read_only=False)
```

#### **Data Protection**

```python
# Secure data insertion with validation
def insert_auction_results(self, keyword, results):
    with self._lock:
        try:
            # Validate and clean data
            # Insert with proper error handling
            # Commit transaction safely
        except Exception as e:
            self.conn.rollback()
            raise e
```

### **File System Security**

```python
# Protect database files
import os

# Ensure database files are not committed
if "*.duckdb" not in gitignore:
    gitignore.append("*.duckdb")
```

---

## 🚨 Troubleshooting

### **Common Security Issues**

#### **1. Credential Exposure**

```bash
# Check for exposed credentials
git log --all --full-history -- "*.json"

# Remove from history if found
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch spartan-rhino-434020-h1-a244eeb7b709.json' \
  --prune-empty --tag-name-filter cat -- --all
```

#### **2. Still Getting Blocked**

- ✅ Increase retry attempts
- ✅ Use longer delays between requests
- ✅ Try different user agents
- ✅ Implement proxy rotation

#### **3. Database Connection Issues**

```python
# Check database file permissions
import os
if not os.access("auction_data.duckdb", os.R_OK | os.W_OK):
    print("Database file permission issues")
```

### **Debug Mode**

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed security logging
logging.getLogger('selenium').setLevel(logging.DEBUG)
```

---

## 📈 Monitoring & Logging

### **Security Metrics**

```python
# Track security events
security_events = {
    'blocking_detected': 0,
    'captcha_encountered': 0,
    'credential_errors': 0,
    'database_errors': 0
}
```

### **Alert System**

```python
def security_alert(event_type, details):
    """Send security alerts for critical events"""
    if event_type == 'credential_exposure':
        # Immediate action required
        send_urgent_alert(details)
    elif event_type == 'blocking_detected':
        # Monitor and adjust strategy
        log_blocking_event(details)
```

---

## 🔧 Configuration Security

### **Environment Setup**

```bash
# Secure environment variables
export GOOGLE_SERVICE_ACCOUNT_PATH="/secure/path/to/credentials.json"
export DUCKDB_PATH="/secure/path/to/database.duckdb"
export LOG_LEVEL="INFO"
```

### **File Permissions**

```bash
# Secure file permissions
chmod 600 service_account.json
chmod 600 auction_data.duckdb
chmod 644 .gitignore
```

### **Network Security**

```python
# Use HTTPS for all external requests
import requests
session = requests.Session()
session.verify = True  # Verify SSL certificates
```

---

## ⚖️ Legal & Ethical Considerations

### **Terms of Service Compliance**

- ✅ Check website's robots.txt
- ✅ Respect rate limiting policies
- ✅ Follow website terms of service
- ✅ Use data responsibly

### **Data Protection**

- ✅ Follow GDPR/privacy regulations
- ✅ Respect intellectual property rights
- ✅ Implement data retention policies
- ✅ Secure data storage and transmission

### **Ethical Scraping**

- ✅ Don't overload servers
- ✅ Use data for legitimate purposes
- ✅ Respect website resources
- ✅ Implement proper attribution

---

## 🚀 Quick Security Checklist

### **Before Running**

- [ ] Credentials are secure (not in version control)
- [ ] Environment variables are set
- [ ] Database file permissions are correct
- [ ] .gitignore protects sensitive files

### **During Operation**

- [ ] Monitor for blocking/captcha
- [ ] Check for unusual activity
- [ ] Validate data integrity
- [ ] Log security events

### **After Operation**

- [ ] Review logs for issues
- [ ] Check for credential exposure
- [ ] Update security measures if needed
- [ ] Rotate credentials periodically

---

## 📞 Emergency Contacts

### **If Credentials are Exposed**

1. **Immediately rotate Google service account key**
2. **Check for unusual activity in Google Cloud Console**
3. **Review repository history for other exposures**
4. **Update all applications with new credentials**

### **If Scraping is Blocked**

1. **Check if website changed security measures**
2. **Update anti-detection techniques**
3. **Consider using different IP/proxy**
4. **Review and adjust retry logic**

---

## 📚 Additional Resources

### **Security Tools**

- [Google Cloud Security](https://cloud.google.com/security)
- [OWASP Security Guidelines](https://owasp.org/)
- [Python Security Best Practices](https://python-security.readthedocs.io/)

### **Web Scraping Ethics**

- [Scraping Ethics Guide](https://www.scrapingbee.com/blog/web-scraping-ethics/)
- [Robots.txt Specification](https://www.robotstxt.org/)

### **Legal Resources**

- [GDPR Compliance](https://gdpr.eu/)
- [Data Protection Laws](https://www.dataprotection.org/)

---

_Last Updated: August 2024_
_Version: 2.0 - Consolidated Security Guide_
