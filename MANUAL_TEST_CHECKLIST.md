# 📋 GovAI Platform - Quick Manual Test Checklist

## 🚀 Pre-Test Setup
- [ ] Backend server running on http://127.0.0.1:8085
- [ ] Frontend running on http://localhost:8501
- [ ] All dependencies installed (`pip install -r requirements.txt`)

---

## 🔍 Fraud Detection Tests

### High-Risk Contract Test
**Input:**
```json
{
  "contract_number": "HIGH-RISK-001",
  "description": "Emergency mega bridge reconstruction project",
  "amount": 50000000,
  "supplier": "Emergency Construction LLC",
  "country": "Pakistan"
}
```
**Expected:** HIGH or MEDIUM risk, Score > 0.3
- [ ] ✅ PASS - [ ] ❌ FAIL

### Low-Risk Contract Test  
**Input:**
```json
{
  "contract_number": "LOW-RISK-001", 
  "description": "Office supplies procurement",
  "amount": 100000,
  "supplier": "Local Business Supplies",
  "country": "Pakistan"
}
```
**Expected:** LOW risk, Score < 0.3
- [ ] ✅ PASS - [ ] ❌ FAIL

---

## 🤖 Chatbot Tests

### English Bill Inquiry
**Input:** "How do I check my electricity bill?"
**Expected:** Helpful response with CNIC/name request
- [ ] ✅ PASS - [ ] ❌ FAIL

### Urdu Bill Inquiry
**Input:** "بجلی کا بل کیسے چیک کریں؟"
**Expected:** Urdu response with guidance
- [ ] ✅ PASS - [ ] ❌ FAIL

### Complaint Filing
**Input:** "I want to file a complaint about broken streetlights"
**Expected:** Step-by-step complaint guidance
- [ ] ✅ PASS - [ ] ❌ FAIL

### Emergency Services
**Input:** "Emergency! Need help immediately!"
**Expected:** Emergency numbers and immediate assistance
- [ ] ✅ PASS - [ ] ❌ FAIL

### Document Request
**Input:** "How can I apply for CNIC?"
**Expected:** Document application guidance
- [ ] ✅ PASS - [ ] ❌ FAIL

### Office Information
**Input:** "What are your office hours?"
**Expected:** Office hours and contact details
- [ ] ✅ PASS - [ ] ❌ FAIL

---

## 💰 Bill Inquiry Tests

### Valid CNIC Test
**Input CNIC:** `42101-1234567-1`
**Expected:** Ahmed Ali Khan's bills displayed
- [ ] ✅ PASS - [ ] ❌ FAIL

### Another Valid CNIC
**Input CNIC:** `42201-2345678-2`
**Expected:** Fatima Sheikh's bills displayed  
- [ ] ✅ PASS - [ ] ❌ FAIL

### Invalid CNIC Test
**Input CNIC:** `99999-9999999-9`
**Expected:** "No citizen found" message
- [ ] ✅ PASS - [ ] ❌ FAIL

---

## 🎨 UI/UX Tests

### Navigation Test
- [ ] Can switch between all 6 tabs smoothly
- [ ] Sidebar navigation works properly
- [ ] Modern gradient design visible
- [ ] No broken layouts or overlapping elements

### Responsive Design Test
- [ ] Works on desktop (1920x1080)
- [ ] Works on tablet view (768px width)
- [ ] Works on mobile view (375px width)
- [ ] All buttons and inputs accessible

### Language Switching Test
- [ ] Language selector in sidebar works
- [ ] Chatbot responds in selected language
- [ ] UI elements switch appropriately

---

## ⚡ Performance Tests

### Response Time Test
- [ ] Fraud detection responds < 3 seconds
- [ ] Chatbot responds < 2 seconds  
- [ ] Bill inquiry responds < 2 seconds
- [ ] Page navigation is instant

### Load Test
- [ ] Can submit 5 fraud detection requests rapidly
- [ ] Can send 10 chat messages in succession
- [ ] System remains responsive under load

---

## 🔧 System Health Tests

