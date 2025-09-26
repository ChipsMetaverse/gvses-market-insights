#!/usr/bin/env python3
"""
Test Computer Use Setup
========================
Quick test to verify the Computer Use verification system is properly configured.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from services.computer_use_verifier import ComputerUseVerifier
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_setup():
    """Test that Computer Use is properly configured."""
    print("=" * 60)
    print(" Computer Use Verification System Test")
    print("=" * 60)
    
    # 1. Check environment
    print("\n1. Environment Configuration:")
    print(f"   OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not Set'}")
    use_computer_use = os.getenv('USE_COMPUTER_USE', 'false').lower() == 'true'
    print(f"   USE_COMPUTER_USE: {'✅ Enabled' if use_computer_use else '⚠️  Disabled (set USE_COMPUTER_USE=true to enable)'}")
    tunnel_url = os.getenv('TUNNEL_URL', 'http://localhost:5174')
    print(f"   TUNNEL_URL: {tunnel_url}")
    
    # 2. Check file structure
    print("\n2. File Structure:")
    files_to_check = [
        'services/computer_use_verifier.py',
        'routers/computer_use_router.py',
        'config/computer_use_scenarios.yaml',
        'tools/run_computer_use_verification.py',
        'COMPUTER_USE_SETUP.md',
        'verification_reports/'
    ]
    
    for file_path in files_to_check:
        exists = Path(file_path).exists()
        print(f"   {'✅' if exists else '❌'} {file_path}")
    
    # 3. Test verifier instantiation
    print("\n3. Verifier Instantiation:")
    try:
        verifier = ComputerUseVerifier()
        print(f"   ✅ Verifier created successfully")
        print(f"   Tunnel URL: {verifier.tunnel_url}")
        print(f"   Computer Use Enabled: {verifier.use_computer_use}")
        print(f"   Reports Directory: {verifier.reports_dir}")
    except Exception as e:
        print(f"   ❌ Failed to create verifier: {e}")
        return
    
    # 4. Test scenarios loading
    print("\n4. Test Scenarios:")
    try:
        default_scenarios = verifier._get_default_scenarios()
        print(f"   ✅ Default scenarios loaded: {len(default_scenarios)} scenarios")
        
        # Try to load from YAML
        yaml_path = Path('config/computer_use_scenarios.yaml')
        if yaml_path.exists():
            scenarios = verifier._load_scenarios(str(yaml_path))
            print(f"   ✅ YAML scenarios loaded: {len(scenarios)} scenarios")
        else:
            print(f"   ⚠️  YAML file not found, using defaults")
    except Exception as e:
        print(f"   ❌ Failed to load scenarios: {e}")
    
    # 5. API endpoint availability (without actually running)
    print("\n5. API Endpoints (when server is running):")
    endpoints = [
        "POST /api/verification/run - Start verification session",
        "GET  /api/verification/status/{session_id} - Check session status",
        "GET  /api/verification/report/{session_id} - Get full report",
        "GET  /api/verification/sessions - List all sessions",
        "POST /api/verification/quick-check - Quick verification"
    ]
    for endpoint in endpoints:
        print(f"   • {endpoint}")
    
    # 6. CLI tool
    print("\n6. CLI Tool Usage:")
    print("   To run verification from command line:")
    print("   $ python backend/tools/run_computer_use_verification.py --help")
    print("   $ python backend/tools/run_computer_use_verification.py --quick")
    print("   $ python backend/tools/run_computer_use_verification.py --tunnel-url https://your-tunnel.ngrok.io")
    
    # Summary
    print("\n" + "=" * 60)
    if use_computer_use:
        print(" ✅ Computer Use is ENABLED and ready to use!")
        print("\n Next steps:")
        print(" 1. Start a tunnel service (ngrok/cloudflared)")
        print(" 2. Set TUNNEL_URL in .env")
        print(" 3. Run: python tools/run_computer_use_verification.py")
    else:
        print(" ⚠️  Computer Use is DISABLED")
        print("\n To enable:")
        print(" 1. Set USE_COMPUTER_USE=true in backend/.env")
        print(" 2. Set up a tunnel service (see COMPUTER_USE_SETUP.md)")
        print(" 3. Set TUNNEL_URL to your public tunnel URL")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_setup())