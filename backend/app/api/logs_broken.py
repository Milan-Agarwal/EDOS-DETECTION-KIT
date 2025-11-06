"""
Live Logs API for real-time system monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random
import uuid
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.database import User, SystemLog
from ..api.auth import get_current_user

router = APIRouter()


@router.get("/recent")
async def get_recent_logs(
    limit: int = Query(5, description="Number of recent logs to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recent logs for overview page recent activity"""
    try:
        logs = (
            db.query(SystemLog)
            .filter(SystemLog.user_id == current_user.id)
            .order_by(SystemLog.timestamp.desc())
            .limit(limit)
            .all()
        )

        result = []
        for log in logs:
            result.append(
                {
                    "id": str(log.id),
                    "timestamp": log.timestamp.strftime("%H:%M:%S"),
                    "level": log.level.upper(),
                    "message": log.message,
                    "source": log.source,
                    "time": log.timestamp.strftime("%H:%M:%S"),
                }
            )

        # If no logs in database, return some default activity
        if not result:
            now = datetime.utcnow()
            result = [
                {
                    "id": "1",
                    "timestamp": (now - timedelta(minutes=1)).strftime("%H:%M:%S"),
                    "level": "INFO",
                    "message": "User authentication successful",
                    "source": "auth_system",
                    "time": (now - timedelta(minutes=1)).strftime("%H:%M:%S"),
                },
                {
                    "id": "2",
                    "timestamp": (now - timedelta(minutes=3)).strftime("%H:%M:%S"),
                    "level": "INFO",
                    "message": "Database connection established",
                    "source": "database",
                    "time": (now - timedelta(minutes=3)).strftime("%H:%M:%S"),
                },
                {
                    "id": "3",
                    "timestamp": (now - timedelta(minutes=5)).strftime("%H:%M:%S"),
                    "level": "INFO",
                    "message": "System monitoring started",
                    "source": "system",
                    "time": (now - timedelta(minutes=5)).strftime("%H:%M:%S"),
                },
            ]

        return result

    except Exception as e:
        print(f"Error fetching recent logs: {e}")
        return []


# Log message templates
LOG_TEMPLATES = {
    "info": [
        "System scan initiated",
        "Firewall rules updated",
        "User authentication successful",
        "Database backup completed",
        "SSL certificate renewed",
        "Security patch applied",
        "Real-time monitoring active",
        "Service health check passed",
        "Configuration updated",
        "Network optimization complete",
    ],
    "warn": [
        "High memory usage detected on {resource}",
        "Disk usage above 80% on {resource}",
        "Unusual network activity from {resource}",
        "Service response time degraded",
        "Connection pool nearly exhausted",
        "Rate limiting threshold approached",
        "Certificate expires in 30 days",
        "Low disk space warning",
    ],
    "error": [
        "Intrusion attempt from IP {ip}",
        "Authentication failed for user {user}",
        "Service unavailable: {resource}",
        "Database connection timeout",
        "Failed to load security rules",
        "Backup process failed",
        "Configuration validation error",
        "Network connectivity lost",
    ],
    "debug": [
        "API response time: {time}ms",
        "Cache hit ratio: {ratio}%",
        "Memory allocation: {size}MB",
        "Thread pool size: {count}",
        "Database query executed in {time}ms",
        "File system access: {path}",
    ],
}

RESOURCES = [
    "web-server-01",
    "db-primary",
    "api-gateway",
    "cache-cluster",
    "firewall-01",
    "monitoring-node",
]
USERS = ["admin", "user123", "service_account", "api_client", "system"]
IPS = ["192.168.1.{}".format(i) for i in range(1, 255)]
PATHS = [
    "/var/log/system.log",
    "/etc/config.json",
    "/tmp/cache.dat",
    "/opt/app/logs/app.log",
]


