"""
Operations Analytics Schemas

Pydantic models for analytics API responses
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TimeRange(str, Enum):
    """Time range options for analytics"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"


class KPIMetric(BaseModel):
    """Individual KPI metric with trend"""
    value: float = Field(..., description="Current value of the metric")
    change: float = Field(..., description="Percentage change from previous period")
    trend: str = Field(..., description="Trend direction: 'up' or 'down'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "value": 1247,
                "change": 12.5,
                "trend": "up"
            }
        }


class AnalyticsKPIResponse(BaseModel):
    """KPI metrics response"""
    total_bookings: KPIMetric = Field(..., description="Total bookings count")
    total_revenue: KPIMetric = Field(..., description="Total revenue in INR")
    active_complaints: KPIMetric = Field(..., description="Active complaints count")
    avg_resolution_time: KPIMetric = Field(..., description="Average resolution time in hours")
    customer_satisfaction: KPIMetric = Field(..., description="Customer satisfaction score (0-5)")
    staff_utilization: KPIMetric = Field(..., description="Staff utilization percentage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_bookings": {"value": 1247, "change": 12.5, "trend": "up"},
                "total_revenue": {"value": 89450, "change": 8.3, "trend": "up"},
                "active_complaints": {"value": 23, "change": -15.2, "trend": "down"},
                "avg_resolution_time": {"value": 4.2, "change": -10.5, "trend": "down"},
                "customer_satisfaction": {"value": 4.6, "change": 5.2, "trend": "up"},
                "staff_utilization": {"value": 87, "change": 3.1, "trend": "up"}
            }
        }


class TrendDataPoint(BaseModel):
    """Single data point in trend chart"""
    date: str = Field(..., description="Date label (e.g., 'Mon', '2024-01-15')")
    bookings: int = Field(..., description="Number of bookings")
    revenue: float = Field(..., description="Revenue amount")
    complaints: int = Field(..., description="Number of complaints")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "Mon",
                "bookings": 45,
                "revenue": 3200,
                "complaints": 5
            }
        }


class AnalyticsTrendResponse(BaseModel):
    """Trend data response"""
    data: List[TrendDataPoint] = Field(..., description="List of trend data points")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {"date": "Mon", "bookings": 45, "revenue": 3200, "complaints": 5},
                    {"date": "Tue", "bookings": 52, "revenue": 3800, "complaints": 3}
                ]
            }
        }


class CategoryData(BaseModel):
    """Service category data"""
    name: str = Field(..., description="Category name")
    value: int = Field(..., description="Number of bookings")
    percentage: float = Field(..., description="Percentage of total")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Cleaning",
                "value": 450,
                "percentage": 36.0
            }
        }


class AnalyticsCategoryResponse(BaseModel):
    """Category distribution response"""
    data: List[CategoryData] = Field(..., description="List of category data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {"name": "Cleaning", "value": 450, "percentage": 36.0},
                    {"name": "Plumbing", "value": 320, "percentage": 26.0}
                ]
            }
        }


class StatusData(BaseModel):
    """Booking status data"""
    name: str = Field(..., description="Status name")
    value: int = Field(..., description="Number of bookings")
    color: str = Field(..., description="Color code for visualization")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Completed",
                "value": 856,
                "color": "#10B981"
            }
        }


class AnalyticsStatusResponse(BaseModel):
    """Status distribution response"""
    data: List[StatusData] = Field(..., description="List of status data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {"name": "Completed", "value": 856, "color": "#10B981"},
                    {"name": "In Progress", "value": 234, "color": "#3B82F6"}
                ]
            }
        }


class PerformanceMetric(BaseModel):
    """Performance metric with target"""
    metric: str = Field(..., description="Metric name")
    current: float = Field(..., description="Current value")
    target: float = Field(..., description="Target value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric": "Response Time",
                "current": 85.0,
                "target": 90.0
            }
        }


class AnalyticsPerformanceResponse(BaseModel):
    """Performance metrics response"""
    data: List[PerformanceMetric] = Field(..., description="List of performance metrics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {"metric": "Response Time", "current": 85.0, "target": 90.0},
                    {"metric": "Resolution Rate", "current": 92.0, "target": 95.0}
                ]
            }
        }

