"""
Admin routes for database management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.db.session import get_db
from api.db.models import Patient, Case, ModelPrediction, HITLDecision, Report

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/stats")
def get_database_stats(db: Session = Depends(get_db)):
    """Get current database statistics."""
    return {
        "patients": db.query(Patient).count(),
        "cases": db.query(Case).count(),
        "predictions": db.query(ModelPrediction).count(),
        "decisions": db.query(HITLDecision).count(),
        "reports": db.query(Report).count(),
    }


@router.post("/cleanup")
def cleanup_database(
    keep_cases: int = 3,
    confirm: str = "",
    db: Session = Depends(get_db)
):
    """
    Clean up database, keeping only first N cases.
    
    Parameters:
    - keep_cases: Number of cases to keep (0 = delete all)
    - confirm: Must be "YES" to proceed
    """
    if confirm != "YES":
        raise HTTPException(
            status_code=400,
            detail="Must provide confirm='YES' parameter to proceed"
        )
    
    # Get stats before
    before = {
        "patients": db.query(Patient).count(),
        "cases": db.query(Case).count(),
        "predictions": db.query(ModelPrediction).count(),
        "decisions": db.query(HITLDecision).count(),
        "reports": db.query(Report).count(),
    }
    
    try:
        if keep_cases == 0:
            # Delete everything
            db.query(Report).delete()
            db.query(HITLDecision).delete()
            db.query(ModelPrediction).delete()
            db.query(Case).delete()
            db.query(Patient).delete()
        else:
            # Keep first N cases
            cases_to_keep = [c.id for c in db.query(Case).order_by(Case.id).limit(keep_cases).all()]
            patient_ids_to_keep = [c.patient_id for c in db.query(Case).filter(Case.id.in_(cases_to_keep)).all()]
            
            db.query(Report).filter(~Report.case_id.in_(cases_to_keep)).delete(synchronize_session=False)
            db.query(HITLDecision).filter(~HITLDecision.case_id.in_(cases_to_keep)).delete(synchronize_session=False)
            db.query(ModelPrediction).filter(~ModelPrediction.case_id.in_(cases_to_keep)).delete(synchronize_session=False)
            db.query(Case).filter(~Case.id.in_(cases_to_keep)).delete(synchronize_session=False)
            db.query(Patient).filter(~Patient.id.in_(patient_ids_to_keep)).delete(synchronize_session=False)
        
        db.commit()
        
        # Get stats after
        after = {
            "patients": db.query(Patient).count(),
            "cases": db.query(Case).count(),
            "predictions": db.query(ModelPrediction).count(),
            "decisions": db.query(HITLDecision).count(),
            "reports": db.query(Report).count(),
        }
        
        return {
            "success": True,
            "message": f"Kept {keep_cases} cases, deleted the rest",
            "before": before,
            "after": after,
            "deleted": {
                "patients": before["patients"] - after["patients"],
                "cases": before["cases"] - after["cases"],
                "predictions": before["predictions"] - after["predictions"],
                "decisions": before["decisions"] - after["decisions"],
                "reports": before["reports"] - after["reports"],
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