### Backend Health
**URL:** http://127.0.0.1:8085/health
**Expected:** `{"status": "healthy", ...}`
- [ ] ✅ PASS - [ ] ❌ FAIL

### API Documentation
**URL:** http://127.0.0.1:8085/docs
**Expected:** Swagger documentation loads
- [ ] ✅ PASS - [ ] ❌ FAIL

### Frontend Health
**URL:** http://localhost:8501
**Expected:** Streamlit interface loads
- [ ] ✅ PASS - [ ] ❌ FAIL

---

## 🎯 Edge Case Tests

### Invalid Contract Data
**Input:** Empty contract number, negative amount
**Expected:** Graceful error handling, no crashes
- [ ] ✅ PASS - [ ] ❌ FAIL

### Empty Chat Message
**Input:** Empty string to chatbot
**Expected:** Helpful prompt or default response
- [ ] ✅ PASS - [ ] ❌ FAIL

### Very Long Message
**Input:** 1000+ character message to chatbot
**Expected:** Processes without errors
- [ ] ✅ PASS - [ ] ❌ FAIL

---

## 🏆 Hackathon Demo Scenarios

### Scenario 1: Fraud Detection Demo
1. **Setup:** Navigate to "🔍 AI Fraud Detection" tab
2. **Action:** Input emergency contract ($50M, 1-month duration)
3. **Expected:** HIGH risk detection with detailed analysis
4. **Demo Value:** Shows AI detecting suspicious patterns
- [ ] ✅ READY FOR DEMO

### Scenario 2: Multilingual Assistant Demo
1. **Setup:** Navigate to "🤖 Smart Assistant" tab
2. **Action:** Ask bill question in English, then same in Urdu
3. **Expected:** Contextual responses in both languages
4. **Demo Value:** Shows multilingual AI capability
- [ ] ✅ READY FOR DEMO

### Scenario 3: Citizen Services Demo
1. **Setup:** Navigate to "💰 Budget Transparency" tab  
2. **Action:** Search CNIC: 42101-1234567-1
3. **Expected:** Instant bill lookup with payment info
4. **Demo Value:** Shows real-time government services
- [ ] ✅ READY FOR DEMO

### Scenario 4: Analytics Dashboard Demo
1. **Setup:** Navigate to "📊 Analytics Hub" tab
2. **Action:** Show performance metrics and charts
3. **Expected:** Professional analytics with insights
4. **Demo Value:** Shows production-ready monitoring
- [ ] ✅ READY FOR DEMO

---

## 📊 Overall Assessment

### Core Functionality
- [ ] All major features working
- [ ] No critical errors
- [ ] Professional appearance
- [ ] Fast response times

### Hackathon Readiness
- [ ] Demo scenarios work flawlessly
- [ ] Impressive visual design
- [ ] Smooth navigation flow
- [ ] Error-free operation

### Competitive Advantages
- [ ] Multilingual support demonstrated
- [ ] AI performance clearly superior
- [ ] Professional government-grade UI
- [ ] Real-time processing showcased

---

## 🎉 Final Checklist

**Pre-Demo:**
- [ ] Run `python comprehensive_test_suite.py` (>90% pass rate)
- [ ] Verify all demo scenarios work
- [ ] Check UI renders correctly
- [ ] Confirm fast response times

**Demo Ready Criteria:**
- [ ] ✅ Zero critical failures
- [ ] ✅ Smooth navigation between all tabs
- [ ] ✅ Fraud detection shows HIGH risk for suspicious contracts
- [ ] ✅ Chatbot responds intelligently in both languages
- [ ] ✅ Bill lookup works instantly
- [ ] ✅ Modern, professional appearance

**🏆 HACKATHON STATUS:**
- [ ] 🎯 **CHAMPION READY** - All systems optimal
- [ ] ⚠️ **NEEDS TUNING** - Minor issues to fix
- [ ] 🔧 **NOT READY** - Major problems require attention

---

*💡 Tip: For best demo impact, start with the fraud detection of a high-value emergency contract, then show the multilingual chatbot, and finish with the real-time bill lookup!*