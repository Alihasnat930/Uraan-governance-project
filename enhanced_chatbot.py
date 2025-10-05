"""
Enhanced Multilingual Chatbot for Citizen Services
Comprehensive AI assistant for government transparency platform
"""

import re
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)

class EnhancedCitizenChatbot:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the enhanced chatbot with multilingual support"""
        self.db_path = db_path
        
        # Enhanced intent patterns with more comprehensive coverage
        self.intent_patterns = {
            'bill_inquiry': {
                'english': [
                    r'\b(bill|bills|payment|due|outstanding|electricity|gas|water|utility)\b',
                    r'\b(how much|amount|owe|pay|check bill|bill status)\b',
                    r'\b(electric bill|gas bill|water bill|utility bill)\b'
                ],
                'urdu': [
                    r'\b(بل|بلز|ادائیگی|بقایا|بجلی|گیس|پانی)\b',
                    r'\b(کتنا|رقم|کیسے ادا کریں|بل چیک)\b'
                ]
            },
            'complaint': {
                'english': [
                    r'\b(complaint|complain|problem|issue|report|wrong|broken|not working)\b',
                    r'\b(file complaint|register complaint|report problem)\b',
                    r'\b(road|street|light|water supply|garbage|corruption)\b'
                ],
                'urdu': [
                    r'\b(شکایت|مسئلہ|خرابی|رپورٹ|غلط|ٹوٹا|کام نہیں)\b',
                    r'\b(شکایت درج|مسائل کی رپورٹ)\b',
                    r'\b(سڑک|گلی|بتی|پانی|کوڑا|بدعنوانی)\b'
                ]
            },
            'document_request': {
                'english': [
                    r'\b(document|certificate|copy|form|application|domicile|cnic|passport)\b',
                    r'\b(how to get|apply for|request|need document)\b',
                    r'\b(birth certificate|death certificate|marriage certificate)\b'
                ],
                'urdu': [
                    r'\b(دستاویز|سرٹیفکیٹ|کاپی|فارم|درخواست|ڈومیسائل|شناختی کارڈ)\b',
                    r'\b(کیسے حاصل کریں|درخواست|ضرورت ہے)\b'
                ]
            },
            'emergency': {
                'english': [
                    r'\b(emergency|urgent|help|crisis|fire|ambulance|police|disaster)\b',
                    r'\b(need help|emergency contact|urgent matter)\b',
                    r'\b(accident|flood|earthquake|medical emergency)\b'
                ],
                'urdu': [
                    r'\b(ایمرجنسی|فوری|مدد|بحران|آگ|ایمبولینس|پولیس)\b',
                    r'\b(مدد چاہیے|فوری رابطہ|ہنگامی)\b',
                    r'\b(حادثہ|سیلاب|زلزلہ|طبی ایمرجنسی)\b'
                ]
            },
            'information': {
                'english': [
                    r'\b(information|info|office|hours|location|address|contact|phone)\b',
                    r'\b(office hours|working hours|contact number|address)\b',
                    r'\b(where|when|how|what time|location)\b'
                ],
                'urdu': [
                    r'\b(معلومات|دفتر|اوقات|پتہ|رابطہ|فون)\b',
                    r'\b(دفتری اوقات|کام کے اوقات|رابطہ نمبر)\b',
                    r'\b(کہاں|کب|کیسے|کیا وقت|جگہ)\b'
                ]
            },
            'fraud_report': {
                'english': [
                    r'\b(fraud|corruption|bribe|illegal|scam|fake|cheat|dishonest)\b',
                    r'\b(report fraud|corruption report|illegal activity)\b',
                    r'\b(taking money|asking bribe|corrupt official)\b'
                ],
                'urdu': [
                    r'\b(دھوکہ|بدعنوانی|رشوت|غیرقانونی|جعلی|فریب)\b',
                    r'\b(فراڈ کی رپورٹ|بدعنوانی کی شکایت)\b',
                    r'\b(پیسے مانگنا|رشوت مانگنا|کرپٹ آفیسر)\b'
                ]
            },
            'services': {
                'english': [
                    r'\b(service|services|what do you provide|help with|assistance)\b',
                    r'\b(government service|public service|citizen service)\b',
                    r'\b(what can you do|available service)\b'
                ],
                'urdu': [
                    r'\b(خدمات|سروس|کیا فراہم|مدد|امداد)\b',
                    r'\b(حکومتی خدمات|عوامی خدمات|شہری خدمات)\b',
                    r'\b(کیا کر سکتے ہیں|دستیاب خدمات)\b'
                ]
            }
        }
        
        # Enhanced responses with more comprehensive information
        self.responses = {
            'bill_inquiry': {
                'english': [
                    "I can help you check your utility bills! 💰\n\nTo check your bills:\n1️⃣ Provide your CNIC number\n2️⃣ Or give me your full name\n3️⃣ I'll search our database for your outstanding bills\n\n🔍 You can also ask: 'Check bill for CNIC 42101-1234567-1'",
                    "Looking for bill information? 📋\n\nI can check:\n• Electricity bills\n• Gas bills  \n• Water bills\n• Property tax\n• Other government dues\n\nJust provide your CNIC or name and I'll find your records!",
                    "Bill inquiry service is available 24/7! 🕐\n\nWhat I can do:\n✅ Check outstanding amounts\n✅ Show payment history\n✅ Provide payment methods\n✅ Give due dates\n\nShare your CNIC number to get started."
                ],
                'urdu': [
                    "میں آپ کے بلز چیک کرنے میں مدد کر سکتا ہوں! 💰\n\nبل چیک کرنے کے لیے:\n1️⃣ اپنا شناختی کارڈ نمبر دیں\n2️⃣ یا اپنا پورا نام بتائیں\n3️⃣ میں آپ کے بقایا بلز تلاش کروں گا\n\n🔍 آپ یہ بھی پوچھ سکتے ہیں: 'شناختی کارڈ 42101-1234567-1 کا بل چیک کریں'",
                    "بل کی معلومات تلاش کر رہے ہیں؟ 📋\n\nمیں یہ چیک کر سکتا ہوں:\n• بجلی کے بل\n• گیس کے بل\n• پانی کے بل\n• پراپرٹی ٹیکس\n• دیگر حکومتی واجبات\n\nصرف اپنا شناختی کارڈ یا نام دیں!",
                    "بل انکوائری سروس 24/7 دستیاب ہے! 🕐\n\nمیں یہ کر سکتا ہوں:\n✅ بقایا رقم چیک کرنا\n✅ ادائیگی کی تاریخ دکھانا\n✅ ادائیگی کے طریقے بتانا\n✅ آخری تاریخ بتانا\n\nشروع کرنے کے لیے اپنا شناختی کارڈ نمبر شیئر کریں۔"
                ]
            },
            'complaint': {
                'english': [
                    "I'll help you file a complaint! 📝\n\nComplaint Categories:\n🏗️ Infrastructure (roads, bridges)\n💡 Utilities (electricity, water, gas)\n🗑️ Sanitation & cleanliness\n👮 Law & order issues\n💰 Corruption reports\n🏥 Public services\n\nPlease describe your issue in detail, and I'll guide you through the process.",
                    "Filing a complaint is easy! 📋\n\nStep-by-step process:\n1️⃣ Choose complaint category\n2️⃣ Provide detailed description\n3️⃣ Add location/address\n4️⃣ Attach photos if possible\n5️⃣ Get complaint reference number\n\nWhat type of issue would you like to report?",
                    "Your voice matters! 🗣️\n\nI can help with:\n• Road repair requests\n• Water supply issues\n• Electricity problems\n• Garbage collection\n• Corruption reports\n• Public service complaints\n\nDescribe your problem and I'll connect you with the right department."
                ],
                'urdu': [
                    "میں آپ کی شکایت درج کرنے میں مدد کروں گا! 📝\n\nشکایت کی اقسام:\n🏗️ بنیادی ڈھانچہ (سڑکیں، پل)\n💡 یوٹیلٹیز (بجلی، پانی، گیس)\n🗑️ صفائی\n👮 امن و امان\n💰 بدعنوانی کی رپورٹ\n🏥 عوامی خدمات\n\nبراہ کرم اپنے مسئلے کی تفصیل بیان کریں۔",
                    "شکایت درج کرنا آسان ہے! 📋\n\nمرحلہ وار عمل:\n1️⃣ شکایت کی قسم منتخب کریں\n2️⃣ تفصیلی وضاحت دیں\n3️⃣ مقام/پتہ شامل کریں\n4️⃣ ممکن ہو تو تصاویر منسلک کریں\n5️⃣ شکایت کا ریفرنس نمبر حاصل کریں\n\nآپ کس قسم کا مسئلہ رپورٹ کرنا چاہتے ہیں؟",
                    "آپ کی آواز اہم ہے! 🗣️\n\nمیں یہ مدد کر سکتا ہوں:\n• سڑک کی مرمت کی درخواست\n• پانی کی فراہمی کے مسائل\n• بجلی کے مسائل\n• کوڑا اٹھانے کی شکایت\n• بدعنوانی کی رپورٹ\n• عوامی خدمات کی شکایات\n\nاپنا مسئلہ بیان کریں اور میں آپ کو متعلقہ شعبے سے جوڑوں گا۔"
                ]
            },
            'document_request': {
                'english': [
                    "I can guide you through document processes! 📄\n\nAvailable Documents:\n🆔 CNIC/Identity Card\n🏠 Domicile Certificate\n👶 Birth Certificate\n💒 Marriage Certificate\n📜 Character Certificate\n🎓 Educational Documents\n\nWhich document do you need? I'll provide step-by-step guidance.",
                    "Document services made easy! 📋\n\nRequired items (general):\n✅ Application form\n✅ Photos (passport size)\n✅ Copy of CNIC\n✅ Fee payment\n✅ Supporting documents\n\nProcessing time: 7-15 working days\nUrgent processing: Available for some documents\n\nWhat specific document are you looking for?",
                    "All document services under one roof! 🏢\n\nOnline services:\n• Download application forms\n• Check application status\n• Schedule appointments\n• Pay fees online\n\nOffice visits:\n• Submit applications\n• Biometric verification\n• Document collection\n\nTell me which document you need and I'll help!"
                ],
                'urdu': [
                    "میں آپ کو دستاویزات کے عمل میں رہنمائی کر سکتا ہوں! 📄\n\nدستیاب دستاویزات:\n🆔 شناختی کارڈ\n🏠 ڈومیسائل سرٹیفکیٹ\n👶 پیدائشی سرٹیفکیٹ\n💒 شادی کا سرٹیفکیٹ\n📜 کردار کا سرٹیفکیٹ\n🎓 تعلیمی دستاویزات\n\nآپ کو کون سا دستاویز چاہیے؟",
                    "دستاویز کی خدمات آسان بنائی گئیں! 📋\n\nضروری اشیاء (عام):\n✅ درخواست کا فارم\n✅ تصاویر (پاسپورٹ سائز)\n✅ شناختی کارڈ کی کاپی\n✅ فیس کی ادائیگی\n✅ معاون دستاویزات\n\nکارروائی کا وقت: 7-15 کاروباری دن\nفوری کارروائی: کچھ دستاویزات کے لیے دستیاب\n\nآپ کو کون سا مخصوص دستاویز چاہیے؟",
                    "تمام دستاویزی خدمات ایک ہی چھت کے نیچے! 🏢\n\nآن لائن خدمات:\n• درخواست کے فارم ڈاؤن لوڈ کریں\n• درخواست کی صورتحال چیک کریں\n• ملاقات کا وقت طے کریں\n• آن لائن فیس ادا کریں\n\nدفتری ملاقات:\n• درخواست جمع کرانا\n• بائیو میٹرک تصدیق\n• دستاویز کی حصولیابی\n\nبتائیں آپ کو کون سا دستاویز چاہیے!"
                ]
            },
            'emergency': {
                'english': [
                    "🚨 EMERGENCY SERVICES 🚨\n\nImmediate Help:\n🚑 Ambulance: 1122\n🚓 Police: 15\n🔥 Fire Brigade: 16\n⛑️ Rescue Services: 1122\n\n24/7 Emergency Hotlines:\n📞 Disaster Management: 1129\n📞 Women Helpline: 1091\n📞 Child Protection: 1121\n\nIf this is a life-threatening emergency, please call the numbers above immediately!",
                    "Emergency assistance available now! 🆘\n\nWhat type of emergency?\n🏥 Medical Emergency → Call 1122\n🚓 Crime/Security → Call 15  \n🔥 Fire/Explosion → Call 16\n⛈️ Natural Disaster → Call 1129\n👨‍⚕️ Poison Control → Call 1166\n\nFor non-life threatening issues, I can help connect you with the right services.",
                    "Emergency protocols activated! 🚨\n\nCritical Services:\n• Pakistan Emergency Services: 1122\n• Police Emergency: 15\n• Fire Department: 16\n• Traffic Police: 1915\n• Anti-Corruption: 1717\n\nPlease describe your emergency and location. I'll provide immediate guidance and connect you with appropriate services."
                ],
                'urdu': [
                    "🚨 ایمرجنسی خدمات 🚨\n\nفوری مدد:\n🚑 ایمبولینس: 1122\n🚓 پولیس: 15\n🔥 فائر بریگیڈ: 16\n⛑️ ریسکیو سروسز: 1122\n\n24/7 ایمرجنسی ہاٹ لائنز:\n📞 ڈیزاسٹر میناجمنٹ: 1129\n📞 خواتین ہیلپ لائن: 1091\n📞 چائلڈ پروٹیکشن: 1121\n\nاگر یہ جان لیوا ہنگامی صورتحال ہے تو فوراً اوپر دیے گئے نمبروں پر کال کریں!",
                    "ایمرجنسی امداد فی الوقت دستیاب ہے! 🆘\n\nکس قسم کی ایمرجنسی؟\n🏥 طبی ایمرجنسی → 1122 کال کریں\n🚓 جرم/سیکیورٹی → 15 کال کریں\n🔥 آگ/دھماکہ → 16 کال کریں\n⛈️ قدرتی آفت → 1129 کال کریں\n👨‍⚕️ زہر کنٹرول → 1166 کال کریں\n\nغیر جان لیوا مسائل کے لیے، میں آپ کو صحیح خدمات سے جوڑنے میں مدد کر سکتا ہوں۔",
                    "ایمرجنسی پروٹوکول فعال! 🚨\n\nاہم خدمات:\n• پاکستان ایمرجنسی سروسز: 1122\n• پولیس ایمرجنسی: 15\n• فائر ڈیپارٹمنٹ: 16\n• ٹریفک پولیس: 1915\n• اینٹی کرپشن: 1717\n\nبراہ کرم اپنی ایمرجنسی اور مقام کا تفصیل بیان کریں۔ میں فوری رہنمائی فراہم کروں گا۔"
                ]
            },
            'information': {
                'english': [
                    "Government office information at your service! 🏢\n\nGeneral Office Hours:\n🕘 Monday-Thursday: 8:00 AM - 4:00 PM\n🕘 Friday: 8:00 AM - 12:30 PM\n🚫 Closed: Saturday & Sunday\n\nContact Information:\n📞 Main Helpline: 111-222-333\n📧 Email: info@govai.gov.pk\n🌐 Website: www.govai.gov.pk\n\nWhich specific office or service do you need information about?",
                    "Office locations and services! 📍\n\nMain Services Centers:\n🏛️ Central Office: Blue Area, Islamabad\n🏢 Regional Office: Gulberg, Lahore  \n🏗️ Branch Office: Clifton, Karachi\n\nServices Available:\n• Document processing\n• Bill payments\n• Complaint registration\n• Information services\n\nNeed directions to a specific location?",
                    "Complete information directory! 📚\n\nQuick Access:\n🔍 Service information\n📋 Forms & applications\n💰 Fee structures  \n⏰ Processing times\n📞 Department contacts\n🗺️ Office locations\n\nWhat specific information are you looking for? I can provide detailed guidance!"
                ],
                'urdu': [
                    "حکومتی دفاتر کی معلومات آپ کی خدمت میں! 🏢\n\nعام دفتری اوقات:\n🕘 پیر سے جمعرات: 8:00 صبح سے 4:00 شام\n🕘 جمعہ: 8:00 صبح سے 12:30 دوپہر\n🚫 بند: ہفتہ اور اتوار\n\nرابطہ معلومات:\n📞 مین ہیلپ لائن: 111-222-333\n📧 ای میل: info@govai.gov.pk\n🌐 ویب سائٹ: www.govai.gov.pk\n\nآپ کو کس مخصوص دفتر یا خدمت کے بارے میں معلومات چاہیے؟",
                    "دفتری مقامات اور خدمات! 📍\n\nمیں سروس سینٹرز:\n🏛️ مرکزی دفتر: بلیو ایریا، اسلام آباد\n🏢 علاقائی دفتر: گلبرگ، لاہور\n🏗️ برانچ آفس: کلفٹن، کراچی\n\nدستیاب خدمات:\n• دستاویز کی کارروائی\n• بل کی ادائیگی\n• شکایت کا اندراج\n• معلوماتی خدمات\n\nکسی مخصوص مقام کا راستہ چاہیے؟",
                    "مکمل معلوماتی ڈائرکٹری! 📚\n\nفوری رسائی:\n🔍 خدمات کی معلومات\n📋 فارمز اور درخواستیں\n💰 فیس کا ڈھانچہ\n⏰ کارروائی کا وقت\n📞 شعبہ جاتی رابطے\n🗺️ دفتری مقامات\n\nآپ کو کیا مخصوص معلومات چاہیے؟ میں تفصیلی رہنمائی فراہم کر سکتا ہوں!"
                ]
            },
            'fraud_report': {
                'english': [
                    "Thank you for reporting potential fraud! 🛡️\n\nFraud Reporting Process:\n1️⃣ Document all evidence (receipts, communications)\n2️⃣ Note names, dates, and amounts involved\n3️⃣ File formal complaint with Anti-Corruption\n4️⃣ Get complaint reference number\n5️⃣ Follow up regularly\n\nAnti-Corruption Helpline: 1717\nSecure Online Portal: Available\nWhistleblower Protection: Guaranteed\n\nYour identity will be protected. Please provide details about the incident.",
                    "Corruption reporting made secure! 🔐\n\nWhat to report:\n💰 Bribery demands\n📋 Document fraud\n⚖️ Abuse of authority\n💼 Misuse of resources\n🏗️ Contract irregularities\n\nReporting channels:\n📞 Hotline: 1717 (24/7)\n💻 Online portal (anonymous)\n📧 Email: anticorruption@gov.pk\n🏢 Walk-in centers\n\nAll reports are investigated confidentially.",
                    "Fighting corruption together! ⚔️\n\nProtection Guaranteed:\n🛡️ Anonymous reporting available\n🔒 Whistleblower protection laws\n⚖️ Legal support provided\n🏆 Recognition for honest citizens\n\nEvidence Collection:\n📷 Photos/videos\n📄 Documents/receipts\n👥 Witness information\n📝 Detailed incident report\n\nEvery report helps build a transparent government!"
                ],
                'urdu': [
                    "ممکنہ فراڈ کی اطلاع کے لیے شکریہ! 🛡️\n\nفراڈ رپورٹنگ کا عمل:\n1️⃣ تمام ثبوت محفوظ کریں (رسیدیں، بات چیت)\n2️⃣ نام، تاریخ، اور رقم نوٹ کریں\n3️⃣ انٹی کرپشن کے ساتھ باضابطہ شکایت درج کرائیں\n4️⃣ شکایت کا ریفرنس نمبر حاصل کریں\n5️⃣ باقاعدگی سے فالو اپ کریں\n\nانٹی کرپشن ہیلپ لائن: 1717\nمحفوظ آن لائن پورٹل: دستیاب\nمخبر کا تحفظ: مضمون\n\nآپ کی شناخت محفوظ رہے گی۔ واقعے کی تفصیلات فراہم کریں۔",
                    "بدعنوانی کی رپورٹنگ محفوظ بنائی گئی! 🔐\n\nکیا رپورٹ کریں:\n💰 رشوت کے مطالبات\n📋 دستاویز میں فراڈ\n⚖️ اختیار کا ناجائز استعمال\n💼 وسائل کا غلط استعمال\n🏗️ کنٹریکٹ میں بے قاعدگیاں\n\nرپورٹنگ کے ذرائع:\n📞 ہاٹ لائن: 1717 (24/7)\n💻 آن لائن پورٹل (گمنام)\n📧 ای میل: anticorruption@gov.pk\n🏢 واک ان سینٹرز\n\nتمام رپورٹس کی خفیہ تحقیقات ہوتی ہیں۔",
                    "بدعنوانی کے خلاف مل کر لڑیں! ⚔️\n\nتحفظ کی ضمانت:\n🛡️ گمنام رپورٹنگ دستیاب\n🔒 مخبر کے تحفظ کے قوانین\n⚖️ قانونی مدد فراہم کی جاتی ہے\n🏆 ایمانdar شہریوں کے لیے اعتراف\n\nثبوت اکٹھا کرنا:\n📷 تصاویر/ویڈیوز\n📄 دستاویزات/رسیدیں\n👥 گواہوں کی معلومات\n📝 تفصیلی واقعہ رپورٹ\n\nہر رپورٹ شفاف حکومت بنانے میں مدد کرتی ہے!"
                ]
            },
            'services': {
                'english': [
                    "Welcome to GovAI Services! 🏛️\n\nI can assist you with:\n\n💰 **Bill Services:**\n• Check outstanding bills\n• Payment information\n• Bill history\n\n📝 **Complaints & Reports:**\n• File complaints\n• Track complaint status\n• Report corruption\n\n📄 **Document Services:**\n• Application guidance\n• Required documents\n• Processing times\n\n🆘 **Emergency Services:**\n• Emergency contacts\n• Immediate assistance\n• Crisis support\n\n🌐 **Available in English & Urdu**\nHow can I help you today?",
                    "Your AI Government Assistant! 🤖\n\nCore Services:\n\n🔍 **Information Services:**\n• Office locations & hours\n• Contact information\n• Service procedures\n\n💡 **Smart Features:**\n• Multilingual support (EN/UR)\n• 24/7 availability\n• Instant responses\n• Secure & private\n\n📊 **Additional Features:**\n• Bill payment guidance\n• Form downloads\n• Status tracking\n• FAQ assistance\n\nWhat would you like to know about?",
                    "Complete Government Solutions! 🎯\n\n🏅 **Premium Features:**\n• AI-powered responses\n• Real-time bill checking\n• Fraud detection alerts\n• Multi-department coordination\n\n🔒 **Security & Privacy:**\n• Encrypted communications\n• No data storage\n• Anonymous options\n• Secure transactions\n\n⚡ **Quick Actions:**\n• Emergency services\n• Bill inquiries\n• Complaint filing\n• Document requests\n\nTell me what you need - I'm here to help!"
                ],
                'urdu': [
                    "GovAI خدمات میں خوش آمدید! 🏛️\n\nمیں آپ کی مدد کر سکتا ہوں:\n\n💰 **بل کی خدمات:**\n• بقایا بل چیک کرنا\n• ادائیگی کی معلومات\n• بل کی تاریخ\n\n📝 **شکایات اور رپورٹس:**\n• شکایت درج کرانا\n• شکایت کی صورتحال ٹریک کرنا\n• بدعنوانی کی رپورٹ\n\n📄 **دستاویز کی خدمات:**\n• درخواست کی رہنمائی\n• ضروری دستاویزات\n• کارروائی کا وقت\n\n🆘 **ایمرجنسی خدمات:**\n• ایمرجنسی رابطے\n• فوری امداد\n• بحرانی مدد\n\n🌐 **انگریزی اور اردو میں دستیاب**\nآج میں آپ کی کیا مدد کر سکتا ہوں؟",
                    "آپ کا AI حکومتی معاون! 🤖\n\nبنیادی خدمات:\n\n🔍 **معلوماتی خدمات:**\n• دفتری مقامات اور اوقات\n• رابطے کی معلومات\n• خدمات کے طریقہ کار\n\n💡 **سمارٹ فیچرز:**\n• کثیر لسانی مدد (EN/UR)\n• 24/7 دستیابی\n• فوری جوابات\n• محفوظ اور نجی\n\n📊 **اضافی فیچرز:**\n• بل ادائیگی کی رہنمائی\n• فارم ڈاؤن لوڈ\n• صورتحال ٹریکنگ\n• FAQ امداد\n\nآپ کیا جاننا چاہتے ہیں؟",
                    "مکمل حکومتی حل! 🎯\n\n🏅 **پریمیم فیچرز:**\n• AI طاقت والے جوابات\n• حقیقی وقت بل چیکنگ\n• فراڈ ڈیٹیکشن الرٹس\n• ملٹی ڈیپارٹمنٹ کوآرڈینیشن\n\n🔒 **سیکیورٹی اور پرائیویسی:**\n• انکرپٹڈ کمیونیکیشن\n• کوئی ڈیٹا اسٹوریج نہیں\n• گمنام آپشنز\n• محفوظ لین دین\n\n⚡ **فوری اعمال:**\n• ایمرجنسی خدمات\n• بل کی انکوائری\n• شکایت درج کرانا\n• دستاویز کی درخواست\n\nبتائیں آپ کو کیا چاہیے - میں مدد کے لیے موجود ہوں!"
                ]
            }
        }
        
        # Greeting patterns
        self.greetings = {
            'english': [
                "Hello! I'm your AI Government Assistant. How can I help you today? 🏛️",
                "Welcome to GovAI! I'm here to assist with government services. What do you need? 🤖",
                "Hi there! Ready to help with bills, complaints, documents, and more. What's on your mind? 💡"
            ],
            'urdu': [
                "السلام علیکم! میں آپ کا AI حکومتی معاون ہوں۔ آج میں آپ کی کیا مدد کر سکتا ہوں؟ 🏛️", 
                "GovAI میں خوش آمدید! میں حکومتی خدمات میں مدد کے لیے موجود ہوں۔ آپ کو کیا چاہیے؟ 🤖",
                "السلام علیکم! بلز، شکایات، دستاویزات اور مزید میں مدد کے لیے تیار ہوں۔ آپ کیا چاہتے ہیں؟ 💡"
            ]
        }
        
        # Default responses for unrecognized inputs
        self.default_responses = {
            'english': [
                "I'm here to help with government services! I can assist with:\n• 💰 Bill inquiries\n• 📝 Filing complaints\n• 📄 Document applications\n• 🆘 Emergency services\n• ℹ️ General information\n\nCould you please rephrase your question or choose from the options above?",
                "I want to help but didn't quite understand. I specialize in:\n• Checking bills and payments\n• Filing complaints and reports\n• Document and certificate guidance\n• Emergency service contacts\n• Office information\n\nWhat specific service do you need?",
                "Let me assist you better! I can help with government services like bill payments, complaints, documents, and emergency contacts. Could you tell me more specifically what you're looking for?"
            ],
            'urdu': [
                "میں حکومتی خدمات میں مدد کے لیے موجود ہوں! میں یہ مدد کر سکتا ہوں:\n• 💰 بل کی انکوائری\n• 📝 شکایات درج کرانا\n• 📄 دستاویز کی درخواستیں\n• 🆘 ایمرجنسی خدمات\n• ℹ️ عمومی معلومات\n\nکیا آپ اپنا سوال دوبارہ پوچھ سکتے ہیں یا اوپر سے کوئی آپشن منتخب کر سکتے ہیں؟",
                "میں مدد کرنا چاہتا ہوں لیکن مکمل طور پر سمجھ نہیں پایا۔ میں یہ خدمات میں مہارت رکھتا ہوں:\n• بل چیک کرنا اور ادائیگیاں\n• شکایات اور رپورٹس درج کرانا\n• دستاویزات اور سرٹیفکیٹس کی رہنمائی\n• ایمرجنسی سروس کے رابطے\n• دفتری معلومات\n\nآپ کو کیا مخصوص خدمت چاہیے؟",
                "میں آپ کی بہتر مدد کرنے دیں! میں حکومتی خدمات جیسے بل ادائیگی، شکایات، دستاویزات، اور ایمرجنسی رابطوں میں مدد کر سکتا ہوں۔ کیا آپ مزید واضح طور پر بتا سکتے ہیں کہ آپ کیا تلاش کر رہے ہیں؟"
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """Enhanced language detection with better accuracy"""
        if not text:
            return 'english'
        
        # Urdu Unicode ranges
        urdu_chars = set('آابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنںوہھءیے')
        text_chars = set(text.lower())
        
        # Count Urdu characters
        urdu_count = len(text_chars.intersection(urdu_chars))
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return 'english'
        
        urdu_ratio = urdu_count / total_chars
        
        # Enhanced detection with context
        if urdu_ratio > 0.2:  # Even small amounts of Urdu indicate Urdu text
            return 'urdu'
        
        # Check for common Urdu words in Roman script
        urdu_roman_words = ['kya', 'kaise', 'kahan', 'kyun', 'aap', 'hum', 'main', 'bill', 'shikayat']
        text_lower = text.lower()
        
        for word in urdu_roman_words:
            if word in text_lower:
                return 'urdu'
        
        return 'english'
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """Enhanced intent classification with confidence scoring"""
        text_lower = text.lower()
        detected_language = self.detect_language(text)
        
        intent_scores = {}
        
        # Check each intent against patterns
        for intent, patterns in self.intent_patterns.items():
            score = 0
            
            # Check patterns for both languages
            for lang in ['english', 'urdu']:
                if lang in patterns:
                    for pattern in patterns[lang]:
                        matches = len(re.findall(pattern, text_lower))
                        # Weight matches by language preference
                        weight = 1.0 if lang == detected_language else 0.7
                        score += matches * weight
            
            intent_scores[intent] = score
        
        # Find best match
        if intent_scores:
            best_intent = max(intent_scores.keys(), key=lambda x: intent_scores[x])
            confidence = intent_scores[best_intent]
            
            # Normalize confidence (simple approach)
            if confidence > 0:
                # Add some context-based scoring
                if 'emergency' in text_lower or 'urgent' in text_lower or 'فوری' in text:
                    if best_intent == 'emergency':
                        confidence += 2
                
                return best_intent, min(confidence / 3.0, 1.0)  # Cap at 1.0
        
        return 'general', 0.0
    
    def get_response(self, message: str, user_id: str = "default", language: str = "auto") -> Dict[str, Any]:
        """Generate comprehensive response with enhanced features"""
        
        # Auto-detect language if requested
        if language == "auto" or language == "auto-detect":
            detected_language = self.detect_language(message)
        else:
            detected_language = language if language in ['english', 'urdu'] else 'english'
        
        # Handle greetings first
        greeting_patterns = [
            r'\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b',
            r'\b(السلام علیکم|آداب|ہیلو|ہائی)\b',
            r'\b(assalam|adab|namaste)\b'
        ]
        
        for pattern in greeting_patterns:
            if re.search(pattern, message.lower()):
                import random
                response = random.choice(self.greetings[detected_language])
                return {
                    'response': response,
                    'intent': 'greeting',
                    'confidence': 0.95,
                    'language': detected_language,
                    'suggestions': self._get_suggestions(detected_language)
                }
        
        # Classify intent
        intent, confidence = self.classify_intent(message)
        
        # Get appropriate response
        if intent != 'general' and confidence > 0.3:
            # Get response from intent-specific responses
            if intent in self.responses and detected_language in self.responses[intent]:
                import random
                response = random.choice(self.responses[intent][detected_language])
                
                # Add contextual information based on intent
                if intent == 'bill_inquiry':
                    response += self._get_bill_inquiry_context(message)
                elif intent == 'complaint':
                    response += self._get_complaint_context(message)
                elif intent == 'emergency':
                    response += self._get_emergency_context(message)
                
            else:
                response = self._get_default_response(detected_language)
        else:
            response = self._get_default_response(detected_language)
        
        return {
            'response': response,
            'intent': intent,
            'confidence': confidence,
            'language': detected_language,
            'suggestions': self._get_suggestions(detected_language, intent),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_suggestions(self, language: str, intent: Optional[str] = None) -> List[str]:
        """Get contextual suggestions based on language and intent"""
        if language == 'urdu':
            suggestions = [
                "💰 بل چیک کریں",
                "📝 شکایت درج کرائیں", 
                "📄 دستاویزات کی رہنمائی",
                "🆘 ایمرجنسی مدد",
                "ℹ️ دفتری معلومات"
            ]
        else:
            suggestions = [
                "💰 Check my bills",
                "📝 File a complaint",
                "📄 Document guidance", 
                "🆘 Emergency help",
                "ℹ️ Office information"
            ]
        
        # Add intent-specific suggestions
        if intent == 'bill_inquiry':
            if language == 'urdu':
                suggestions.extend(["شناختی کارڈ سے بل چیک کریں", "پیمنٹ کے طریقے"])
            else:
                suggestions.extend(["Check by CNIC", "Payment methods"])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _get_default_response(self, language: str) -> str:
        """Get default response when intent is unclear"""
        import random
        return random.choice(self.default_responses[language])
    
    def _get_bill_inquiry_context(self, message: str) -> str:
        """Add specific context for bill inquiries"""
        cnic_pattern = r'\b\d{5}-\d{7}-\d{1}\b'
        if re.search(cnic_pattern, message):
            return "\n\n🔍 I found a CNIC number in your message. Let me search for bills associated with it..."
        return ""
    
    def _get_complaint_context(self, message: str) -> str:
        """Add specific context for complaints"""
        urgent_patterns = ['urgent', 'emergency', 'immediate', 'فوری', 'ایمرجنسی']
        for pattern in urgent_patterns:
            if pattern in message.lower():
                return "\n\n⚡ I see this is urgent. I'll prioritize your complaint and connect you with immediate assistance."
        return ""
    
    def _get_emergency_context(self, message: str) -> str:
        """Add specific context for emergencies"""
        return "\n\n🚨 This appears to be an emergency. If you're in immediate danger, please call the emergency numbers listed above right away!"

# Global instance for easy importing
chatbot = EnhancedCitizenChatbot()

def get_chatbot_response(message: str, user_id: str = "default", language: str = "auto") -> Dict[str, Any]:
    """Main function to get chatbot response"""
    return chatbot.get_response(message, user_id, language)

# Test function
if __name__ == "__main__":
    # Test the chatbot
    test_messages = [
        "Hello, how can I check my electricity bill?",
        "السلام علیکم، میرا بجلی کا بل کیسے چیک کروں؟",
        "I want to file a complaint about broken streetlight",
        "شکایت درج کرانا چاہتا ہوں سڑک کی بتی خراب ہے",
        "Emergency! Need help immediately!",
        "What documents do I need for CNIC?",
        "Office hours and location please"
    ]
    
    print("🤖 Enhanced Citizen Chatbot Test\n" + "="*50)
    
    for msg in test_messages:
        result = chatbot.get_response(msg)
        print(f"\n📝 Input: {msg}")
        print(f"🎯 Intent: {result['intent']} (Confidence: {result['confidence']:.2f})")
        print(f"🌐 Language: {result['language']}")
        print(f"💬 Response: {result['response'][:200]}...")
        print("-" * 50)