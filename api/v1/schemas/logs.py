# -*- coding: utf-8 -*-
"""
===================================
日志文件相关模型
===================================

职责：
1. 定义日志文件列表和详情模型
"""

from typing import Optional, List, Any

from pydantic import BaseModel, Field


class LogItem(BaseModel):
    """历史记录摘要（列表展示用）"""
    
    file_name: str = Field(..., description="日志文件名")
    file_size: str = Field(..., description="文件大小")
    created_at: Optional[str] = Field(None, description="创建时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_name": "abc123",
                "file_size": "123",
                "created_at": "2025-01-01T12:00:00"
            }
        }


class LogsListResponse(BaseModel):
    """历史记录列表响应"""
    
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    items: List[LogItem] = Field(default_factory=list, description="记录列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "limit": 20,
                "items": []
            }
        }

class LogDetail(BaseModel):
    """日志明细"""
    
    file_name: str = Field(..., description="文件名")
    content: List[str] = Field(..., description="内容")
    pointer: int = Field(..., description="起始行数")

