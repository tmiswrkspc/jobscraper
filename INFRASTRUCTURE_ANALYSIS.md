# Infrastructure Analysis & Scaling Plan
## Current Infrastructure → 1-2K Jobs Per Day

**Date**: March 7, 2026  
**Goal**: Scale from 8 jobs/session to 1000-2000 jobs/day

---

## 📊 Current Infrastructure

### What We Have Now

#### Hardware/Network
- **Single Machine**: Your local MacBook Pro
- **Single IP Address**: Residential ISP connection
- **Network**: Standard home/office internet
- **Browser**: Chromium via Playwright (headless capable)

#### Software Stack
- **Python 3.12.2**: ✅ Modern, stable
- **Playwright 1.40.0**: ✅ Latest browser automation
- **playwright-stealth**: ✅ Anti-detection plugins
- **Hypothesis**: ✅ Property-based testing
- **pytest**: ✅ Test framework

#### Scraper Capabilities
- **Queries**: 8 predefined searches
- **Pages per Query**: 2 (configurable to 4)
- **Delay Range**: 30-60 seconds between requests
- **Anti-Detection**: Scrolling, mouse movements, resource blocking
- **Error Handling**: CAPTCHA detection, network errors, selector validation
- **Session Management**: Checkpoints, resumability
- **Export**: JSON + CSV with UTF-8 encoding

### Current Performance Metrics

| Metric | Current Value | Bottleneck |
|--------|---------------|------------|
| Jobs per Session | 8 | IP blocking |
| Success Rate | 37.5% | CAPTCHA detection |
| Session Duration | 5-10 minutes | Delays |
| Sessions per Day | 1 | IP blocking |
| **Total Jobs/Day** | **8** | **IP + CAPTCHA** |

### Current Limitations

#### 1. Single IP Address 🚫
- **Problem**: Indeed flags and blocks after 3 queries
- **Impact**: Can only run 1 session before 12-24 hour block
- **Result**: Maximum 8 jobs per day

#### 2. CAPTCHA Blocking 🤖
- **Problem**: 62.5% of queries hit CAPTCHAs
- **Impact**: Only 3 out of 8 queries succeed
- **Result**: Massive data loss (99.6% below target)

#### 3. No Proxy Rotation 🔄
- **Problem**: All requests from same IP
- **Impact**: Easy to detect and block
- **Result**: Cannot scale beyond 1 session

#### 4. No CAPTCHA Solving 🧩
- **Problem**: Manual intervention required
- **Impact**: Automated scraping stops at CAPTCHAs
- **Result**: 62.5% of potential data lost

#### 5. Single Data Source 📍
- **Problem**: Only scraping Indeed
- **Impact**: All eggs in one basket
- **Result**: Vulnerable to single-site blocking

---

## 🎯 Target Infrastructure (1-2K Jobs/Day)

### What We Need to Build

#### Option A: Indeed-Only (High Investment)
**Target**: 1000-2000 jobs/day from Indeed alone

**Required Infrastructure**:
1. **Residential Proxy Pool**: 50-100 rotating IPs
2. **CAPTCHA Solving Service**: Automated solving
3. **Distributed Execution**: Multiple machines/containers
4. **Rate Limiting**: Smart request distribution
5. **Monitoring**: Real-time success rate tracking

**Estimated Cost**: $150-300/month

#### Option B: Multi-Site (Recommended)
**Target**: 1000-2000 jobs/day from multiple sources

**Required Infrastructure**:
1. **Multiple Scrapers**: Indeed, Naukri, Monster, LinkedIn, Glassdoor
2. **Basic Proxy Pool**: 10-20 IPs (optional for some sites)
3. **Data Aggregation**: Unified database/storage
4. **Deduplication**: Cross-site duplicate detection
5. **Scheduling**: Staggered execution across sites

**Estimated Cost**: $50-100/month (optional proxies)

---

## 🔧 Detailed Upgrade Path

### Phase 1: Quick Wins (Free - 1 Week)
**Goal**: 100-200 jobs/day without spending money

