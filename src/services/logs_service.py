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
            # return sublist of items, start from (page-1)*limit, end to page*limit
            total = items.__len__()
            items = items[(page - 1) * limit:page * limit]
            return {
                "total": total,
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
            明细，不存在返回 None
        """
        try:
            payload = self.system_config_service.get_config(include_schema=True)
            items = {item["key"]: item for item in payload["items"]}
            log_dir = items["LOG_DIR"]["value"]
            log_path = Path(log_dir)

            limit = 100

            """read log file and get last 1000 lines"""
            records = []
            file_path = log_path / file_name

            if not file_path.exists() or pointer < 0:
                return None

            # 获取总行数计算总页数
            file_path = str(file_path)
            total_lines = get_total_lines(file_path)
            # pages = (total_lines + limit - 1) // limit if total_lines > 0 else 1
            
            # 使用 helper 函数获取指定页的内容
            # records = get_last_lines(str(file_path), limit, pointer)
            
            isBigFile = is_big_file(file_path)
            if isBigFile:
                rrb = list(read_reverse_bigfile(file_path))
                with open(file_path, encoding='utf-8') as f:
                    orl = f.readlines()
                print(len(orl))
            else:
                records = read_reverse(file_path, limit, pointer)
                if pointer == 0:
                    pointer = total_lines - limit
                else:
                    pointer = pointer - limit

            if not records:
                return None
            
            # 反转记录以保持时间倒序
            records.reverse()

            return {
                "file_name": file_name,
                "content": records,
                "pointer": pointer,
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

def is_big_file(file_path: str) -> bool:
    """
    判断文件是否大于 100M
    
    Args:
        file_path: 文件路径
        
    Returns:
        True: 文件大于 100M
        False: 文件小于 100M
    """
    try:
        file_size = os.path.getsize(file_path)
        return file_size > 100 * 1024 * 1024
    except Exception as e:
        logger.error(f"判断文件大小失败: {e}", exc_info=True)

def read_reverse(file_path: str, limit: int, pointer: int) -> List[str]:
    """
    获取文件末尾指定页的行内容
    
    Args:
        file_path: 文件路径
        limit: 每页行数
        pointer: 起始位置
        
    Returns:
        行内容列表
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            
        total = len(all_lines)
        if total == 0:
            return []

        if pointer == 0:
            pointer = total
        
        # 计算切片索引
        start_idx = pointer - limit
        end_idx = pointer
        
        # 边界处理
        if start_idx < 0:
            start_idx = 0
        if end_idx > total:
            end_idx = total
            
        if start_idx >= end_idx:
            return []
            
        return all_lines[start_idx:end_idx]
        
    except Exception as e:
        logger.error(f"读取文件片段失败：{e}", exc_info=True)
        return []

def read_reverse_bigfile(filepath, encoding='utf-8', separator=b'\n', single_size=1024 * 1024):
    """
    :param filepath: 文件路径
    :param encoding: 字符编码，默认utf-8
    :param separator: 行尾分隔符，默认 '\n'
    :param single_size: 单次读取 字符量，默认 1024*1024
    :return: generator 
    """
    with open(filepath, 'rb') as f:
        try:
            f.seek(0, 2)
            position = f.tell()
            if position > single_size:
                f.seek(-single_size, 2)
            else:
                f.seek(0, 0)
        except OSError as e:
            return 'Blank file'
        line = b''
        while 1:
            chunk = f.read(single_size)
            index_list = [match.end() for match in re.finditer(separator, chunk)]
            index = None
            while index_list:
                target = index_list.pop()
                if index is None:
                    line = chunk[target:] + line
                else:
                    line = chunk[target:index] + line
                if line:
                    yield line.decode(encoding=encoding)
                line = b''
                index = target
            else:
                line = chunk[:index] + line
            position = f.tell()
            if position > 2 * single_size and single_size > 0:
                f.seek(-2 * single_size, 1)
            else:
                f.seek(0, 0)
                single_size = position - single_size
                if single_size <= 0:
                    yield line.decode(encoding=encoding)
                    return 'End'
