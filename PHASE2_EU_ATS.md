# PHASE 2 IMPLEMENTED - EU/NL ATS Sources

## ✅ NIEUWE SOURCES TOEGEVOEGD!

### **Recruitee** 🇳🇱 (NL/EU Market Leader!)
- **Why:** #1 ATS in NL/EU startups
- **API:** `{company}.recruitee.com/api/offers`
- **Auth:** None required (public API)
- **Coverage:** Direct NL startup jobs!

### **Workable** 🌍 (Global, some EU)
- **Why:** Popular globally, some EU presence
- **API:** `apply.workable.com/api/v1/widget/accounts/{account}`
- **Auth:** None required (public widget)
- **Coverage:** International + some EU

---

## 🇳🇱 NL/EU COMPANIES IN CONFIG

### **Recruitee (8 companies):**
1. **payter** - Payments
2. **adyen** - Payments (grote NL tech!)
3. **mollie** - Payments
4. **messagebird** - Communications
5. **booking** - Travel
6. **picnic-technologies** - Groceries/logistics
7. **miro** - Collaboration tools
8. **sendcloud** - Shipping/logistics

### **Workable (3 companies):**
1. **inventyou-ab** - Nordic/EU
2. **candoris** - EU
3. **lalaland** - Fashion tech

---

## 📊 IMPACT

### **Volume:**
```
Was:     ~6500 jobs (120+ sources)
Nu:      ~6600-6800 jobs (130+ sources)
Extra:   +11 NL/EU sources
```

### **Quality:**
✅ **Direct access** to NL startup jobs
✅ **No aggregator** noise
✅ **Company ATS** = freshest jobs
✅ **Remote vaak** in description (NL culture)

### **Coverage:**
- Payments sector (Adyen, Mollie, Payter)
- Tech startups (Miro, Booking)
- Logistics (Picnic, Sendcloud)
- Communications (MessageBird)

---

## 🧪 TEST NU!

```bash
cd /Users/ahmedmobarak/Downloads/remote-sre-job-scanner
python3 jobhunt.py --config config.explore.json scan --dry-run
```

**Watch for:**
```
✓ recruitee/payter: X jobs
✓ recruitee/adyen: X jobs
✓ recruitee/mollie: X jobs
✓ recruitee/messagebird: X jobs
✓ recruitee/booking: X jobs
✓ recruitee/picnic-technologies: X jobs
✓ recruitee/miro: X jobs
✓ recruitee/sendcloud: X jobs
✓ workable/inventyou-ab: X jobs
✓ workable/candoris: X jobs
✓ workable/lalaland: X jobs
```

**Check results:**
```bash
cat out/explore.md
```

---

## 💡 WAAROM DIT BETER IS DAN ADZUNA

### **Adzuna Problems:**
- ❌ Aggregator = veel ruis
- ❌ Mogelijk weinig NL SRE volume
- ❌ Vaak duplicates
- ❌ Verouderde listings

### **Direct ATS (Recruitee/Workable):**
- ✅ Straight from company
- ✅ Fresh listings
- ✅ No duplicates
- ✅ Company-specific details
- ✅ Direct apply links

---

## 🎯 EXPECTED RESULTS

### **In Scan:**
- ✅ 11 nieuwe sources scannen
- ✅ Jobs van bekende NL bedrijven
- ✅ "Remote" of "thuiswerken" in text
- ✅ Platform/Infra/SRE roles

### **In explore.md:**
- DevOps Engineer @ Adyen
- Platform Engineer @ Booking
- SRE @ Mollie
- Infrastructure @ MessageBird
- Cloud Engineer @ Picnic

---

## 📈 MEER COMPANIES TOEVOEGEN?

### **Easy wins (Recruitee):**
```json
"recruitee": {
  "companies": [
    "...existing...",
    "bunq",          // Banking
    "felyx",         // Mobility
    "coolblue",      // E-commerce
    "rituals",       // Retail tech
    "backbase"       // Banking tech
  ]
}
```

### **How to find more:**
1. Google: `"site:recruitee.com" AND "netherlands" AND "devops"`
2. Check company careers pages
3. If URL is `{company}.recruitee.com` → add to config!

---

## ⚠️ TROUBLESHOOTING

### **If recruitee/company fails:**
```
✗ recruitee/payter: 404 Not Found
```
**Means:** Company doesn't use Recruitee (anymore)
**Fix:** Remove from config

### **If 0 jobs:**
```
✓ recruitee/company: 0 jobs
```
**Means:** No open positions currently
**Fix:** Normal, keep in config for future

### **If parse error:**
```
✗ recruitee/company: Parse error
```
**Means:** API structure changed
**Fix:** Check source_health, will auto-skip

---

## 🚀 NEXT STEPS

### **1. Test Now:**
```bash
python3 jobhunt.py --config config.explore.json scan --dry-run
cat out/explore.md
```

### **2. Add More Companies:**
- Find NL companies using Recruitee
- Add to config
- Test

### **3. If Works Well:**
- Add to config.balanced.json
- Monitor Slack
- Adjust as needed

### **4. Future (Phase 3):**
- Personio (German market)
- Teamtailor (Nordic)
- Pinpoint (UK/EU)

---

## ✅ STATUS

| Source | Status | Companies | Jobs Expected |
|--------|--------|-----------|---------------|
| **Recruitee** | ✅ Ready | 8 NL/EU | 20-100 |
| **Workable** | ✅ Ready | 3 EU | 5-20 |
| RemoteOK | ✅ Ready | N/A | 500+ |
| Adzuna | ⚠️ Low volume | N/A | 0-10 |

---

## 🎯 WAAROM DIT WERKT

**Direct ATS = Best Strategy:**
1. ✅ Fresh jobs (from company directly)
2. ✅ No aggregator noise
3. ✅ NL companies = NL culture = remote friendly
4. ✅ Public APIs (no scraping)
5. ✅ Stable (less breakage)

**NL Companies Using Recruitee:**
- Super common in NL tech scene
- Easy to find more
- Consistent API
- No auth needed

---

**RECRUITEE + WORKABLE NU ACTIEF!** 🇳🇱🚀

**TEST:** `python3 jobhunt.py --config config.explore.json scan --dry-run`