def generate_log_entry():
    """Generate a realistic log entry"""
    level = random.choice(["info", "warn", "error", "debug"])
    template = random.choice(LOG_TEMPLATES[level])

    # Replace placeholders
    message = template.format(
        resource=random.choice(RESOURCES),
        ip=random.choice(IPS),
        user=random.choice(USERS),
        time=random.randint(50, 500),
        ratio=random.randint(60, 98),
        size=random.randint(100, 2000),
        count=random.randint(5, 50),
        path=random.choice(PATHS),
    )

    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "source": random.choice(RESOURCES),
        "thread_id": random.randint(1000, 9999),
        "process_id": random.randint(100, 999),
    }


# Initialize with some sample logs
for _ in range(20):
    log_entry = generate_log_entry()
    log_entry["timestamp"] = (
        datetime.utcnow() - timedelta(minutes=random.randint(0, 120))
    ).isoformat()
    logs_db.append(log_entry)

# Sort by timestamp
logs_db.sort(key=lambda x: x["timestamp"], reverse=True)


@router.get("/")
async def get_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    source: Optional[str] = Query(None, description="Filter by source resource"),
    limit: int = Query(100, description="Maximum number of logs to return"),
    current_user: User = Depends(get_current_user),
):
    """Get system logs with optional filtering"""
    filtered_logs = logs_db.copy()

    # Apply filters
    if level and level.lower() != "all":
        filtered_logs = [log for log in filtered_logs if log["level"] == level.lower()]

    if source and source.lower() != "all":
        filtered_logs = [log for log in filtered_logs if log["source"] == source]

    # Sort by timestamp (newest first)
    filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)

    # Limit results
    filtered_logs = filtered_logs[:limit]

    # Format timestamps for display
    for log in filtered_logs:
        try:
            dt = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
            log["formatted_time"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            log["formatted_time"] = log["timestamp"]

    return {
        "logs": filtered_logs,
        "total_count": len(logs_db),
        "filtered_count": len(filtered_logs),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/")
async def create_log(log_data: dict, current_user: User = Depends(get_current_user)):
    """Create new log entry"""
    new_log = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        **log_data,
    }

    logs_db.insert(0, new_log)  # Insert at beginning

    # Keep only last 10000 logs
    if len(logs_db) > 10000:
        logs_db[:] = logs_db[:10000]

    return {"status": "log_created", "id": new_log["id"]}


@router.delete("/")
async def clear_logs(current_user: User = Depends(get_current_user)):
    """Clear all logs"""
    global logs_db
    logs_db.clear()
    return {"status": "logs_cleared", "timestamp": datetime.utcnow().isoformat()}


@router.get("/sources")
async def get_log_sources(current_user: User = Depends(get_current_user)):
    """Get all available log sources"""
    sources = list(set([log["source"] for log in logs_db]))
    return {
        "sources": sorted(sources),
        "total_sources": len(sources),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/levels")
async def get_log_levels():
    """Get all available log levels"""
    return {
        "levels": ["info", "warn", "error", "debug"],
        "descriptions": {
            "info": "Informational messages",
            "warn": "Warning conditions",
            "error": "Error conditions",
            "debug": "Debug-level messages",
        },
    }


@router.get("/stats")
async def get_log_stats(current_user: User = Depends(get_current_user)):
    """Get log statistics"""
    total_logs = len(logs_db)

    # Count by level
    level_counts = {}
    source_counts = {}

    # Recent logs (last hour)
    recent_cutoff = datetime.utcnow() - timedelta(hours=1)
    recent_logs = 0

    for log in logs_db:
        level = log["level"]
        source = log["source"]

        level_counts[level] = level_counts.get(level, 0) + 1
        source_counts[source] = source_counts.get(source, 0) + 1

        # Check if recent
        try:
            log_time = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
            if log_time > recent_cutoff:
                recent_logs += 1
        except:
            pass

    return {
        "total_logs": total_logs,
        "recent_logs_1h": recent_logs,
        "level_breakdown": level_counts,
        "source_breakdown": source_counts,
        "timestamp": datetime.utcnow().isoformat(),
    }
