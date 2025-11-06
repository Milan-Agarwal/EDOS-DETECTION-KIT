"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


# Enums
class AlertLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class LogLevel(str, Enum):
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"


class ResourceStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class ResourceHealth(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


# Alert Models
class GeoLocation(BaseModel):
    country_iso: str
    region: str
    city: str
    lat: float
    lng: float


class NetworkEndpoint(BaseModel):
    ip: str
    port: int
    geo: Optional[GeoLocation] = None


class EventInfo(BaseModel):
    kind: str = "alert"
    category: str  # network, security, system
    action: str  # edos_attack_detected, sql_injection, etc.


class ModelInfo(BaseModel):
    name: str
    version: str
    probability: float
    threshold: float
    features_used: Optional[List[str]] = None


class SystemInfo(BaseModel):
    vm_id: Optional[str] = None
    service: Optional[str] = None
    cloud: Optional[str] = None


class Alert(BaseModel):
    id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    alert_id: str
    level: AlertLevel
    event: EventInfo
    source: NetworkEndpoint
    destination: Optional[NetworkEndpoint] = None
    model: Optional[ModelInfo] = None
    message: str
    recommendation: Optional[str] = None
    severity_score: Optional[int] = Field(default=0, ge=0, le=100)
    raw_log_ref: Optional[str] = None
    system: Optional[SystemInfo] = None
    read: bool = False
    time: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )


class AlertCreate(BaseModel):
    level: AlertLevel
    message: str
    source: NetworkEndpoint
    destination: Optional[NetworkEndpoint] = None
    recommendation: Optional[str] = None


class AlertUpdate(BaseModel):
    read: Optional[bool] = None


# Network Models
class NetworkArc(BaseModel):
    id: Optional[str] = None
    startLat: float
    startLng: float
    endLat: float
    endLng: float
    isAttack: bool
    label: Optional[str] = None
    color: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    attack_type: Optional[str] = None
    data_size: Optional[str] = None
    duration: Optional[int] = None  # seconds


class ThreatPoint(BaseModel):
    lat: float
    lng: float
    label: str
    isAttack: bool
    color: str
    size: float = 0.5
    city: Optional[str] = None
    country: Optional[str] = None
    connections: Optional[int] = 0
    status: Optional[str] = "monitoring"


class NetworkTrafficResponse(BaseModel):
    arcs: List[NetworkArc]
    points: List[ThreatPoint]


# Resource Models
class CloudResource(BaseModel):
    id: Optional[int] = None
    name: str
    type: str  # EC2, RDS, Lambda, etc.
    os: str
    status: ResourceStatus
    health: ResourceHealth
    cpu: float = Field(ge=0, le=100)
    memory: float = Field(ge=0, le=100)
    disk: float = Field(ge=0, le=100)
    region: str
    uptime: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ResourceCreate(BaseModel):
    name: str
    type: str
    os: str
    region: str


class ResourceUpdate(BaseModel):
    cpu: Optional[float] = None
    memory: Optional[float] = None
    disk: Optional[float] = None
    status: Optional[ResourceStatus] = None
    health: Optional[ResourceHealth] = None


# Metrics Models
class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    uptime: float


class ThreatMetrics(BaseModel):
    total_detected: int
    blocked_attacks: int
    active_threats: int
    threat_level: str


class NetworkMetrics(BaseModel):
    total_connections: int
    data_processed: str
    bandwidth_usage: float
    regions_monitored: int


class MetricsResponse(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    system: SystemMetrics
    threats: ThreatMetrics
    network: NetworkMetrics


# Log Models
class LogEntry(BaseModel):
    id: Optional[int] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )
    level: LogLevel
    message: str
    source: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class LogCreate(BaseModel):
    level: LogLevel
    message: str
    source: str


# Settings Models
class SecuritySettings(BaseModel):
    authTimeout: int = 30
    maxFailedLogins: int = 5
    twoFactorAuth: bool = True
    autoSecurityScans: bool = True
    realTimeThreatDetection: bool = True


class AlertSettings(BaseModel):
    thresholdLevel: str = "medium"
    emailNotifications: bool = True
    smsNotifications: bool = False
    pushNotifications: bool = True
    alertRetention: int = 90


class SystemSettings(BaseModel):
    theme: str = "dark"
    refreshInterval: int = 5
    autoSave: bool = True
    performanceMode: str = "high"


class NetworkSettings(BaseModel):
    apiEndpoint: str = "https://api.edos-security.com"
    connectionTimeout: int = 5000
    sslVerification: bool = True
    vpnConnection: bool = True


class SettingsResponse(BaseModel):
    security: SecuritySettings
    alerts: AlertSettings
    system: SystemSettings
    network: NetworkSettings


# Authentication Models
class UserProfile(BaseModel):
    firstName: str = "John"
    lastName: str = "Smith"
    email: str = "admin@edos-security.com"
    username: str = "admin"
    role: str = "System Administrator"
    department: str = "Cybersecurity Operations"
    phone: str = "+1 (555) 123-4567"
    lastLogin: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    accountCreated: str = "2023-01-15T10:30:00Z"
    twoFactorEnabled: bool = True
    sessionTimeout: int = 30
    timezone: str = "UTC-5 (Eastern)"
    language: str = "English"


class UserNotifications(BaseModel):
    email: bool = True
    sms: bool = False
    desktop: bool = True
    mobile: bool = True


class UserSecurity(BaseModel):
    passwordLastChanged: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    loginAttempts: int = 0
    accountLocked: bool = False
    ipWhitelist: List[str] = ["192.168.1.100", "10.0.0.50"]


class UserProfileComplete(BaseModel):
    profile: UserProfile
    notifications: UserNotifications
    security: UserSecurity


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


# Chart Data Models
class ChartDataPoint(BaseModel):
    time: str
    timestamp: int
    cpu: int
    memory: int
    network: int
    threats: int
    disk: int


class ChartDataResponse(BaseModel):
    data: List[ChartDataPoint]


# Statistics Models
class AlertStats(BaseModel):
    total: int
    unread: int
    critical: int
    high: int
    medium: int
    low: int


class DashboardStats(BaseModel):
    threats_detected: int
    attacks_blocked: int
    data_processed: str
    system_uptime: float
    active_connections: int
    monitored_regions: int
