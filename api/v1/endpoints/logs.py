# -*- coding: utf-8 -*-
"""
===================================
历史记录接口
===================================

职责：
1. 提供 GET /api/v1/logs 日志列表查询接口
2. 提供 GET /api/v1/logs/{query_id}?l=1000 日志详情查询接口
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends

from api.deps import get_database_manager
from api.v1.schemas.logs import (
    LogsListResponse,
    LogItem,
    NewsIntelItem,
    NewsIntelResponse,
    LogDetail,
    ReportMeta,
    ReportSummary,
    ReportStrategy,
    ReportDetails,
)
from api.v1.schemas.common import ErrorResponse
from src.storage import DatabaseManager
from src.services.logs_service import LogsService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=LogsListResponse,
    responses={
        200: {"description": "日志记录列表"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="获取日志列表",
    description="分页获取日志列表，支持按文件名和日期范围筛选"
)
def get_history_list(
    file_name: Optional[str] = Query(None, description="文件名筛选"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="页码（从 1 开始）"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
) -> LogsListResponse:
    """
    获取历史分析列表
    
    分页获取历史分析记录摘要，支持按股票代码和日期范围筛选
    
    Args:
        file_name: 文件名筛选
        start_date: 开始日期
        end_date: 结束日期
        page: 页码
        limit: 每页数量
        
    Returns:
        LogsListResponse: 历史记录列表
    """
    try:
        service = LogsService()
        
        # 使用 def 而非 async def，FastAPI 自动在线程池中执行
        result = service.get_logs_list(
            file_name=file_name,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )
        
        # 转换为响应模型
        items = [
            LogItem(
                file_name=item.get("file_name", ""),
                file_size=item.get("file_size"),
                created_at=item.get("created_at")
            )
            for item in result.get("items", [])
        ]
        
        return LogsListResponse(
            total=result.get("total", 0),
            page=page,
            limit=limit,
            items=items
        )
        
    except Exception as e:
        logger.error(f"查询日志列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"查询日志列表失败: {str(e)}"
            }
        )


@router.get(
    "/{file_name}",
    response_model=LogDetail,
    responses={
        200: {"description": "文件详情"},
        404: {"description": "文件不存在", "model": ErrorResponse},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="获取历史文件详情",
    description="根据 file_name 获取完整的历史分析文件"
)
def get_log_detail(
    file_name: str,
    pointer: Optional[int] = Query(None, description="开始行数")
) -> LogDetail:
    """
    获取历史文件详情
    
    根据 file_name 获取完整的历史分析文件
    
    Args:
        file_name: 分析记录唯一标识
        pointer: 分析记录唯一标识

    Returns:
        LogDetail: 完整分析文件
        
    Raises:
        HTTPException: 404 - 文件不存在
    """
    try:
        service = LogsService()

        if not pointer:
            pointer = 0
        # 使用 def 而非 async def，FastAPI 自动在线程池中执行
        result = service.get_log_detail(file_name, pointer)
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": f"未找到 file_name={file_name} 的记录"
                }
            )

        # 构建响应模型
        return LogDetail(
            file_name=result.get("file_name", ""),
            content=result.get("content", ""),
            pointer=result.get("pointer"),
            pages=result.get("pages"),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询历史详情失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"查询历史详情失败: {str(e)}"
            }
        )