#### 1.1 Multi-Site Expansion
**Action**: Build scrapers for less-protected sites
- ✅ Naukri.com (India's #1 job site)
- ✅ Monster India (moderate protection)
- ✅ Glassdoor (reasonable rate limits)
- ✅ AngelList/Wellfound (startup jobs)

**Expected Results**:
- Naukri: 50-100 jobs/day
- Monster: 30-50 jobs/day
- Glassdoor: 20-40 jobs/day
- Indeed: 8 jobs/day (current)
- **Total: 108-198 jobs/day**

**Implementation Time**: 2-3 days per site

#### 1.2 Batch Mode Scheduling
**Action**: Spread scraping across the day
- Run Indeed: 1 query every 6 hours (4 queries/day)
- Run Naukri: 2 queries every 4 hours (12 queries/day)
- Run Monster: 2 queries every 6 hours (8 queries/day)

**Expected Results**:
- Avoid detection by spacing requests
- No IP blocking (sufficient cooldown)
- **Increase to 150-250 jobs/day**

**Implementation Time**: 1 day (cron jobs/scheduler)

#### 1.3 Network Rotation (Free)
**Action**: Use multiple networks
- Home WiFi: Morning session
- Mobile Hotspot: Afternoon session
- Coffee Shop/Library: Evening session

**Expected Results**:
- 3 different IPs per day
- 3x more sessions possible
- **Increase to 200-300 jobs/day**

**Implementation Time**: Immediate (manual)

**Phase 1 Total**: 200-300 jobs/day (20-30% of target)

---

### Phase 2: Infrastructure Investment ($50-100/month)
**Goal**: 500-800 jobs/day with basic infrastructure

#### 2.1 Residential Proxy Service
**Recommended Providers**:

| Provider | Price | IPs | Best For |
|----------|-------|-----|----------|
| **BrightData** | $500/month | Unlimited | Enterprise (overkill) |
| **Smartproxy** | $75/month | 10GB | Good balance |
| **Proxy-Cheap** | $50/month | 5GB | Budget option |
| **IPRoyal** | $40/month | 5GB | Best value |

**Recommendation**: Start with **IPRoyal** ($40/month)
- 5GB bandwidth (~5000 requests)
- Residential IPs (harder to detect)
- Rotating IPs (new IP per request)
- India-specific IPs available

**Implementation**:
```python
# Add to scraper.py
PROXY_CONFIG = {
    'server': 'http://proxy.iproyal.com:12321',
    'username': 'your_username',
    'password': 'your_password'
}

# In create_browser_profile()
context = browser.new_context(
    proxy=PROXY_CONFIG,
    locale='en-IN',
    timezone_id='Asia/Kolkata'
)
```

**Expected Results**:
- Indeed: 200-400 jobs/day (no IP blocking)
- Naukri: 100-200 jobs/day (with proxies)
- Monster: 50-100 jobs/day (with proxies)
- **Total: 350-700 jobs/day**

**Implementation Time**: 2-3 hours

#### 2.2 Basic CAPTCHA Solving (Optional)
**Recommended Providers**:

| Provider | Price | Speed | Success Rate |
|----------|-------|-------|--------------|
| **2Captcha** | $2.99/1000 | 10-30s | 90-95% |
| **Anti-Captcha** | $2.00/1000 | 5-20s | 95-98% |
| **CapSolver** | $0.80/1000 | 10-40s | 85-90% |

**Recommendation**: Start with **2Captcha** ($2.99/1000)
- Good balance of price/speed/accuracy
- Easy API integration
- Pay-as-you-go (no monthly commitment)

**Expected Usage**:
- ~100 CAPTCHAs per day
- Cost: $0.30/day = $9/month

**Implementation**:
```python
from twocaptcha import TwoCaptcha

solver = TwoCaptcha('YOUR_API_KEY')

def solve_captcha(page):
    # Get CAPTCHA site key
    site_key = page.locator('[data-sitekey]').get_attribute('data-sitekey')
    
    # Solve CAPTCHA
    result = solver.recaptcha(
        sitekey=site_key,
        url=page.url
    )
    
    # Submit solution
    page.evaluate(f"document.getElementById('g-recaptcha-response').innerHTML='{result['code']}'")
    page.click('button[type="submit"]')
```

**Expected Results**:
- Recover 62.5% of blocked queries
- Indeed: 400-600 jobs/day (with CAPTCHA solving)
- **Total: 500-800 jobs/day**

**Implementation Time**: 3-4 hours

**Phase 2 Total**: 500-800 jobs/day (50-80% of target)

---

### Phase 3: Full Production ($150-300/month)
**Goal**: 1000-2000 jobs/day with enterprise infrastructure

#### 3.1 Premium Proxy Pool
**Upgrade to**: Smartproxy or BrightData
- **Smartproxy**: $75/month for 10GB
- 10,000+ requests per day
- Sticky sessions (same IP for 10-30 minutes)
- Better success rates

**Expected Results**:
- Indeed: 600-800 jobs/day
- Naukri: 200-400 jobs/day
- Monster: 100-200 jobs/day
- Glassdoor: 100-200 jobs/day
- **Total: 1000-1600 jobs/day**

#### 3.2 CAPTCHA Solving at Scale
**Upgrade to**: Anti-Captcha
- Faster solving (5-20s vs 10-30s)
- Higher success rate (95-98%)
- Better for high volume

**Expected Usage**:
- ~300 CAPTCHAs per day
- Cost: $0.60/day = $18/month

#### 3.3 Distributed Execution
**Setup**: Multiple machines/containers
- **Option A**: AWS EC2 (t3.micro) - $10/month per instance
- **Option B**: DigitalOcean Droplets - $6/month per instance
- **Option C**: Docker containers on single VPS - $20/month

**Configuration**:
- 3-5 instances running simultaneously
- Each instance handles 1-2 sites
- Coordinated via central database

**Expected Results**:
- 5x parallel execution
- **Total: 1500-2000 jobs/day**

#### 3.4 Database & Storage
**Setup**: Centralized data storage
- **PostgreSQL**: Store all scraped jobs
- **Redis**: Cache and deduplication
- **S3/Spaces**: Backup storage

**Cost**: $10-20/month

#### 3.5 Monitoring & Alerts
**Setup**: Real-time monitoring
- **Grafana**: Visualize success rates
- **Prometheus**: Metrics collection
- **PagerDuty/Email**: Alerts for failures

**Cost**: Free (self-hosted) or $10/month (cloud)

**Phase 3 Total**: 1500-2000 jobs/day (100-200% of target)

---

## 💰 Cost Breakdown

### Budget Option ($0/month)
- Multi-site scrapers (Naukri, Monster, Glassdoor)
- Network rotation (home, mobile, public WiFi)
- Batch scheduling
- **Result**: 200-300 jobs/day

### Basic Option ($50-100/month)
- Budget proxies (IPRoyal: $40/month)
- Optional CAPTCHA solving (2Captcha: $9/month)
- Multi-site scrapers
- **Result**: 500-800 jobs/day

### Premium Option ($150-300/month)
- Premium proxies (Smartproxy: $75/month)
- CAPTCHA solving (Anti-Captcha: $18/month)
- Distributed execution (AWS: $30/month)
- Database (PostgreSQL: $15/month)
- Monitoring (Grafana: $10/month)
- **Result**: 1500-2000 jobs/day

---

## 📈 Scaling Roadmap

### Week 1: Multi-Site Foundation (Free)
**Tasks**:
- [ ] Build Naukri scraper
- [ ] Build Monster scraper
- [ ] Build Glassdoor scraper
- [ ] Setup batch scheduling
- [ ] Test network rotation

**Expected**: 200-300 jobs/day

### Week 2: Proxy Integration ($40-50)
**Tasks**:
- [ ] Sign up for IPRoyal
- [ ] Integrate proxy rotation
- [ ] Test with Indeed
- [ ] Optimize proxy usage
- [ ] Monitor success rates

**Expected**: 500-800 jobs/day

### Week 3: CAPTCHA Solving ($9-18)
**Tasks**:
- [ ] Sign up for 2Captcha
- [ ] Integrate CAPTCHA solving
- [ ] Test with Indeed
- [ ] Optimize solving speed
- [ ] Track solve rates

**Expected**: 800-1200 jobs/day

### Week 4: Optimization & Scale
**Tasks**:
- [ ] Optimize all scrapers
- [ ] Add more search queries
- [ ] Implement deduplication
- [ ] Setup monitoring
- [ ] Document processes

**Expected**: 1000-2000 jobs/day

---

## 🔍 Detailed Implementation Guide

### Step 1: Multi-Site Scrapers (Priority 1)

#### Naukri.com Scraper
**Why**: India's #1 job site, less aggressive blocking

**Differences from Indeed**:
- Different URL structure: `naukri.com/jobs-in-bangalore`
- Different selectors (need to inspect)
- Different pagination (page numbers vs start parameter)
- Less aggressive CAPTCHA

**Implementation**:
```python
# naukri_scraper.py
BASE_URL = "https://www.naukri.com"

SELECTORS = {
    'job_card': ['.jobTuple', '.srp-jobtuple-wrapper'],
    'title': ['.title', '.jobTuple-title'],
    'company': ['.companyInfo', '.comp-name'],
    'location': ['.location', '.locWdth'],
    'salary': ['.salary', '.sal-wrap'],
    'link': ['a.title', '.jobTuple-title a']
}

def construct_search_url(query, location):
    return f"{BASE_URL}/{query}-jobs-in-{location}"
```

**Expected**: 50-100 jobs/day

#### Monster India Scraper
**Why**: Large database, moderate protection

**Differences**:
- URL: `monsterindia.com/search/jobs`
- Different selectors
- AJAX-based loading (may need wait strategies)

**Expected**: 30-50 jobs/day

#### Glassdoor Scraper
**Why**: Jobs + company reviews, reasonable limits

**Differences**:
- URL: `glassdoor.co.in/Job/jobs.htm`
- Requires location parameter
- Has salary estimates

**Expected**: 20-40 jobs/day

### Step 2: Proxy Integration (Priority 2)

#### IPRoyal Setup
```python
# config.py
PROXY_ENABLED = True
PROXY_CONFIG = {
    'server': 'http://geo.iproyal.com:12321',
    'username': 'your_username',
    'password': 'your_password'
}

# For India-specific IPs
PROXY_COUNTRY = 'in'  # India
```

#### Proxy Rotation Strategy
```python
def create_browser_with_proxy(playwright_instance):
    if PROXY_ENABLED:
        proxy_url = f"{PROXY_CONFIG['server']}?country={PROXY_COUNTRY}"
        context = browser.new_context(
            proxy={
                'server': proxy_url,
                'username': PROXY_CONFIG['username'],
                'password': PROXY_CONFIG['password']
            }
        )
    else:
        context = browser.new_context()
    
    return context
```

#### Proxy Testing
```python
def test_proxy():
    """Test proxy connection and IP location"""
    page.goto('https://api.ipify.org?format=json')
    ip = page.content()
    print(f"Current IP: {ip}")
    
    page.goto('https://ipinfo.io/json')
    info = page.content()
    print(f"IP Info: {info}")
```

### Step 3: CAPTCHA Solving (Priority 3)

#### 2Captcha Integration
```python
# Install: pip install 2captcha-python
from twocaptcha import TwoCaptcha

solver = TwoCaptcha(config.CAPTCHA_API_KEY)

def solve_recaptcha(page):
    """Solve reCAPTCHA v2 on current page"""
    try:
        # Find CAPTCHA site key
        site_key = page.locator('[data-sitekey]').get_attribute('data-sitekey')
        
        if not site_key:
            return False
        
        # Solve CAPTCHA
        logger.info(f"Solving CAPTCHA for {page.url}")
        result = solver.recaptcha(
            sitekey=site_key,
            url=page.url
        )
        
        # Inject solution
        page.evaluate(f"""
            document.getElementById('g-recaptcha-response').innerHTML = '{result['code']}';
            document.getElementById('g-recaptcha-response').style.display = 'block';
        """)
        
        # Submit form
        page.click('button[type="submit"]')
        
        logger.info("CAPTCHA solved successfully")
        return True
        
    except Exception as e:
        logger.error(f"CAPTCHA solving failed: {e}")
        return False
```

#### Modified CAPTCHA Detection
```python
def detect_and_solve_captcha(page):
    """Detect CAPTCHA and attempt to solve"""
    if detect_captcha(page):
        logger.warning("CAPTCHA detected, attempting to solve...")
        
        if config.CAPTCHA_SOLVING_ENABLED:
            success = solve_recaptcha(page)
            if success:
                logger.info("CAPTCHA solved, continuing...")
                return False  # No CAPTCHA anymore
            else:
                logger.error("CAPTCHA solving failed, skipping page")
                return True  # Still has CAPTCHA
        else:
            logger.warning("CAPTCHA solving disabled, skipping page")
            return True
    
    return False
```

---

## 📊 Expected Results by Phase

### Current State
```
Infrastructure: Single IP, no proxies, no CAPTCHA solving
Sites: Indeed only
Result: 8 jobs/day
Cost: $0/month
```

### After Phase 1 (Multi-Site)
```
Infrastructure: Single IP, network rotation
Sites: Indeed, Naukri, Monster, Glassdoor
Result: 200-300 jobs/day (25x improvement)
Cost: $0/month
Time: 1 week
```

### After Phase 2 (Proxies)
```
Infrastructure: Proxy pool (10-20 IPs)
Sites: Indeed, Naukri, Monster, Glassdoor
Result: 500-800 jobs/day (62-100x improvement)
Cost: $50-100/month
Time: 2 weeks
```

### After Phase 3 (Full Production)
```
Infrastructure: Premium proxies, CAPTCHA solving, distributed
Sites: Indeed, Naukri, Monster, Glassdoor, LinkedIn
Result: 1500-2000 jobs/day (187-250x improvement)
Cost: $150-300/month
Time: 4 weeks
```

---

## 🎯 Recommended Action Plan

### Immediate (This Week)
1. **Build Naukri scraper** - Highest ROI, least blocking
2. **Setup batch scheduling** - Space out Indeed queries
3. **Test network rotation** - Use mobile hotspot

**Expected**: 100-200 jobs/day by end of week

### Short-term (Next 2 Weeks)
1. **Sign up for IPRoyal** - $40/month proxy service
2. **Integrate proxy rotation** - Add to all scrapers
3. **Build Monster scraper** - Additional data source

**Expected**: 500-800 jobs/day by end of month

### Medium-term (Next Month)
1. **Add 2Captcha** - Solve CAPTCHAs automatically
2. **Build Glassdoor scraper** - More data diversity
3. **Optimize all scrapers** - Improve success rates

**Expected**: 1000-1500 jobs/day by month 2

### Long-term (Quarter 1)
1. **Upgrade to premium proxies** - Better reliability
2. **Add distributed execution** - Scale horizontally
3. **Build monitoring dashboard** - Track performance

**Expected**: 1500-2000 jobs/day sustained

---

## 🚀 Quick Start: Get to 200 Jobs/Day (Free)

### Day 1: Naukri Scraper
```bash
# Copy Indeed scraper as template
cp scraper.py naukri_scraper.py

# Update selectors for Naukri
# Update URL construction
# Test with 1 query
python3 naukri_scraper.py
```

### Day 2: Monster Scraper
```bash
# Copy template
cp scraper.py monster_scraper.py

# Update for Monster
# Test
python3 monster_scraper.py
```

### Day 3: Batch Scheduler
```bash
# Create scheduler script
cat > run_all_scrapers.sh << 'EOF'
#!/bin/bash
python3 indeed_scraper.py &
sleep 300  # 5 minute delay
python3 naukri_scraper.py &
sleep 300
python3 monster_scraper.py &
wait
EOF

chmod +x run_all_scrapers.sh
```

### Day 4: Cron Setup
```bash
# Add to crontab
crontab -e

# Run every 6 hours
0 */6 * * * cd /path/to/scraper && ./run_all_scrapers.sh
```

**Result**: 200-300 jobs/day without spending money!

---

## 📞 Support & Next Steps

### Ready to Scale?

**Option 1: DIY (Recommended)**
- Follow this guide step-by-step
- Start with free multi-site approach
- Add proxies when ready to scale
- Total time: 2-4 weeks to 1000+ jobs/day

**Option 2: Assisted Setup**
- I can help build the additional scrapers
- Guide you through proxy integration
- Setup CAPTCHA solving
- Total time: 1-2 weeks to 1000+ jobs/day

**Option 3: Full Service**
- Build all scrapers
- Setup infrastructure
- Configure monitoring
- Deliver turnkey solution
- Total time: 1 week to 1000+ jobs/day

### Questions?
- Which phase do you want to start with?
- What's your budget for infrastructure?
- Do you want to build Naukri scraper first?
- Need help with proxy setup?

---

**Bottom Line**: You can reach 200-300 jobs/day for FREE in 1 week by building multi-site scrapers. To hit 1000-2000 jobs/day, budget $50-150/month for proxies and CAPTCHA solving.

**Next Step**: Build Naukri scraper (highest ROI, least blocking) 🚀
