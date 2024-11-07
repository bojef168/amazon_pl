"""NLTK资源初始化器"""
import nltk
import logging
import time
from pathlib import Path
import ssl
from typing import List
import os

logger = logging.getLogger(__name__)

def initialize_nltk_resources(max_retries: int = 3, retry_delay: int = 2):
    """
    初始化NLTK资源，包含重试机制和离线备份

    参数:
        max_retries: 最大重试次数
        retry_delay: 重试间隔（秒）
    """
    # 需要下载的资源列表
    required_resources = [
        'punkt',
        'stopwords',
        'wordnet',
        'averaged_perceptron_tagger'
    ]

    # 设置NLTK数据目录
    nltk_data_dir = Path(os.path.expanduser('~/nltk_data'))
    nltk_data_dir.mkdir(parents=True, exist_ok=True)

    # 尝试创建SSL上下文
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    for resource in required_resources:
        retries = 0
        while retries < max_retries:
            try:
                # 检查资源是否已存在
                try:
                    nltk.data.find(f'tokenizers/{resource}')
                    logger.info(f"Resource {resource} already exists")
                    break
                except LookupError:
                    # 资源不存在，尝试下载
                    logger.info(f"Downloading {resource}...")
                    nltk.download(resource, quiet=True, raise_on_error=True)
                    logger.info(f"Successfully downloaded {resource}")
                    break

            except Exception as e:
                retries += 1
                if retries == max_retries:
                    logger.error(f"Failed to download {resource} after {max_retries} attempts: {str(e)}")
                    # 尝试使用备份方案
                    try_offline_backup(resource)
                else:
                    logger.warning(f"Attempt {retries} failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)

def try_offline_backup(resource: str):
    """
    尝试使用离线备份资源

    参数:
        resource: 资源名称
    """
    backup_dir = Path('resources/nltk_backup')
    if backup_dir.exists():
        backup_file = backup_dir / f"{resource}.zip"
        if backup_file.exists():
            try:
                # 复制备份文件到NLTK数据目录
                import shutil
                nltk_data_dir = Path(nltk.data.path[0])
                target_dir = nltk_data_dir / resource
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.unpack_archive(str(backup_file), str(target_dir))
                logger.info(f"Successfully restored {resource} from backup")
            except Exception as e:
                logger.error(f"Failed to restore {resource} from backup: {str(e)}")
        else:
            logger.error(f"No backup found for {resource}")
    else:
        logger.error("Backup directory not found")