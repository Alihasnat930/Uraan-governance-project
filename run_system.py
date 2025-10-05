"""
GovAI Platform - Complete Setup and Launch Script
Trains models using real data and starts the full system
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def check_dependencies():
    """Check if required packages are installed"""
    print_header("CHECKING DEPENDENCIES")
    
    required_packages = [
        'pandas', 'numpy', 'scikit-learn', 'fastapi', 
        'uvicorn', 'joblib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("✅ All dependencies installed!")
    else:
        print("✅ All dependencies are available!")

def train_models():
    """Train all ML models using real data"""
    print_header("TRAINING ML MODELS")
    
    try:
        print("🏋️ Starting model training pipeline...")
        result = subprocess.run([sys.executable, "train_models.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Model training completed successfully!")
            print("📁 Models saved in: ./models/")
            return True
        else:
            print("❌ Model training failed!")
            print("Error output:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Model training timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Training error: {e}")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    print_header("STARTING BACKEND SERVER")
    
    try:
        print("🚀 Starting FastAPI backend on http://localhost:8000")
        print("📚 API Documentation will be available at: http://localhost:8000/docs")
        
        # Start backend in background
        backend_process = subprocess.Popen(
            [sys.executable, "api/backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if process is still running
        if backend_process.poll() is None:
            print("✅ Backend server started successfully!")
            return backend_process
        else:
            print("❌ Backend server failed to start")
            stdout, stderr = backend_process.communicate()
            print("Error:", stderr.decode())
            return None
            
    except Exception as e:
        print(f"❌ Backend startup error: {e}")
        return None

def start_frontend():
    """Start the frontend HTTP server"""
    print_header("STARTING FRONTEND SERVER")
    
    try:
        print("🌐 Starting frontend server on http://localhost:3000")
        
        # Change to frontend directory
        os.chdir("frontend")
        
        # Start simple HTTP server
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "http.server", "3000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Change back to main directory
        os.chdir("..")
        
        # Give it a moment to start
        time.sleep(2)
        
        if frontend_process.poll() is None:
            print("✅ Frontend server started successfully!")
            print("🌐 Open http://localhost:3000 in your browser")
            return frontend_process
        else:
            print("❌ Frontend server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Frontend startup error: {e}")
        return None

def test_system():
    """Test if the system is working"""
    print_header("TESTING SYSTEM")
    
    try:
        import requests
        
        # Test backend health
        print("🔍 Testing backend health...")
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend health check passed!")
            print(f"   Fraud Detection: {data.get('fraud_detection_accuracy', 0):.1%}")
            print(f"   Chatbot: {data.get('chatbot_accuracy', 0):.1%}")
            print(f"   Analytics: {data.get('analytics_accuracy', 0):.1%}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            
        # Test frontend
        print("🌐 Testing frontend...")
        response = requests.get("http://localhost:3000", timeout=5)
        
        if response.status_code == 200:
            print("✅ Frontend is accessible!")
        else:
            print(f"❌ Frontend test failed: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main setup and launch function"""
    print_header("GOVAI PLATFORM SETUP & LAUNCH")
    print("🏛️ Government AI Transparency Platform")
    print("📊 Real data training with 85%+ accuracy target")
    
    # Step 1: Check dependencies
    check_dependencies()
    
    # Step 2: Train models
    training_success = train_models()
    if not training_success:
        print("⚠️  Continuing with existing models or fallback...")
    
    # Step 3: Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Cannot start system without backend")
        return False
    
    # Step 4: Start frontend  
    frontend_process = start_frontend()
    
    # Step 5: Test system
    time.sleep(2)  # Give servers time to fully start
    test_system()
    
    # Final instructions
    print_header("SYSTEM READY")
    print("🎉 GovAI Platform is now running!")
    print()
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print()
    print("🔍 Features Available:")
    print("   • Contract fraud detection with real data")
    print("   • Multilingual government services chatbot")
    print("   • Government expenditure analytics")
    print("   • Contract database exploration")
    print()
    print("⚠️  Press Ctrl+C to stop all servers")
    
    try:
        # Keep the script running to maintain servers
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process and backend_process.poll() is not None:
                print("❌ Backend process died")
                break
                
            if frontend_process and frontend_process.poll() is not None:
                print("❌ Frontend process died")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
            
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
            
        print("👋 GovAI Platform stopped successfully!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("✅ Setup completed successfully!")
        else:
            print("❌ Setup failed!")
            sys.exit(1)
    except Exception as e:
        print(f"💥 Critical error: {e}")
        sys.exit(1)