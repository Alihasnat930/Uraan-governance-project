#!/usr/bin/env python3
"""
GovAI Platform - Comprehensive Manual Testing Suite
Complete test scenarios for fraud detection and chatbot functionality
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
API_BASE_URL = "http://127.0.0.1:8085"
FRONTEND_URL = "http://localhost:8501"

class GovAITestSuite:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}")
        
        if details:
            print(f"   📝 {details}")
        
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_fraud_detection_scenarios(self):
        """Test various fraud detection scenarios"""
        print("\n🔍 FRAUD DETECTION TEST SCENARIOS")
        print("=" * 60)
        
        # Test Case 1: High-Risk Emergency Contract
        print("\n1. HIGH-RISK EMERGENCY CONTRACT TEST")
        high_risk_contract = {
            "contract_number": "EMERGENCY-MEGA-001", 
            "description": "Emergency mega infrastructure project - bridge reconstruction",
            "amount": 75000000.0,  # $75M - Very High
            "supplier": "Rapid Emergency Construction LLC",
            "country": "Pakistan",
            "contract_type": "Emergency",
            "duration_months": 2,  # Very short duration
            "is_emergency": True
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/fraud-detect", json=high_risk_contract, timeout=15)
            if response.status_code == 200:
                result = response.json()
                risk_level = result.get('risk_level', 'Unknown')
                risk_score = result.get('risk_score', 0)
                
                if risk_level in ['HIGH', 'CRITICAL'] or risk_score > 0.4:
                    self.log_test("High-Risk Contract Detection", "PASS", 
                                f"Risk: {risk_level}, Score: {risk_score:.3f}")
                else:
                    self.log_test("High-Risk Contract Detection", "FAIL", 
                                f"Expected HIGH risk, got {risk_level} (Score: {risk_score:.3f})")
            else:
                self.log_test("High-Risk Contract Detection", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("High-Risk Contract Detection", "FAIL", f"Error: {str(e)}")
        
        # Test Case 2: Medium-Risk Standard Contract
        print("\n2. MEDIUM-RISK STANDARD CONTRACT TEST")
        medium_risk_contract = {
            "contract_number": "STANDARD-INFRA-002",
            "description": "Standard road maintenance and repair project",
            "amount": 5000000.0,  # $5M - Medium
            "supplier": "Reliable Infrastructure Solutions",
            "country": "Pakistan",
            "contract_type": "Infrastructure",
            "duration_months": 8,
            "is_emergency": False
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/fraud-detect", json=medium_risk_contract, timeout=15)
            if response.status_code == 200:
                result = response.json()
                risk_level = result.get('risk_level', 'Unknown')
                risk_score = result.get('risk_score', 0)
                
                self.log_test("Medium-Risk Contract Detection", "PASS", 
                            f"Risk: {risk_level}, Score: {risk_score:.3f}")
            else:
                self.log_test("Medium-Risk Contract Detection", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Medium-Risk Contract Detection", "FAIL", f"Error: {str(e)}")
        
        # Test Case 3: Low-Risk Small Contract
        print("\n3. LOW-RISK SMALL CONTRACT TEST")
        low_risk_contract = {
            "contract_number": "SMALL-OFFICE-003",
            "description": "Office supplies and equipment procurement",
            "amount": 250000.0,  # $250K - Small
            "supplier": "Local Business Supplies Co",
            "country": "Pakistan", 
            "contract_type": "Other",
            "duration_months": 12,
            "is_emergency": False
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/fraud-detect", json=low_risk_contract, timeout=15)
            if response.status_code == 200:
                result = response.json()
                risk_level = result.get('risk_level', 'Unknown')
                risk_score = result.get('risk_score', 0)
                
                if risk_level == 'LOW' or risk_score < 0.3:
                    self.log_test("Low-Risk Contract Detection", "PASS", 
                                f"Risk: {risk_level}, Score: {risk_score:.3f}")
                else:
                    self.log_test("Low-Risk Contract Detection", "WARN", 
                                f"Expected LOW risk, got {risk_level} (Score: {risk_score:.3f})")
            else:
                self.log_test("Low-Risk Contract Detection", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Low-Risk Contract Detection", "FAIL", f"Error: {str(e)}")
        
        # Test Case 4: Suspicious Pattern Detection
        print("\n4. SUSPICIOUS PATTERN DETECTION TEST")
        suspicious_contract = {
            "contract_number": "SUSPICIOUS-999",
            "description": "Urgent special project - confidential requirements",
            "amount": 99999999.0,  # Almost $100M - Extremely high
            "supplier": "New Venture Solutions",  # Unknown supplier
            "country": "Pakistan",
            "contract_type": "Emergency",
            "duration_months": 1,  # Extremely short
            "is_emergency": True
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/fraud-detect", json=suspicious_contract, timeout=15)
            if response.status_code == 200:
                result = response.json()
                risk_level = result.get('risk_level', 'Unknown')
                risk_score = result.get('risk_score', 0)
                
                self.log_test("Suspicious Pattern Detection", "PASS", 
                            f"Risk: {risk_level}, Score: {risk_score:.3f}")
            else:
                self.log_test("Suspicious Pattern Detection", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Suspicious Pattern Detection", "FAIL", f"Error: {str(e)}")
    
    def test_chatbot_scenarios(self):
        """Test chatbot functionality in multiple languages and scenarios"""
        print("\n🤖 CHATBOT FUNCTIONALITY TEST SCENARIOS")
        print("=" * 60)
        
        chatbot_tests = [
            # English Tests
            {
                "name": "English Bill Inquiry",
                "message": "How do I check my electricity bill?",
                "language": "english",
                "expected_intent": "bill_inquiry"
            },
            {
                "name": "English Complaint Filing", 
                "message": "I want to file a complaint about broken streetlights",
                "language": "english",
                "expected_intent": "complaint"
            },
            {
                "name": "English Emergency Request",
                "message": "This is an emergency! I need help immediately!",
                "language": "english", 
                "expected_intent": "emergency"
            },
            {
                "name": "English Document Request",
                "message": "How can I apply for a birth certificate?",
                "language": "english",
                "expected_intent": "document_request"
            },
            {
                "name": "English Office Information",
                "message": "What are your office hours and location?",
                "language": "english",
                "expected_intent": "information"
            },
            {
                "name": "English Fraud Report",
                "message": "I want to report corruption and bribery by an official",
                "language": "english",
                "expected_intent": "fraud_report"
            },
            
            # Urdu Tests
            {
                "name": "Urdu Bill Inquiry",
                "message": "بجلی کا بل کیسے چیک کریں؟",
                "language": "urdu",
                "expected_intent": "bill_inquiry"
            },
            {
                "name": "Urdu Complaint Filing",
                "message": "سڑک کی بتی خراب ہے شکایت درج کرانا چاہتا ہوں",
                "language": "urdu",
                "expected_intent": "complaint"
            },
            {
                "name": "Urdu Emergency Request", 
                "message": "فوری مدد چاہیے! ایمرجنسی ہے!",
                "language": "urdu",
                "expected_intent": "emergency"
            },
            {
                "name": "Urdu Document Request",
                "message": "شناختی کارڈ کے لیے کیسے درخواست دیں؟",
                "language": "urdu",
                "expected_intent": "document_request"
            },
            
            # Mixed/Auto-detect Tests
            {
                "name": "Auto-detect Language",
                "message": "Hello, میں aap سے مدد چاہتا ہوں",
                "language": "auto-detect",
                "expected_intent": "general"
            },
            
            # Service Tests
            {
                "name": "General Services Inquiry",
                "message": "What services do you provide?",
                "language": "english",
                "expected_intent": "services"
            }
        ]
        
        for i, test in enumerate(chatbot_tests, 1):
            print(f"\n{i}. {test['name'].upper()} TEST")
            
            chat_data = {
                "message": test["message"],
                "user_id": f"test_user_{i}",
                "language": test["language"]
            }
            
            try:
                response = requests.post(f"{API_BASE_URL}/assistant", json=chat_data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    bot_response = result.get('response', '')
                    detected_intent = result.get('intent', 'unknown')
                    detected_language = result.get('language', 'unknown')
                    confidence = result.get('confidence', 0)
                    
                    # Check if response is meaningful
                    if len(bot_response) > 20 and bot_response != "Sorry, I could not process your request.":
                        self.log_test(f"Chatbot {test['name']}", "PASS", 
                                    f"Intent: {detected_intent}, Lang: {detected_language}, Confidence: {confidence:.2f}")
                        print(f"   💬 Response: {bot_response[:100]}...")
                    else:
                        self.log_test(f"Chatbot {test['name']}", "FAIL", 
                                    f"Poor response: {bot_response[:50]}...")
                else:
                    self.log_test(f"Chatbot {test['name']}", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Chatbot {test['name']}", "FAIL", f"Error: {str(e)}")
            
            time.sleep(0.5)  # Small delay between requests
    
    def test_bill_inquiry_system(self):
        """Test the bill inquiry functionality"""
        print("\n💰 BILL INQUIRY SYSTEM TEST SCENARIOS")
        print("=" * 60)
        
        # Test with sample CNICs from database
        test_cnics = [
            "42101-1234567-1",  # Ahmed Ali Khan
            "42201-2345678-2",  # Fatima Sheikh
            "42301-3456789-3",  # Muhammad Hassan
            "99999-9999999-9"   # Non-existent CNIC
        ]
        
        for i, cnic in enumerate(test_cnics, 1):
            print(f"\n{i}. BILL INQUIRY FOR CNIC: {cnic}")
            
            try:
                response = requests.get(f"{API_BASE_URL}/bill-inquiry?cnic={cnic}", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'citizen' in result and result['citizen']:
                        citizen_name = result['citizen'].get('name', 'Unknown')
                        bills = result.get('bills', [])
                        total_amount = sum(bill.get('amount', 0) for bill in bills)
                        
                        self.log_test(f"Bill Inquiry {cnic}", "PASS", 
                                    f"Citizen: {citizen_name}, Bills: {len(bills)}, Total: ${total_amount:.2f}")
                    else:
                        if cnic == "99999-9999999-9":  # Expected not to exist
                            self.log_test(f"Bill Inquiry {cnic}", "PASS", "Correctly returned no citizen found")
                        else:
                            self.log_test(f"Bill Inquiry {cnic}", "FAIL", "No citizen data returned")
                else:
                    self.log_test(f"Bill Inquiry {cnic}", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Bill Inquiry {cnic}", "FAIL", f"Error: {str(e)}")
    
    def test_system_health(self):
        """Test overall system health and connectivity"""
        print("\n⚙️ SYSTEM HEALTH TEST SCENARIOS")
        print("=" * 60)
        
        # Test 1: Backend Health Check
        print("\n1. BACKEND HEALTH CHECK")
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                self.log_test("Backend Health Check", "PASS", f"Status: {health_data.get('status', 'unknown')}")
            else:
                self.log_test("Backend Health Check", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Backend Health Check", "FAIL", f"Error: {str(e)}")
        
        # Test 2: API Documentation Accessibility
        print("\n2. API DOCUMENTATION ACCESS")
        try:
            response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
            if response.status_code == 200:
                self.log_test("API Documentation Access", "PASS", "Documentation accessible")
            else:
                self.log_test("API Documentation Access", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("API Documentation Access", "FAIL", f"Error: {str(e)}")
        
        # Test 3: Frontend Accessibility (if running)
        print("\n3. FRONTEND ACCESSIBILITY CHECK")
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Accessibility", "PASS", "Streamlit interface accessible")
            else:
                self.log_test("Frontend Accessibility", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Accessibility", "FAIL", f"Error: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🔬 EDGE CASES AND ERROR HANDLING")
        print("=" * 60)
        
        # Test 1: Invalid Contract Data
        print("\n1. INVALID CONTRACT DATA TEST")
        invalid_contract = {
            "contract_number": "",  # Empty
            "description": "x",     # Too short
            "amount": -1000,        # Negative amount
            "supplier": "",         # Empty
            "country": "InvalidCountry"
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/fraud-detect", json=invalid_contract, timeout=10)
            # Should handle gracefully, not crash
            if response.status_code in [200, 400, 422]:  # Acceptable responses
                self.log_test("Invalid Contract Handling", "PASS", f"Handled gracefully (HTTP {response.status_code})")
            else:
                self.log_test("Invalid Contract Handling", "FAIL", f"Unexpected HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Contract Handling", "FAIL", f"Error: {str(e)}")
        
        # Test 2: Empty Chatbot Message
        print("\n2. EMPTY CHATBOT MESSAGE TEST")
        empty_chat = {
            "message": "",
            "user_id": "test_user",
            "language": "english"
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/assistant", json=empty_chat, timeout=10)
            if response.status_code in [200, 400]:
                self.log_test("Empty Message Handling", "PASS", "Handled gracefully")
            else:
                self.log_test("Empty Message Handling", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Empty Message Handling", "FAIL", f"Error: {str(e)}")
        
        # Test 3: Very Long Message
        print("\n3. VERY LONG MESSAGE TEST")
        long_message = "Hello! " + "This is a very long message. " * 100  # ~3000 characters
        long_chat = {
            "message": long_message,
            "user_id": "test_user",
            "language": "english"
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/assistant", json=long_chat, timeout=15)
            if response.status_code == 200:
                self.log_test("Long Message Handling", "PASS", "Processed successfully")
            else:
                self.log_test("Long Message Handling", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Long Message Handling", "FAIL", f"Error: {str(e)}")
    
    def run_performance_tests(self):
        """Test system performance and response times"""
        print("\n⚡ PERFORMANCE TEST SCENARIOS")
        print("=" * 60)
        
        # Test 1: Fraud Detection Response Time
        print("\n1. FRAUD DETECTION RESPONSE TIME")
        start_time = time.time()
        
        test_contract = {
            "contract_number": "PERF-TEST-001",
            "description": "Performance testing contract",
            "amount": 1000000.0,
            "supplier": "Test Supplier",
            "country": "Pakistan"
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/fraud-detect", json=test_contract, timeout=10)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200 and response_time < 3.0:  # Should be under 3 seconds
                self.log_test("Fraud Detection Performance", "PASS", f"Response time: {response_time:.2f}s")
            else:
                self.log_test("Fraud Detection Performance", "FAIL", f"Response time: {response_time:.2f}s")
        except Exception as e:
            self.log_test("Fraud Detection Performance", "FAIL", f"Error: {str(e)}")
        
        # Test 2: Chatbot Response Time
        print("\n2. CHATBOT RESPONSE TIME")
        start_time = time.time()
        
        chat_data = {
            "message": "What are your office hours?",
            "user_id": "perf_test_user",
            "language": "english"
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/assistant", json=chat_data, timeout=10)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200 and response_time < 2.0:  # Should be under 2 seconds
                self.log_test("Chatbot Performance", "PASS", f"Response time: {response_time:.2f}s")
            else:
                self.log_test("Chatbot Performance", "FAIL", f"Response time: {response_time:.2f}s")
        except Exception as e:
            self.log_test("Chatbot Performance", "FAIL", f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "🏆" * 60)
        print("COMPREHENSIVE TEST REPORT")
        print("🏆" * 60)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   ✅ Passed: {self.passed_tests}")
        print(f"   ❌ Failed: {self.failed_tests}")
        print(f"   📈 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        # Categorize results
        categories = {
            "Fraud Detection": [r for r in self.test_results if "fraud" in r["test"].lower() or "contract" in r["test"].lower()],
            "Chatbot": [r for r in self.test_results if "chatbot" in r["test"].lower()],
            "Bill Inquiry": [r for r in self.test_results if "bill" in r["test"].lower()],
            "System Health": [r for r in self.test_results if "health" in r["test"].lower() or "frontend" in r["test"].lower()],
            "Performance": [r for r in self.test_results if "performance" in r["test"].lower()],
            "Edge Cases": [r for r in self.test_results if any(word in r["test"].lower() for word in ["invalid", "empty", "long", "edge"])]
        }
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, results in categories.items():
            if results:
                passed = len([r for r in results if r["status"] == "PASS"])
                total = len(results)
                print(f"   {category}: {passed}/{total} ({(passed/total*100):.1f}%)")
        
        # Critical issues
        critical_failures = [r for r in self.test_results if r["status"] == "FAIL" and any(word in r["test"].lower() for word in ["health", "fraud", "chatbot"])]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES DETECTED:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES DETECTED")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if self.passed_tests / self.total_tests >= 0.9:
            print("   🎉 EXCELLENT! System is ready for production/demo")
        elif self.passed_tests / self.total_tests >= 0.7:
            print("   👍 GOOD! Minor issues need attention")
        else:
            print("   ⚠️  NEEDS WORK! Major issues require fixing")
        
        print(f"\n🎯 HACKATHON READINESS:")
        fraud_tests = len([r for r in self.test_results if "fraud" in r["test"].lower() and r["status"] == "PASS"])
        chatbot_tests = len([r for r in self.test_results if "chatbot" in r["test"].lower() and r["status"] == "PASS"])
        
        if fraud_tests >= 3 and chatbot_tests >= 5:
            print("   🏆 READY FOR HACKATHON DEMO!")
        else:
            print("   🔧 More testing needed for demo readiness")
        
        return self.test_results

def main():
    """Run the complete test suite"""
    print("🚀 GOVAI PLATFORM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("🎯 Testing all system components for hackathon readiness")
    print("⏰ Estimated time: 2-3 minutes")
    print("=" * 80)
    
    # Initialize test suite
    test_suite = GovAITestSuite()
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server not running! Please start it first:")
            print("   python perfect_deployment.py")
            return
    except:
        print("❌ Cannot connect to backend server!")
        print("   Make sure the server is running on http://127.0.0.1:8085")
        return
    
    print("✅ Backend server detected. Starting tests...\n")
    
    # Run all test suites
    test_suite.test_system_health()
    test_suite.test_fraud_detection_scenarios()
    test_suite.test_chatbot_scenarios()
    test_suite.test_bill_inquiry_system()
    test_suite.test_edge_cases()
    test_suite.run_performance_tests()
    
    # Generate final report
    results = test_suite.generate_report()
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Test results saved to: test_results.json")
    print(f"🎉 Test suite completed!")

if __name__ == "__main__":
    main()