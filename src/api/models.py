"""
Common API models and data structures.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Base response models
class BaseResponse(BaseModel):
    """Base response model with common fields."""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginationInfo(BaseModel):
    """Pagination information model."""
    total_count: int
    page_size: int
    current_page: int
    total_pages: int
    has_next: bool
    has_previous: bool

class PaginatedResponse(BaseModel):
    """Base paginated response model."""
    items: List[Any]
    pagination: PaginationInfo

# Enums
class DocumentType(str, Enum):
    """Document type enumeration."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"

class ProcessingStatus(str, Enum):
    """Processing status enumeration."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUEUED = "queued"

class AnalysisDepth(str, Enum):
    """Analysis depth enumeration."""
    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"

class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Priority(str, Enum):
    """Priority level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Common data models
class FileInfo(BaseModel):
    """File information model."""
    filename: str
    size: int
    type: DocumentType
    checksum: Optional[str] = None
    upload_date: datetime

class ProcessingMetrics(BaseModel):
    """Processing metrics model."""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None

class AnalysisMetadata(BaseModel):
    """Analysis metadata model."""
    analysis_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: ProcessingStatus
    configuration: Dict[str, Any]
    metrics: Optional[ProcessingMetrics] = None

class Tag(BaseModel):
    """Tag model for categorization."""
    key: str
    value: str
    category: Optional[str] = None

class Attachment(BaseModel):
    """Attachment model."""
    id: str
    filename: str
    content_type: str
    size: int
    url: Optional[str] = None

# Validation models
class ValidationRule(BaseModel):
    """Validation rule model."""
    rule_id: str
    name: str
    description: str
    category: str
    severity: Priority
    enabled: bool = True

class ValidationResult(BaseModel):
    """Validation result model."""
    rule_id: str
    passed: bool
    score: Optional[float] = None
    message: Optional[str] = None
    suggestions: List[str] = []

# Search and filter models
class SearchFilter(BaseModel):
    """Search filter model."""
    field: str
    operator: str  # 'eq', 'ne', 'gt', 'lt', 'contains', 'in'
    value: Union[str, int, float, List[Any]]

class SearchQuery(BaseModel):
    """Search query model."""
    query: Optional[str] = None
    filters: List[SearchFilter] = []
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # 'asc', 'desc'
    limit: int = 50
    offset: int = 0

class SearchResult(BaseModel):
    """Search result model."""
    items: List[Dict[str, Any]]
    total_count: int
    query_time_ms: float
    facets: Optional[Dict[str, Any]] = None

# Configuration models
class AIConfig(BaseModel):
    """AI service configuration model."""
    provider: str  # 'openai', 'anthropic', 'azure', 'mock'
    model: str
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    timeout_seconds: int = 30

class SystemConfig(BaseModel):
    """System configuration model."""
    ai_config: AIConfig
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: List[str] = [".pdf", ".docx", ".txt", ".md"]
    cache_ttl_seconds: int = 3600
    rate_limit_per_minute: int = 100

# Status and health models
class ComponentStatus(BaseModel):
    """Component status model."""
    name: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None

class SystemHealth(BaseModel):
    """System health model."""
    overall_status: str
    components: List[ComponentStatus]
    uptime_seconds: float
    version: str
    environment: str

# Audit and logging models
class AuditEvent(BaseModel):
    """Audit event model."""
    event_id: str
    timestamp: datetime
    user_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class LogEntry(BaseModel):
    """Log entry model."""
    timestamp: datetime
    level: str  # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    logger: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    extra: Dict[str, Any] = {}

# Integration models
class WebhookConfig(BaseModel):
    """Webhook configuration model."""
    webhook_id: str
    url: str
    events: List[str]
    secret: Optional[str] = None
    enabled: bool = True
    retry_count: int = 3
    timeout_seconds: int = 30

class WebhookEvent(BaseModel):
    """Webhook event model."""
    event_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None

# Export models
class ExportRequest(BaseModel):
    """Export request model."""
    format: str  # 'json', 'csv', 'xlsx', 'pdf'
    filters: Optional[SearchQuery] = None
    fields: Optional[List[str]] = None
    template: Optional[str] = None

class ExportResponse(BaseModel):
    """Export response model."""
    export_id: str
    status: ProcessingStatus
    format: str
    file_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

# Notification models
class NotificationChannel(BaseModel):
    """Notification channel model."""
    channel_id: str
    type: str  # 'email', 'sms', 'webhook', 'slack'
    configuration: Dict[str, Any]
    enabled: bool = True

class NotificationTemplate(BaseModel):
    """Notification template model."""
    template_id: str
    name: str
    subject: Optional[str] = None
    body: str
    variables: List[str] = []
    channel_type: str

class NotificationRequest(BaseModel):
    """Notification request model."""
    template_id: str
    channel_ids: List[str]
    variables: Dict[str, Any] = {}
    priority: Priority = Priority.MEDIUM
    scheduled_at: Optional[datetime] = None

# Batch operation models
class BatchOperation(BaseModel):
    """Batch operation model."""
    operation_id: str
    operation_type: str
    items: List[str]  # List of item IDs
    parameters: Dict[str, Any] = {}
    status: ProcessingStatus = ProcessingStatus.QUEUED
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class BatchResult(BaseModel):
    """Batch operation result model."""
    operation_id: str
    total_items: int
    processed_items: int
    successful_items: int
    failed_items: int
    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
