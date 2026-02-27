# -*- coding: utf-8 -*-
"""
===================================
历史记录相关模型
===================================

职责：
1. 定义历史记录列表和详情模型
2. 定义分析报告完整模型
"""

from typing import Optional, List, Any

from pydantic import BaseModel, Field


class LogItem(BaseModel):
    """历史记录摘要（列表展示用）"""
    
    file_name: str = Field(..., description="日志文件名")
    file_size: str = Field(..., description="股票代码")
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


class NewsIntelItem(BaseModel):
    """新闻情报条目"""

    title: str = Field(..., description="新闻标题")
    snippet: str = Field("", description="新闻摘要（最多200字）")
    url: str = Field(..., description="新闻链接")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "公司发布业绩快报，营收同比增长 20%",
                "snippet": "公司公告显示，季度营收同比增长 20%...",
                "url": "https://example.com/news/123"
            }
        }


class NewsIntelResponse(BaseModel):
    """新闻情报响应"""

    total: int = Field(..., description="新闻条数")
    items: List[NewsIntelItem] = Field(default_factory=list, description="新闻列表")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "items": []
            }
        }


class ReportMeta(BaseModel):
    """报告元信息"""
    
    file_name: str = Field(..., description="分析记录唯一标识")
    file_size: str = Field(..., description="股票代码")
    stock_name: Optional[str] = Field(None, description="股票名称")
    report_type: Optional[str] = Field(None, description="报告类型")
    created_at: Optional[str] = Field(None, description="创建时间")
    current_price: Optional[float] = Field(None, description="分析时股价")
    change_pct: Optional[float] = Field(None, description="分析时涨跌幅(%)")


class ReportSummary(BaseModel):
    """报告概览区"""
    
    analysis_summary: Optional[str] = Field(None, description="关键结论")
    operation_advice: Optional[str] = Field(None, description="操作建议")
    trend_prediction: Optional[str] = Field(None, description="趋势预测")
    sentiment_score: Optional[int] = Field(
        None, 
        description="情绪评分 (0-100)",
        ge=0,
        le=100
    )
    sentiment_label: Optional[str] = Field(None, description="情绪标签")


class ReportStrategy(BaseModel):
    """策略点位区"""
    
    ideal_buy: Optional[str] = Field(None, description="理想买入价")
    secondary_buy: Optional[str] = Field(None, description="第二买入价")
    stop_loss: Optional[str] = Field(None, description="止损价")
    take_profit: Optional[str] = Field(None, description="止盈价")


class ReportDetails(BaseModel):
    """报告详情区"""
    
    news_content: Optional[str] = Field(None, description="新闻摘要")
    raw_result: Optional[Any] = Field(None, description="原始分析结果（JSON）")
    context_snapshot: Optional[Any] = Field(None, description="分析时上下文快照（JSON）")


class LogDetail(BaseModel):
    """日志明细"""
    
    file_name: str = Field(..., description="文件名")
    content: List[str] = Field(..., description="内容")
    pointer: int = Field(..., description="起始行数")
    pages: int = Field(..., description="总页数")

