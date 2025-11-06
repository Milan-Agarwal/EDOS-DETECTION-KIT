"""
Alerts API endpoints for real-time threat detection
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.database import User, SecurityAlert
from ..api.auth import get_current_user
import random

router = APIRouter()

# Initialize with some sample alerts
router = APIRouter()

# Sample alerts removed - now using real database


@router.get("/", response_model=List[dict])
async def get_alerts(
    level: Optional[str] = Query(None, description="Filter by alert level"),
    read: Optional[bool] = Query(None, description="Filter by read status"),
    limit: int = Query(50, description="Maximum number of alerts to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all alerts with optional filtering from database"""
    try:
        # Query alerts for current user
        query = db.query(SecurityAlert).filter(SecurityAlert.user_id == current_user.id)

        # Apply filters
        if level:
            query = query.filter(SecurityAlert.severity == level.lower())

        if read is not None:
            # Map read status to alert status
            status_filter = "acknowledged" if read else "new"
            query = query.filter(SecurityAlert.status == status_filter)

        # Order by detected_at (newest first) and limit
        alerts = query.order_by(SecurityAlert.detected_at.desc()).limit(limit).all()

        # Convert to response format
        result = []
        for alert in alerts:
            result.append(
                {
                    "id": str(alert.id),
                    "level": alert.severity.upper(),
                    "message": alert.description,
                    "source": str(alert.source_ip) if alert.source_ip else "unknown",
                    "timestamp": alert.detected_at.isoformat(),
                    "time": alert.detected_at.strftime("%m/%d %H:%M"),
                    "read": alert.status == "acknowledged",
                    "title": alert.title,
                    "category": alert.category,
                    "confidence": (
                        float(alert.confidence_score)
                        if alert.confidence_score
                        else None
                    ),
                    "target_ip": str(alert.target_ip) if alert.target_ip else None,
                    "target_port": alert.target_port,
                    "detection_method": alert.detection_method,
                }
            )

        return result

    except Exception as e:
        print(f"Error fetching alerts: {e}")
        # Return empty list if there's an error
        return []


@router.post("/", response_model=dict)
async def create_alert(alert: dict):
    """Create new alert (typically called by ML model)"""
    new_alert = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow(),
        "read": False,
        **alert,
    }

    alerts_db.insert(0, new_alert)  # Insert at beginning for newest first

    # Keep only last 1000 alerts
    if len(alerts_db) > 1000:
        alerts_db[:] = alerts_db[:1000]

    return {"status": "alert_created", "id": new_alert["id"]}


@router.patch("/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark an alert as read"""
    alert = (
        db.query(SecurityAlert)
        .filter(SecurityAlert.id == alert_id, SecurityAlert.user_id == current_user.id)
        .first()
    )

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()
    db.commit()

    return {"message": "Alert marked as read"}


@router.delete("/{alert_id}")
async def dismiss_alert(alert_id: str, current_user: User = Depends(get_current_user)):
    """Dismiss/delete specific alert"""
    global alerts_db
    alerts_db = [alert for alert in alerts_db if alert["id"] != alert_id]
    return {"message": "Alert dismissed"}


@router.put("/mark-all-read")
async def mark_all_alerts_read(current_user: User = Depends(get_current_user)):
    """Mark all alerts as read"""
    for alert in alerts_db:
        alert["read"] = True
    return {"message": "All alerts marked as read"}


@router.get("/stats")
async def get_alert_stats(current_user: User = Depends(get_current_user)):
    """Get alert statistics"""
    total_alerts = len(alerts_db)
    unread_alerts = len([a for a in alerts_db if not a["read"]])

    # Count by level
    level_counts = {}
    for alert in alerts_db:
        level = alert["level"]
        level_counts[level] = level_counts.get(level, 0) + 1

    # Recent alerts (last 24 hours)
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    recent_alerts = len([a for a in alerts_db if a["timestamp"] > recent_cutoff])

    return {
        "total_alerts": total_alerts,
        "unread_alerts": unread_alerts,
        "recent_alerts_24h": recent_alerts,
        "level_breakdown": level_counts,
        "timestamp": datetime.utcnow().isoformat(),
    }
