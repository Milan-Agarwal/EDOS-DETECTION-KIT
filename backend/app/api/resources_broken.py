"""
Cloud Resources Management API
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models.database import User, UserResource, CloudProvider, ResourceType
from ..api.auth import get_current_user
import random

router = APIRouter()


class ResourceCreate(BaseModel):
    name: str
    resource_type_id: str
    cloud_provider_id: str
    region: str
    instance_size: Optional[str] = "t3.medium"
    operating_system: Optional[str] = "ubuntu"
    tags: Optional[dict] = {}


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    instance_size: Optional[str] = None
    tags: Optional[dict] = None
    status: Optional[str] = None


@router.get("/providers")
async def get_cloud_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get available cloud providers"""
    providers = db.query(CloudProvider).all()
    return [{"id": str(p.id), "name": p.name, "description": p.description} for p in providers]


@router.get("/types")
async def get_resource_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get available resource types"""
    types = db.query(ResourceType).all()
    return [{"id": str(t.id), "name": t.name, "description": t.description} for t in types]


# Mock data for now - remove this section
mock_data_start = {
        "id": 1,
        "name": "web-server-01",
        "type": "EC2",
        "os": "ubuntu",
        "status": "running",
        "health": "healthy",
        "cpu": 45,
        "memory": 62,
        "disk": 78,
        "region": "us-east-1",
        "uptime": "45d 12h",
        "created": "2024-09-15T10:30:00Z",
        "last_updated": datetime.utcnow().isoformat(),
    },
    {
        "id": 2,
        "name": "db-primary",
        "type": "RDS",
        "os": "mysql",
        "status": "running",
        "health": "healthy",
        "cpu": 23,
        "memory": 89,
        "disk": 34,
        "region": "us-west-2",
        "uptime": "120d 8h",
        "created": "2024-07-01T14:20:00Z",
        "last_updated": datetime.utcnow().isoformat(),
    },
    {
        "id": 3,
        "name": "api-gateway",
        "type": "Lambda",
        "os": "nodejs",
        "status": "running",
        "health": "warning",
        "cpu": 78,
        "memory": 45,
        "disk": 12,
        "region": "eu-central-1",
        "uptime": "23d 15h",
        "created": "2024-10-10T09:15:00Z",
        "last_updated": datetime.utcnow().isoformat(),
    },
    {
        "id": 4,
        "name": "cache-cluster",
        "type": "ElastiCache",
        "os": "redis",
        "status": "running",
        "health": "healthy",
        "cpu": 12,
        "memory": 34,
        "disk": 89,
        "region": "ap-south-1",
        "uptime": "67d 3h",
        "created": "2024-08-20T16:45:00Z",
        "last_updated": datetime.utcnow().isoformat(),
    },
]


@router.get("/")
async def get_resources(
    search: Optional[str] = Query(
        None, description="Search resources by name, type, or OS"
    ),
    status: Optional[str] = Query(None, description="Filter by status"),
    health: Optional[str] = Query(None, description="Filter by health status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all cloud resources with optional filtering from database"""
    try:
        # Query user's resources
        query = db.query(UserResource).filter(UserResource.user_id == current_user.id)
        
        # Apply filters
        if search:
            query = query.filter(UserResource.name.contains(search))
        if status:
            query = query.filter(UserResource.status == status)
        
        resources = query.all()
        
        # Convert to response format
        result = []
        for resource in resources:
            # Generate mock metrics for now (could be from separate metrics table)
            result.append({
                "id": resource.id,
                "name": resource.name,
                "type": resource.resource_type.name if resource.resource_type else "Unknown",
                "os": resource.operating_system,
                "status": resource.status,
                "health": "healthy" if resource.status == "running" else "warning",
                "cpu": random.randint(20, 80),  # Mock CPU usage
                "memory": random.randint(30, 90),  # Mock memory usage
                "disk": random.randint(40, 85),  # Mock disk usage
                "region": resource.region,
                "uptime": "45d 12h",  # Mock uptime
                "instance_size": resource.instance_size,
                "created_at": resource.created_at.isoformat(),
            })
        
        return result
        
    except Exception as e:
        print(f"Error fetching resources: {e}")
        return []


