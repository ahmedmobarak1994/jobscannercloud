# Adzuna Setup - Find Your APP_ID

## ✅ YOU HAVE THE API KEY!

**API KEY:** `d8f65cb6ece4e2f3bb8c5ff1b6b09cf1`

## ❓ MAAR WE MISSEN DE APP_ID

Adzuna requires **BOTH**:
1. ✅ `ADZUNA_APP_KEY` (you have this!)
2. ❓ `ADZUNA_APP_ID` (we need this!)

---

## 🔍 HOW TO FIND YOUR APP_ID

### **Option 1: Check Developer Dashboard**

1. Go to: https://developer.adzuna.com/
2. Log in with your account
3. Go to "Dashboard" or "My Applications"
4. You should see:
   ```
   Application Name: [Your App Name]
   App ID: [YOUR_APP_ID]        ← THIS IS WHAT WE NEED!
   App Key: d8f65cb6...          ← You already gave this
   ```

### **Option 2: Check Signup Email**

When you signed up, Adzuna sent you an email with:
- Your APP_ID
- Your APP_KEY

Search your email for "Adzuna" or "developer.adzuna.com"

### **Option 3: It Might Be in the API Key Format**

Sometimes the APP_ID looks like:
- A number (e.g., `12345`)
- Or a short string (e.g., `abcd1234`)

---

## 🚀 ONCE YOU HAVE THE APP_ID:

### **Add to .env:**
```bash
echo 'ADZUNA_APP_ID=your_app_id_here' >> .env
echo 'ADZUNA_APP_KEY=d8f65cb6ece4e2f3bb8c5ff1b6b09cf1' >> .env
```

### **Test Adzuna:**
```bash
python3 test_search_engines.py
```

### **Add to GitHub Secrets:**
```
Repository → Settings → Secrets → Actions
+ New secret: ADZUNA_APP_ID = your_app_id
+ New secret: ADZUNA_APP_KEY = d8f65cb6ece4e2f3bb8c5ff1b6b09cf1
```

---

## 🧪 IN THE MEANTIME: TEST REMOTEOK!

RemoteOK doesn't need credentials:

```bash
python3 jobhunt.py --config config.explore.json scan --dry-run
```

You should see:
```
✓ remoteok/all: 500+ jobs
```

This will prove the search engine integration works!

---

## 📝 WHAT TO DO NOW:

1. ✅ Find your ADZUNA_APP_ID (dashboard or email)
2. ✅ Add both to .env
3. ✅ Test: `python3 test_search_engines.py`
4. ✅ Test full scan with RemoteOK: `python3 jobhunt.py --config config.explore.json scan --dry-run`
5. ✅ Check results in `out/explore.md`

---

## ⚡ QUICK TEST (RemoteOK only - works now!)

```bash
cd /Users/ahmedmobarak/Downloads/remote-sre-job-scanner
python3 jobhunt.py --config config.explore.json scan --dry-run
```

**Watch for:**
- `✓ remoteok/all: X jobs`
- `Jobs passed: X` (should be more than usual!)
- Check `out/explore.md` for results

**IF THIS WORKS:** ✅ Search engines are working!

**THEN ADD ADZUNA:** Once you find the APP_ID!

---

## 🎯 STATUS:

- ✅ RemoteOK: Ready to test (no credentials)
- ⏳ Adzuna: Need APP_ID (you have the KEY)

**TEST REMOTEOK NOW!** 🚀

