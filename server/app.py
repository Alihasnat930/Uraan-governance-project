#!/usr/bin/env python3
"""
GovAI Platform - FastAPI Backend Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import pandas as pd
import numpy as np
import joblib
import os
from typing import Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GovAI Transparency Platform",
    description="Government AI services for fraud detection and citizen assistance",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fraud_model = None
chatbot_model = None
feature_scaler = None
feature_names = []
db_path = "data/govai.db"

class ContractAnalysisRequest(BaseModel):
    contract_number: str
    description: str
    amount: float
    supplier: str
    country: str

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    language: Optional[str] = "english"

class BillInquiryRequest(BaseModel):
    cnic: str
    account_number: Optional[str] = None

class ContractResponse(BaseModel):
    risk_level: str
    risk_score: float
    anomaly_score: float
    recommendation: str

class ChatResponse(BaseModel):
    response: str
    intent: str
    language: str

def load_models():
    global fraud_model, chatbot_model, feature_scaler, feature_names
    
    logger.info("Loading GovAI models...")
    
    try:
        # Load optimized production configuration (first priority)
        if os.path.exists("models/final/latest_optimized_config.json"):
            import json
            with open("models/final/latest_optimized_config.json") as f:
                config = json.load(f)
            
            # Load optimized model
            model_file = config.get('model_file')
            if model_file and os.path.exists(model_file):
                fraud_model = joblib.load(model_file)
                logger.info(f"Loaded OPTIMIZED {config['model_name']} (F1={config['performance']['f1_score']:.3f})")
                logger.info(f"Performance improvement: {config['improvement_over_original']}")
            
            # Load optimized scaler
            scaler_file = config.get('scaler_file')
            if scaler_file and os.path.exists(scaler_file):
                feature_scaler = joblib.load(scaler_file)
                logger.info(f"Loaded optimized scaler: {scaler_file}")
            
            # Load optimized feature names
            feature_names = config.get('features', [])
            if feature_names:
                logger.info(f"Loaded {len(feature_names)} optimized features")
        
        # Fallback to previous production configuration
        elif os.path.exists("models/latest_production_config.json"):
            import json
            with open("models/latest_production_config.json") as f:
                config = json.load(f)
            
            # Load best model
            best_model_name = config.get('best_model')
            if best_model_name and best_model_name in config['model_files']:
                model_file = config['model_files'][best_model_name]
                if os.path.exists(model_file):
                    fraud_model = joblib.load(model_file)
                    logger.info(f"Loaded {best_model_name} fraud detection model: {model_file}")
                else:
                    logger.error(f"Model file not found: {model_file}")
            
            # Load scaler
            scaler_file = config.get('scaler_file')
            if scaler_file and os.path.exists(scaler_file):
                feature_scaler = joblib.load(scaler_file)
                logger.info(f"Loaded feature scaler: {scaler_file}")
            
            # Load feature names
            features_file = config.get('features_file')
            if features_file and os.path.exists(features_file):
                with open(features_file) as f:
                    feature_names = json.load(f)
                logger.info(f"Loaded {len(feature_names)} feature names")
        
        # Fallback to old model if new ones not available
        elif os.path.exists("models/isolation_forest_model.pkl"):
            fraud_model = joblib.load("models/isolation_forest_model.pkl")
            logger.info("Loaded fallback fraud detection model")
        else:
            logger.warning("No fraud detection model found")
        
        chatbot_model = {
            'intents': {
                'bill_inquiry': ['bill', 'payment', 'amount', 'بل', 'ادائیگی'],
                'document_request': ['document', 'certificate', 'ID', 'دستاویز', 'سرٹیفکیٹ'],
                'complaint': ['complaint', 'problem', 'issue', 'شکایت', 'مسئلہ'],
                'fraud_report': ['fraud', 'corruption', 'bribe', 'فراڈ', 'بدعنوانی'],
                'emergency': ['urgent', 'emergency', 'help', 'فوری', 'مدد'],
                'information': ['information', 'office', 'hours', 'معلومات', 'دفتر'],
                'budget': ['budget', 'expenditure', 'spending', 'بجٹ', 'اخراجات']
            }
        }
        logger.info("Chatbot model loaded with multilingual support")
        
    except Exception as e:
        logger.error(f"Error loading models: {e}")

def get_db_connection():
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Database not found")
    return sqlite3.connect(db_path)

def detect_language(text: str) -> str:
    # Simple language detection
    urdu_chars = set('آابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنںوہھءیے')
    text_chars = set(text)
    urdu_ratio = len(text_chars.intersection(urdu_chars)) / len(text_chars) if text_chars else 0
    return "urdu" if urdu_ratio > 0.3 else "english"

def classify_intent(text: str) -> str:
    # Import enhanced chatbot
    try:
        from enhanced_chatbot import chatbot
        result = chatbot.get_response(text)
        return result.get('intent', 'general')
    except ImportError:
        # Fallback to original method
        text_lower = text.lower()
        
        if chatbot_model and 'intents' in chatbot_model:
            for intent, keywords in chatbot_model['intents'].items():
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        return intent
        
        return "general"

@app.on_event("startup")
async def startup_event():
    load_models()

@app.get("/")
async def root():
    return {
        "service": "GovAI Transparency Platform",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "fraud_detection": "/fraud-detect",
            "citizen_assistant": "/assistant",
            "bill_inquiry": "/bill-inquiry",
            "health_check": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models": {
            "fraud_detection": fraud_model is not None,
            "chatbot": chatbot_model is not None
        },
        "database": os.path.exists(db_path)
    }

@app.post("/fraud-detect", response_model=ContractResponse)
async def detect_fraud(contract: ContractAnalysisRequest):
    logger.info(f"Analyzing contract: {contract.contract_number}")
    
    try:
        if fraud_model is None or feature_scaler is None or not feature_names:
            # Fallback risk calculation
            risk_score = min(1.0, contract.amount / 10000000)
            anomaly_score = risk_score
        else:
            # Create enhanced features for optimized model
            duration_months = 12  # Default duration
            bid_count = 3  # Default bid count
            
            # Calculate advanced features matching the optimized model
            import math
            
            features_dict = {
                # Basic features
                'contract_value': contract.amount,
                'value_log': math.log1p(contract.amount),
                'value_sqrt': math.sqrt(contract.amount),
                'duration_months': duration_months,
                'bid_count': bid_count,
                'value_per_month': contract.amount / duration_months,
                
                # Statistical features
                'value_zscore': abs(contract.amount - 5000000) / 2000000,  # Z-score approximation
                'value_percentile': min(0.99, contract.amount / 50000000),  # Percentile approximation
                
                # Ratio features (key for fraud detection)
                'value_duration_ratio': contract.amount / duration_months,
                'value_bid_ratio': contract.amount / bid_count,
                'supplier_concentration': min(1.0, contract.amount / 10000000),  # Concentration approximation
                
                # Risk flags (critical for detection)
                'extreme_high_value': 1 if contract.amount > 25000000 else 0,
                'extreme_short_duration': 1 if duration_months <= 3 else 0,
                'extreme_low_bids': 1 if bid_count <= 1 else 0,
                
                # Interaction features
                'high_value_short_duration': (1 if contract.amount > 25000000 else 0) * (1 if duration_months <= 3 else 0),
                'frequent_supplier_high_value': 0,  # Default to 0 for new suppliers
                
                # Ranking features
                'supplier_frequency_rank': 0.2,  # Default moderate frequency
                'dept_frequency_rank': 0.5,  # Default government department frequency
                
                # Risk scores
                'supplier_risk_score': 0.3,  # Default moderate risk
                'manual_anomaly_score': (
                    (1 if contract.amount > 25000000 else 0) * 0.25 +
                    (1 if duration_months <= 3 else 0) * 0.20 +
                    (1 if bid_count <= 1 else 0) * 0.15 +
                    0.3 * 0.30  # supplier risk component
                ),
                
                # Time features
                'weekend_award': 0,  # Default to weekday
                'end_of_year': 0,  # Default to not end of year
                'award_year_encoded': 0  # Default encoding
            }
            
            # Create feature array in correct order
            features = []
            for feature_name in feature_names:
                if feature_name in features_dict:
                    features.append(features_dict[feature_name])
                else:
                    features.append(0.0)  # Default value for missing features
            
            features = np.array([features])
            
            # Use the optimized model
            if hasattr(fraud_model, 'predict_proba'):
                # Random Forest model - use probability prediction
                features_scaled = feature_scaler.transform(features)
                probabilities = fraud_model.predict_proba(features_scaled)[0]
                fraud_probability = probabilities[1] if len(probabilities) > 1 else probabilities[0]
                
                # Use more sensitive threshold for live detection (0.30)
                prediction = 1 if fraud_probability >= 0.30 else 0
                anomaly_score = fraud_probability
                risk_score = fraud_probability
                
            else:
                # Fallback for Isolation Forest
                features_scaled = feature_scaler.transform(features)
                prediction = fraud_model.predict(features_scaled)[0]
                anomaly_score = fraud_model.decision_function(features_scaled)[0]
                risk_score = max(0, min(1, 0.5 + (-anomaly_score * 0.5)))
        
        # Determine risk level
        if risk_score > 0.8:
            risk_level = "CRITICAL"
            recommendation = "Immediate investigation required."
        elif risk_score > 0.6:
            risk_level = "HIGH"
            recommendation = "Detailed review recommended."
        elif risk_score > 0.3:
            risk_level = "MEDIUM"
            recommendation = "Standard verification needed."
        else:
            risk_level = "LOW"
            recommendation = "Contract appears normal."
        
        # Log to database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO contracts 
            (contract_number, description, amount, supplier, country, risk_score, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (contract.contract_number, contract.description, contract.amount, 
                   contract.supplier, contract.country, risk_score, risk_level))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not log to database: {e}")
        
        return ContractResponse(
            risk_level=risk_level,
            risk_score=round(risk_score, 3),
            anomaly_score=round(float(anomaly_score), 3),
            recommendation=recommendation
        )
        
    except Exception as e:
        logger.error(f"Error in fraud detection: {e}")
        raise HTTPException(status_code=500, detail=f"Fraud detection failed: {str(e)}")

@app.post("/assistant", response_model=ChatResponse)
async def citizen_assistant(chat: ChatRequest):
    logger.info(f"Chat request: {chat.message[:50]}...")
    
    try:
        # Detect language
        language = detect_language(chat.message)
        if chat.language:
            language = chat.language
        
        # Classify intent
        intent = classify_intent(chat.message)
        
        # Generate response
        responses = {
            "english": {
                "bill_inquiry": "To check your bill, please provide your CNIC and account number.",
                "document_request": "For documents, visit the nearest government office with required papers.",
                "complaint": "Your complaint has been noted. Please provide details for investigation.",
                "fraud_report": "Thank you for reporting. Fraud cases are taken seriously.",
                "emergency": "For emergencies, call 15 or visit the nearest office immediately.",
                "information": "Government offices are open Monday-Friday, 9 AM to 5 PM.",
                "general": "Hello! I'm your government services assistant. How can I help you?"
            },
            "urdu": {
                "bill_inquiry": "اپنا بل چیک کرنے کے لیے CNIC اور اکاؤنٹ نمبر فراہم کریں۔",
                "document_request": "دستاویزات کے لیے قریبی سرکاری دفتر جائیں۔",
                "complaint": "آپ کی شکایت نوٹ کر لی گئی ہے۔ تفصیلات فراہم کریں۔",
                "fraud_report": "رپورٹ کا شکریہ۔ کرپشن کے معاملات سنجیدگی سے لیے جاتے ہیں۔",
                "emergency": "ایمرجنسی کے لیے 15 پر کال کریں۔",
                "information": "سرکاری دفاتر پیر سے جمعہ کھلے ہیں۔",
                "general": "السلام علیکم! میں سرکاری خدمات کا معاون ہوں۔"
            }
        }
        
        response_text = responses[language].get(intent, responses[language]["general"])
        
        # Log chat
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO chat_logs (user_id, message, response, language, intent)
            VALUES (?, ?, ?, ?, ?)
            """, (chat.user_id, chat.message, response_text, language, intent))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not log chat: {e}")
        
        return ChatResponse(
            response=response_text,
            intent=intent,
            language=language
        )
        
    except Exception as e:
        logger.error(f"Error in chatbot: {e}")
        raise HTTPException(status_code=500, detail=f"Assistant failed: {str(e)}")

