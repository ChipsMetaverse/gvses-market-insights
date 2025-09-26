"""
Computer Use Verification Router
=================================
API endpoints for running UI verification with OpenAI Computer Use.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import uuid

from services.computer_use_verifier import get_verifier

router = APIRouter(prefix="/api/verification", tags=["verification"])
logger = logging.getLogger(__name__)

# Store running sessions
verification_sessions: Dict[str, Dict[str, Any]] = {}


class VerificationRequest(BaseModel):
    """Request to run verification scenarios."""
    scenarios: Optional[List[str]] = None  # Specific scenarios to run, or None for all
    tunnel_url: Optional[str] = None  # Override default tunnel URL
    
    
class VerificationResponse(BaseModel):
    """Response from verification request."""
    session_id: str
    status: str
    message: str
    

class VerificationStatus(BaseModel):
    """Status of a verification session."""
    session_id: str
    status: str  # running, completed, failed
    progress: Dict[str, Any]
    timestamp: str


@router.post("/run", response_model=VerificationResponse)
async def run_verification(
    request: VerificationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a verification session.
    
    This runs asynchronously and returns a session ID for tracking.
    """
    try:
        verifier = get_verifier()
        
        # Check if Computer Use is enabled
        if not verifier.use_computer_use:
            raise HTTPException(
                status_code=400,
                detail="Computer Use is not enabled. Set USE_COMPUTER_USE=true in environment."
            )
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Initialize session tracking
        verification_sessions[session_id] = {
            "status": "initializing",
            "started_at": datetime.now().isoformat(),
            "scenarios": request.scenarios or "all",
            "results": []
        }
        
        # Override tunnel URL if provided
        if request.tunnel_url:
            verifier.tunnel_url = request.tunnel_url
        
        # Run verification in background
        background_tasks.add_task(
            run_verification_task,
            session_id,
            request.scenarios
        )
        
        return VerificationResponse(
            session_id=session_id,
            status="started",
            message=f"Verification session started. Track progress at /api/verification/status/{session_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to start verification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{session_id}", response_model=VerificationStatus)
async def get_verification_status(session_id: str):
    """Get the status of a verification session."""
    if session_id not in verification_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    session = verification_sessions[session_id]
    
    return VerificationStatus(
        session_id=session_id,
        status=session["status"],
        progress={
            "started_at": session["started_at"],
            "scenarios": session["scenarios"],
            "completed": len([r for r in session["results"] if r.get("status") == "completed"]),
            "total": len(session["results"]) if session["results"] else 0
        },
        timestamp=datetime.now().isoformat()
    )


@router.get("/report/{session_id}")
async def get_verification_report(session_id: str):
    """
    Get the full report for a verification session.
    
    Returns detailed results including issues found and suggested fixes.
    """
    if session_id not in verification_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    session = verification_sessions[session_id]
    
    if session["status"] != "completed":
        return {
            "session_id": session_id,
            "status": session["status"],
            "message": "Verification still in progress. Check back later."
        }
    
    # Compile report
    results = session["results"]
    
    # Count passes and failures
    total_scenarios = len(results)
    passed = sum(1 for r in results if not r.get("issues"))
    failed = total_scenarios - passed
    
    # Collect all issues and fixes
    all_issues = []
    all_fixes = []
    
    for result in results:
        all_issues.extend(result.get("issues", []))
        all_fixes.extend(result.get("fixes", []))
    
    return {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_scenarios": total_scenarios,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/total_scenarios)*100:.1f}%" if total_scenarios > 0 else "0%"
        },
        "issues": all_issues,
        "suggested_fixes": all_fixes,
        "scenario_results": [
            {
                "name": r.get("scenario"),
                "status": r.get("status"),
                "issues_count": len(r.get("issues", [])),
                "screenshots_count": len(r.get("screenshots", []))
            }
            for r in results
        ],
        "detailed_results": results  # Full results for debugging
    }


@router.get("/sessions")
async def list_verification_sessions():
    """List all verification sessions."""
    return {
        "sessions": [
            {
                "session_id": sid,
                "status": session["status"],
                "started_at": session["started_at"],
                "scenarios": session["scenarios"]
            }
            for sid, session in verification_sessions.items()
        ]
    }


@router.delete("/session/{session_id}")
async def delete_verification_session(session_id: str):
    """Delete a verification session from memory."""
    if session_id not in verification_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    del verification_sessions[session_id]
    
    return {"message": f"Session {session_id} deleted"}


async def run_verification_task(session_id: str, scenarios: Optional[List[str]]):
    """
    Background task to run verification scenarios.
    
    Args:
        session_id: Session ID for tracking
        scenarios: List of scenario names to run, or None for all
    """
    try:
        # Update status
        verification_sessions[session_id]["status"] = "running"
        
        verifier = get_verifier()
        
        # Run scenarios
        if scenarios:
            # Run specific scenarios
            results = []
            for scenario_name in scenarios:
                # Create scenario config
                scenario = {
                    "name": scenario_name,
                    "steps": []  # Would be loaded from config
                }
                result = await verifier.run_scenario(scenario)
                results.append(result)
                
                # Update progress
                verification_sessions[session_id]["results"] = results
        else:
            # Run all default scenarios
            results = await verifier.run_all_scenarios()
            verification_sessions[session_id]["results"] = results
        
        # Mark complete
        verification_sessions[session_id]["status"] = "completed"
        verification_sessions[session_id]["completed_at"] = datetime.now().isoformat()
        
        logger.info(f"Verification session {session_id} completed with {len(results)} scenarios")
        
    except Exception as e:
        logger.error(f"Verification task failed for session {session_id}: {e}")
        verification_sessions[session_id]["status"] = "failed"
        verification_sessions[session_id]["error"] = str(e)


@router.post("/quick-check")
async def quick_verification_check():
    """
    Run a quick verification check on critical issues.
    
    This is a simplified endpoint that runs key tests synchronously.
    """
    try:
        verifier = get_verifier()
        
        # Define quick test scenarios
        quick_scenarios = [
            {
                "name": "Company Info Quick Check",
                "steps": [
                    {
                        "action": "Query: 'What is PLTR?'",
                        "expected": "Company description, not just price"
                    }
                ]
            },
            {
                "name": "Chart Sync Quick Check", 
                "steps": [
                    {
                        "action": "Query: 'Show me MSFT'",
                        "expected": "Chart switches to MSFT"
                    }
                ]
            }
        ]
        
        results = []
        for scenario in quick_scenarios:
            result = await verifier.run_scenario(scenario)
            results.append({
                "scenario": scenario["name"],
                "passed": len(result.get("issues", [])) == 0,
                "issues": result.get("issues", [])
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "all_passed": all(r["passed"] for r in results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Quick check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))