@router.post("/")
async def create_resource(
    resource: ResourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new cloud resource"""
    try:
        # Check if cloud provider exists
        cloud_provider = db.query(CloudProvider).filter(
            CloudProvider.id == resource.cloud_provider_id
        ).first()
        
        if not cloud_provider:
            raise HTTPException(status_code=404, detail="Cloud provider not found")
        
        # Check if resource type exists
        resource_type = db.query(ResourceType).filter(
            ResourceType.id == resource.resource_type_id
        ).first()
        
        if not resource_type:
            raise HTTPException(status_code=404, detail="Resource type not found")
        
        # Create new resource
        new_resource = UserResource(
            user_id=current_user.id,
            cloud_provider_id=resource.cloud_provider_id,
            resource_type_id=resource.resource_type_id,
            name=resource.name,
            region=resource.region,
            instance_size=resource.instance_size,
            operating_system=resource.operating_system,
            status="running",
            tags=resource.tags or {},
            configuration={}
        )
        
        db.add(new_resource)
        db.commit()
        db.refresh(new_resource)
        
        return {
            "id": new_resource.id,
            "name": new_resource.name,
            "status": new_resource.status,
            "message": "Resource created successfully"
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error creating resource: {e}")
        raise HTTPException(status_code=500, detail="Failed to create resource")
        resource["cpu"] = max(5, min(95, resource["cpu"] + random.randint(-5, 5)))
        resource["memory"] = max(
            10, min(95, resource["memory"] + random.randint(-3, 3))
        )
        resource["disk"] = max(5, min(95, resource["disk"] + random.randint(-2, 2)))
        resource["last_updated"] = datetime.utcnow().isoformat()

    # Apply filters
    if search:
        search_lower = search.lower()
        filtered_resources = [
            r
            for r in filtered_resources
            if search_lower in r["name"].lower()
            or search_lower in r["type"].lower()
            or search_lower in r["os"].lower()
        ]

    if status:
        filtered_resources = [
            r for r in filtered_resources if r["status"].lower() == status.lower()
        ]

    if health:
        filtered_resources = [
            r for r in filtered_resources if r["health"].lower() == health.lower()
        ]

    return filtered_resources


@router.get("/{resource_id}")
async def get_resource(resource_id: int, current_user: str = Depends(verify_token)):
    """Get specific resource by ID"""
    resource = next((r for r in resources_db if r["id"] == resource_id), None)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Add detailed metrics
    detailed_resource = resource.copy()
    detailed_resource.update(
        {
            "network_io": {
                "bytes_in": random.randint(1000000, 10000000),
                "bytes_out": random.randint(500000, 5000000),
                "packets_in": random.randint(1000, 10000),
                "packets_out": random.randint(800, 8000),
            },
            "processes": random.randint(50, 200),
            "connections": random.randint(10, 100),
            "load_average": round(random.uniform(0.5, 4.0), 2),
            "temperature": random.randint(35, 75),
        }
    )

    return detailed_resource


@router.post("/")
async def create_resource(
    resource_data: dict, current_user: str = Depends(verify_token)
):
    """Create new cloud resource"""
    new_id = max([r["id"] for r in resources_db]) + 1 if resources_db else 1

    new_resource = {
        "id": new_id,
        "created": datetime.utcnow().isoformat(),
        "last_updated": datetime.utcnow().isoformat(),
        "status": "running",
        "health": "healthy",
        "cpu": random.randint(20, 40),
        "memory": random.randint(30, 50),
        "disk": random.randint(20, 60),
        **resource_data,
    }

    resources_db.append(new_resource)
    return {"status": "resource_created", "id": new_id, "resource": new_resource}


@router.put("/{resource_id}")
async def update_resource(
    resource_id: int, resource_data: dict, current_user: str = Depends(verify_token)
):
    """Update existing resource"""
    resource = next((r for r in resources_db if r["id"] == resource_id), None)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Update resource data
    for key, value in resource_data.items():
        if key in resource:
            resource[key] = value

    resource["last_updated"] = datetime.utcnow().isoformat()

    return {"status": "resource_updated", "resource": resource}


@router.delete("/{resource_id}")
async def delete_resource(resource_id: int, current_user: str = Depends(verify_token)):
    """Delete resource"""
    global resources_db
    resources_db = [r for r in resources_db if r["id"] != resource_id]
    return {"status": "resource_deleted", "id": resource_id}


@router.get("/stats/overview")
async def get_resource_stats(current_user: str = Depends(verify_token)):
    """Get resource statistics overview"""
    total_resources = len(resources_db)
    running_resources = len([r for r in resources_db if r["status"] == "running"])
    healthy_resources = len([r for r in resources_db if r["health"] == "healthy"])
    warning_resources = len([r for r in resources_db if r["health"] == "warning"])
    critical_resources = len([r for r in resources_db if r["health"] == "critical"])

    # Calculate average utilization
    avg_cpu = (
        sum([r["cpu"] for r in resources_db]) / total_resources
        if total_resources > 0
        else 0
    )
    avg_memory = (
        sum([r["memory"] for r in resources_db]) / total_resources
        if total_resources > 0
        else 0
    )
    avg_disk = (
        sum([r["disk"] for r in resources_db]) / total_resources
        if total_resources > 0
        else 0
    )

    # Count by type and region
    type_counts = {}
    region_counts = {}

    for resource in resources_db:
        res_type = resource["type"]
        region = resource["region"]

        type_counts[res_type] = type_counts.get(res_type, 0) + 1
        region_counts[region] = region_counts.get(region, 0) + 1

    return {
        "total_resources": total_resources,
        "running_resources": running_resources,
        "healthy_resources": healthy_resources,
        "warning_resources": warning_resources,
        "critical_resources": critical_resources,
        "average_utilization": {
            "cpu": round(avg_cpu, 1),
            "memory": round(avg_memory, 1),
            "disk": round(avg_disk, 1),
        },
        "resource_types": type_counts,
        "regions": region_counts,
        "timestamp": datetime.utcnow().isoformat(),
    }