@app.post("/bill-inquiry")
async def bill_inquiry(request: BillInquiryRequest):
    logger.info(f"Bill inquiry for CNIC: {request.cnic}")
    
    try:
        conn = get_db_connection()
        
        # Get user info
        user_df = pd.read_sql_query("""
        SELECT * FROM users WHERE cnic = ?
        """, conn, params=(request.cnic,))
        
        if user_df.empty:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_df.iloc[0]
        
        # Get bills
        bills_query = """
        SELECT * FROM bills WHERE cnic = ?
        """
        params = [request.cnic]
        
        if request.account_number:
            bills_query += " AND account = ?"
            params.append(request.account_number)
        
        bills_df = pd.read_sql_query(bills_query, conn, params=tuple(params))
        conn.close()
        
        bills_list = bills_df.to_dict('records') if not bills_df.empty else []
        
        return {
            "user": {
                "name": user['name'],
                "cnic": user['cnic'],
                "language": user['language']
            },
            "bills": bills_list,
            "total_amount": float(bills_df['amount'].sum()) if not bills_df.empty else 0,
            "bill_count": len(bills_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bill inquiry: {e}")
        raise HTTPException(status_code=500, detail=f"Bill inquiry failed: {str(e)}")

@app.get("/analytics/dashboard")
async def analytics_dashboard():
    try:
        conn = get_db_connection()
        
        # Contract statistics
        contracts_df = pd.read_sql_query("SELECT * FROM contracts", conn)
        
        # Risk level distribution
        risk_distribution = contracts_df['risk_level'].value_counts().to_dict()
        
        # Top suppliers
        top_suppliers = contracts_df.groupby('supplier')['amount'].sum().nlargest(10).to_dict()
        
        # Monthly trends
        monthly_trends = {
            "2023-01": float(contracts_df[contracts_df['date_signed'].str.contains('2023-01', na=False)]['amount'].sum()),
            "2023-02": float(contracts_df[contracts_df['date_signed'].str.contains('2023-02', na=False)]['amount'].sum()),
            "2023-03": float(contracts_df[contracts_df['date_signed'].str.contains('2023-03', na=False)]['amount'].sum())
        }
        
        # Bills statistics
        bills_df = pd.read_sql_query("SELECT * FROM bills", conn)
        bill_stats = {
            "total_bills": len(bills_df),
            "total_amount": float(bills_df['amount'].sum()),
            "avg_amount": float(bills_df['amount'].mean()),
            "by_type": bills_df['bill_type'].value_counts().to_dict()
        }
        
        conn.close()
        
        return {
            "contracts": {
                "total_contracts": len(contracts_df),
                "total_value": float(contracts_df['amount'].sum()),
                "risk_distribution": risk_distribution,
                "top_suppliers": top_suppliers,
                "monthly_trends": monthly_trends
            },
            "bills": bill_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

@app.get("/contracts")
async def get_contracts(limit: int = 100, risk_level: Optional[str] = None):
    try:
        conn = get_db_connection()
        
        query = "SELECT * FROM contracts"
        params = []
        
        if risk_level:
            query += " WHERE risk_level = ?"
            params.append(risk_level)
        
        query += f" ORDER BY amount DESC LIMIT {limit}"
        
        contracts_df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return {
            "contracts": contracts_df.to_dict('records'),
            "count": len(contracts_df)
        }
        
    except Exception as e:
        logger.error(f"Error getting contracts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get contracts: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)