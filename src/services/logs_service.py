# -*- coding: utf-8 -*-
"""
===================================
历史查询服务层
===================================

职责：
1. 封装历史记录查询逻辑
2. 提供分页和筛选功能
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

from src.services.system_config_service import SystemConfigService

logger = logging.getLogger(__name__)


class LogsService:
    """
    历史查询服务
    
    封装历史分析记录的查询逻辑
    """
    
    def __init__(self):
        """
        初始化历史查询服务
        """
        self.system_config_service = SystemConfigService()
    
    def get_logs_list(
        self,
        file_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        获取历史分析列表
        
        Args:
            file_name: 股票代码筛选
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            page: 页码
            limit: 每页数量
            
        Returns:
            包含 total, items 的字典
        """
        try:
            # 解析日期参数
            start_dt = None
            end_dt = None
            
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                except ValueError:
                    logger.warning(f"无效的 start_date 格式: {start_date}")
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                except ValueError:
                    logger.warning(f"无效的 end_date 格式: {end_date}")
            
            # 计算 offset
            offset = (page - 1) * limit
            
            # 使用新的分页查询方法
            # records, total = self.db.get_analysis_history_paginated(
            #     code=file_name,
            #     start_date=start_dt,
            #     end_date=end_dt,
            #     offset=offset,
            #     limit=limit
            # )

            payload = self.system_config_service.get_config(include_schema=True)
            items = {item["key"]: item for item in payload["items"]}
            log_dir = items["LOG_DIR"]["value"]
            log_path = Path(log_dir)
            """read files under this path and find the latest one"""
            log_files = [f for f in log_path.iterdir() if f.is_file()]
            # 列出所有文件名，文件大小（单位MB）和创建日期（格式YYYY-MM-dd HH:mm:ss）
            # 列出所有文件名，文件大小（单位MB）和创建日期
            # log_files = [(f.name, f.stat().st_size / 1024 / 1024, datetime.fromtimestamp(f.stat().st_mtime)) for f in log_path.iterdir() if f.is_file()]
            # if log_files:
            #     # 列出所有文件名，文件大小（单位MB）和创建日期（格式YYYY-MM-dd HH:mm:ss）
            #     # log_files = [(f.name, f.stat().st_mtime) for f in log_files]
            #     # log_files = [f for f in log_files if f.stat().st_mtime > (datetime.now() - timedelta(days=7)).timestamp()]
            #
            #     latest_file = max(log_files, key=lambda f: f.stat().st_mtime)
            #     logger.info(f"[AnalysisService] start to read log file: {str(latest_file)}")
            #
            #     """read log file and get last 100 lines"""
            #     with open(latest_file, "r", encoding="utf-8") as f:
            #         lines = f.readlines()[-limit:]
            #         # log_content = "".join(lines)
            #         logger.info(f"[AnalysisService] end to read log file: {str(latest_file)}")
            #     log_content = str(lines)

            # 转换为响应格式
            items = []
            for record in log_files:
                items.append({
                    "file_name": record.name,
                    "file_size": str(round(record.stat().st_size / 1024 / 1024, 2)),
                    "created_at": datetime.fromtimestamp(record.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                })

            # items sort by created_at desc
            items.sort(key=lambda x: x["created_at"], reverse=True)
            return {
                "total": items.count(self),
                "items": items,
            }
            
        except Exception as e:
            logger.error(f"查询日志列表失败: {e}", exc_info=True)
            return {"total": 0, "items": []}
    
    def get_log_detail(self, file_name: str, pointer: int) -> Optional[Dict[str, Any]]:
        """
        获取历史报告详情
        
        Args:
            file_name: 分析记录唯一标识
            
        Returns:
            完整的分析报告字典，不存在返回 None
        """
        try:
            payload = self.system_config_service.get_config(include_schema=True)
            items = {item["key"]: item for item in payload["items"]}
            log_dir = items["LOG_DIR"]["value"]
            log_path = Path(log_dir)

            limit = 1000

            """read log file and get last 1000 lines"""
            records = []
            file_path = log_path / file_name
            # 获取file_path文件的总行数
            total_lines = get_total_lines(str(file_path))
            pages = (total_lines + limit - 1) // limit
            with open(file_path, "r", encoding="utf-8") as f:
                records = f.readlines()[-limit:]
                # log_content = "".join(lines)
            # log_content = str(records)
            
            if not records:
                return None
            
            return {
                "file_name": file_name,
                "content": records,
                "pointer": pointer,
                "pages": pages,
            }
            
        except Exception as e:
            logger.error(f"查询历史详情失败: {e}", exc_info=True)
            return None


def get_total_lines(file_path: str) -> int:
    """
    获取文件的总行数

    Args:
        file_path: 文件路径

    Returns:
        文件总行数
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception as e:
        logger.error(f"读取文件行数失败: {e}", exc_info=True)
        return 0

