"""
基础分析器
功能：定义所有维度共用的基础分析功能，包括趋势分析和交叉分析
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
import pandas as pd
import logging
import os
from ..utils.text_processor import TextProcessor
from ..utils.sentiment_analyzer import SentimentAnalyzer
from ..utils.insight_generator import InsightGenerator
import spacy
import hashlib
import json
from functools import lru_cache
from pathlib import Path

# 确保日志和缓存目录存在
os.makedirs('logs', exist_ok=True)
os.makedirs('cache', exist_ok=True)

class AnalysisError(Exception):
    """基础分析异常"""
    pass

class DataValidationError(AnalysisError):
    """数据验证异常"""
    pass

class ProcessingError(AnalysisError):
    """处理过程异常"""
    pass

class ResourceError(AnalysisError):
    """资源相关异常"""
    pass

class BaseAnalyzer(ABC):
    def __init__(self):
        """初始化基础分析器"""
        try:
            # 设置日志
            self._setup_logging()
            self.logger.info("Initializing base analyzer...")

            # 初始化 NLTK 数据
            self.logger.info("Checking NLTK resources...")
            import nltk
            required_nltk_data = [
                'punkt',
                'stopwords',
                'wordnet',
                'averaged_perceptron_tagger'
            ]

            for item in required_nltk_data:
                try:
                    nltk.data.find(f'tokenizers/{item}')
                except LookupError:
                    self.logger.info(f"Downloading {item}...")
                    nltk.download(item, quiet=True)

            # 初始化工具类
            self.logger.info("Initializing utility classes...")
            self.text_processor = TextProcessor()
            self.sentiment_analyzer = SentimentAnalyzer()
            self.insight_generator = InsightGenerator()

            # 初始化 spaCy
            self.logger.info("Initializing spaCy...")
            try:
                import spacy
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                self.logger.warning("Downloading spaCy model...")
                import os
                os.system('python -m spacy download en_core_web_sm')
                self.nlp = spacy.load('en_core_web_sm')

            # 缓存设置
            self.cache_dir = Path('cache')
            self.cache_enabled = True
            self.cache_ttl = 3600  # 缓存有效期（秒）

            # 存储分析结果
            self.categories = {}
            self.analysis_metadata = {
                'start_time': None,
                'end_time': None,
                'total_samples': 0,
                'processed_samples': 0,
                'error_samples': 0,
                'error_details': []
            }

            self.logger.info("Base analyzer initialization completed")

        except Exception as e:
            self.logger.error(f"Error initializing analyzer: {str(e)}")
            raise ResourceError(f"Failed to initialize analyzer: {str(e)}")

    def _setup_logging(self):
        """设置日志"""
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # 文件处理器
            file_handler = logging.FileHandler(
                f'logs/{self.__class__.__name__}.log'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            self.logger.setLevel(logging.INFO)

    def _generate_cache_key(self, df: pd.DataFrame) -> str:
        """
        生成数据的缓存键

        参数:
            df: 评论数据DataFrame
        返回:
            str: 缓存键
        """
        try:
            # 使用更安全的方式生成缓存键
            # 1. 获取DataFrame的基本信息
            row_count = len(df)
            col_count = len(df.columns)
            column_names = '_'.join(df.columns)

            # 2. 获取数据的简单统计信息
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            stats = []
            if not numeric_cols.empty:
                stats = df[numeric_cols].mean().round(2).values.tolist()

            # 3. 组合信息生成键
            key_parts = [
                self.__class__.__name__,
                str(row_count),
                str(col_count),
                column_names,
                '_'.join(map(str, stats))
            ]

            # 4. 生成哈希值
            key_string = '_'.join(key_parts)
            hash_object = hashlib.sha256(key_string.encode())
            return hash_object.hexdigest()

        except Exception as e:
            self.logger.error(f"Failed to generate cache key: {str(e)}")
            # 如果生成缓存键失败，返回时间戳作为备用键
            return f"{self.__class__.__name__}_{datetime.now().timestamp()}"

    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """
        获取缓存的分析结果

        参数:
            cache_key: 缓存键
        返回:
            Optional[Dict]: 缓存的结果，如果没有找到则返回None
        """
        if not self.cache_enabled:
            return None

        cache_file = self.cache_dir / f"{self.__class__.__name__}_{cache_key}.json"

        try:
            if cache_file.exists():
                # 检查缓存是否过期
                if (datetime.now().timestamp() - cache_file.stat().st_mtime) > self.cache_ttl:
                    self.logger.info("Cache expired, removing old file")
                    cache_file.unlink()
                    return None

                with cache_file.open('r', encoding='utf-8') as f:
                    self.logger.info("Using cached result")
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Error reading cache: {str(e)}")
            return None

        return None

    def _save_to_cache(self, cache_key: str, results: Dict) -> None:
        """
        保存结果到缓存

        参数:
            cache_key: 缓存键
            results: 分析结果
        """
        if not self.cache_enabled:
            return

        cache_file = self.cache_dir / f"{self.__class__.__name__}_{cache_key}.json"

        try:
            # 处理 datetime 对象
            def process_dict(d: Dict) -> Dict:
                processed = {}
                for key, value in d.items():
                    if isinstance(value, datetime):
                        processed[key] = value.isoformat()
                    elif isinstance(value, dict):
                        processed[key] = process_dict(value)
                    elif isinstance(value, list):
                        processed[key] = [
                            item.isoformat() if isinstance(item, datetime) else item
                            for item in value
                        ]
                    else:
                        processed[key] = value
                return processed

            processed_results = process_dict(results)

            with cache_file.open('w', encoding='utf-8') as f:
                json.dump(processed_results, f, ensure_ascii=False, indent=2)
            self.logger.info("Results saved to cache")
        except Exception as e:
            self.logger.warning(f"Error saving to cache: {str(e)}")

    def _clean_old_cache(self) -> None:
        """清理过期的缓存文件"""
        if not self.cache_enabled:
            return

        try:
            current_time = datetime.now().timestamp()
            for cache_file in self.cache_dir.glob(f"{self.__class__.__name__}_*.json"):
                if (current_time - cache_file.stat().st_mtime) > self.cache_ttl:
                    cache_file.unlink()
                    self.logger.info(f"Removed expired cache file: {cache_file.name}")
        except Exception as e:
            self.logger.warning(f"Error cleaning cache: {str(e)}")

    def _validate_data(self, df: pd.DataFrame) -> None:
        """验证输入数据的有效性"""
        if df is None or len(df) == 0:
            raise DataValidationError("Empty or null DataFrame provided")

        # 检查必需的列
        required_columns = {'评论人', '内容', '评论时间'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise DataValidationError(f"Missing required columns: {missing_columns}")

        # 检查空值
        null_counts = df[list(required_columns)].isnull().sum()
        if null_counts.any():
            self.logger.warning(f"Found null values in columns: {null_counts[null_counts > 0]}")

    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        通用分析流程

        参数:
            df: 包含评论数据的DataFrame
        返回:
            Dict: 分析结果
        """
        try:
            # 保存 df 作为实例属性
            self.df = df

            # 数据验证
            self._validate_data(df)

            # 清理旧缓存
            self._clean_old_cache()

            # 检查缓存
            cache_key = self._generate_cache_key(df)
            cached_result = self._get_cached_result(cache_key)
            if cached_result is not None:
                self.logger.info("Using cached analysis result")
                return cached_result

            self.analysis_metadata['start_time'] = datetime.now()
            self.analysis_metadata['total_samples'] = len(df)

            # 1. 提取评论中的主要类别
            self.logger.info("Extracting categories...")
            try:
                self.categories = self._extract_categories(df)
            except Exception as e:
                raise ProcessingError(f"Category extraction failed: {str(e)}")

            # 2. 统计每个类别的提及次数和示例
            self.logger.info("Counting mentions...")
            try:
                mention_results = self._count_mentions(df)
            except Exception as e:
                raise ProcessingError(f"Mention counting failed: {str(e)}")

            # 3. 情感分析
            self.logger.info("Analyzing sentiment...")
            try:
                sentiment_results = self._analyze_sentiment(df, mention_results)
            except Exception as e:
                raise ProcessingError(f"Sentiment analysis failed: {str(e)}")

            # 4. 趋势分析
            self.logger.info("Analyzing trends...")
            try:
                trend_results = self._analyze_trends(df, sentiment_results)
            except Exception as e:
                raise ProcessingError(f"Trend analysis failed: {str(e)}")

            # 5. 生成洞察
            self.logger.info("Generating insights...")
            try:
                final_results = self._generate_insights(trend_results)
            except Exception as e:
                raise ProcessingError(f"Insight generation failed: {str(e)}")

            # 确保所有类别和关键词都是字符串类型
            processed_results = {
                'total': len(df),
                'categories': {},
                'metadata': self.analysis_metadata
            }

            for category, data in final_results.get('categories', {}).items():
                category_str = str(category)
                processed_results['categories'][category_str] = {
                    'count': int(data.get('mention_count', 0)),
                    'percentage': float(data.get('percentage', 0)),
                    'examples': [str(ex) for ex in data.get('examples', [])],
                    'sentiment': {
                        k: int(v) for k, v in data.get('sentiment', {}).items()
                    },
                    'keywords': [str(kw) for kw in data.get('keywords', [])],
                    'trend': data.get('trend', {})
                }

            self.analysis_metadata['end_time'] = datetime.now()
            self.analysis_metadata['processed_samples'] = len(df)
            processed_results['metadata'] = self.analysis_metadata

            # 保存结果到缓存
            self._save_to_cache(cache_key, processed_results)

            return processed_results

        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            self.analysis_metadata['error_details'].append({
                'timestamp': datetime.now(),
                'error_type': type(e).__name__,
                'error_message': str(e)
            })
            self.analysis_metadata['error_samples'] += 1
            raise

    def _count_mentions(self, df: pd.DataFrame) -> Dict:
        """
        统计各个类别的提及次数和示例

        参数:
            df: 评论数据DataFrame
        返回:
            Dict: {
                'category_name': {
                    'mention_count': int,
                    'percentage': float,
                    'examples': List[str]
                }
            }
        """
        try:
            results = {}
            total_reviews = len(df)

            for category, keywords in self.categories.items():
                mentions = 0
                examples = []

                for _, row in df.iterrows():
                    try:
                        text = f"{row['标题']} {row['内容']}"
                        if self.text_processor.extract_keywords(text, keywords):
                            mentions += 1
                            if len(examples) < 3:  # 每个类别保存最多3个示例
                                examples.append(text)
                    except Exception as e:
                        self.logger.warning(f"Error processing row: {str(e)}")
                        continue

                if mentions > 0:
                    results[category] = {
                        'mention_count': mentions,
                        'percentage': (mentions / total_reviews) * 100,
                        'examples': examples
                    }

            return results
        except Exception as e:
            raise ProcessingError(f"Error counting mentions: {str(e)}")

    def _analyze_sentiment(self, df: pd.DataFrame, mention_results: Dict) -> Dict:
        """分析情感倾向"""
        try:
            results = mention_results.copy()

            # 跳过metadata键
            categories = {k: v for k, v in results.items() if k != 'metadata'}

            for category, data in categories.items():
                if 'examples' in data:
                    category_texts = df[df['内容'].isin(data['examples'])]['内容']
                    if not category_texts.empty:
                        sentiments = [
                            self.sentiment_analyzer.analyze_sentiment(text)['polarity']
                            for text in category_texts
                        ]
                        data['sentiment'] = {
                            'mean': sum(sentiments) / len(sentiments),
                            'positive': len([s for s in sentiments if s > 0]),
                            'negative': len([s for s in sentiments if s < 0]),
                            'neutral': len([s for s in sentiments if s == 0])
                        }

            return results
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {str(e)}")
            return mention_results

    def _analyze_trends(self, df: pd.DataFrame, current_results: Dict) -> Dict:
        """
        分析时间趋势

        参数:
            df: 数据DataFrame
            current_results: 当前的分析结果
        返回:
            Dict: 添加了趋势分析的结果
        """
        try:
            # 确保数据中有时间列
            date_column = '评论时间'  # 修改为实际的时间列名
            if date_column not in df.columns:
                self.logger.warning(f"No date column '{date_column}' found for trend analysis")
                return current_results

            # 转换日期格式
            df['date'] = pd.to_datetime(df[date_column])

            # 为每个类别分析趋势
            for category, data in current_results.items():
                if category == 'metadata':
                    continue

                # 获取该类别的评论
                category_df = df[df['内容'].isin(data.get('examples', []))]

                if not category_df.empty:
                    # 按时间分组统计
                    time_series = category_df.set_index('date').resample('D').size()

                    # 计算变化率
                    if len(time_series) > 1:
                        change_rate = (
                            (time_series[-1] - time_series[0]) / time_series[0]
                            if time_series[0] != 0 else 0
                        )
                    else:
                        change_rate = 0

                    # 添加趋势信息
                    data['trend'] = {
                        'time_series': time_series.to_dict(),
                        'change_rate': change_rate,
                        'trend_direction': 'increasing' if change_rate > 0.1
                        else 'decreasing' if change_rate < -0.1
                        else 'stable'
                    }

            return current_results

        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            return current_results

    def _generate_insights(self, trend_results: Dict) -> Dict:
        """
        生成基础分析洞察

        参数:
            trend_results: 趋势分析结果
        返回:
            Dict: 包含基础分析洞察的字典
        """
        try:
            insights = {
                'summary': {
                    'total_reviews': len(self.df),
                    'analyzed_items': len(self.df[self.df['内容'].notna()]),
                },
                'sentiment': {
                    'positive_ratio': (self.df['情感分数'] > 0).mean() if '情感分数' in self.df.columns else 0,
                    'negative_ratio': (self.df['情感分数'] < 0).mean() if '情感分数' in self.df.columns else 0,
                    'neutral_ratio': (self.df['情感分数'] == 0).mean() if '情感分数' in self.df.columns else 0,
                },
                'categories': getattr(self, 'category_counts', {}),
                'trends': trend_results or {},
                'key_metrics': {
                    'avg_length': self.df['内容'].str.len().mean() if '内容' in self.df.columns else 0,
                    'keyword_frequency': getattr(self, 'keyword_freq', {})
                }
            }
            return insights

        except Exception as e:
            self.logger.warning(f"Error generating insights: {str(e)}")
            return {
                'error': str(e),
                'summary': {'total_reviews': 0},
                'sentiment': {},
                'categories': {},
                'trends': {},
                'key_metrics': {}
            }

    def _calculate_category_trend(
            self,
            df: pd.DataFrame,
            category: str,
            category_data: Dict
    ) -> Dict:
        """
        计算单个类别的趋势

        参数:
            df: 数据DataFrame
            category: 类别名称
            category_data: 类别数据
        返回:
            Dict: 趋势数据
        """
        try:
            # 按时间分组统计
            df['date'] = pd.to_datetime(df['date'])
            time_series = df.set_index('date').resample('M').size()

            # 计算变化率
            if len(time_series) > 1:
                change_rate = (
                    (time_series[-1] - time_series[0]) / time_series[0]
                    if time_series[0] != 0 else 0
                )
            else:
                change_rate = 0

            return {
                'time_series': time_series.to_dict(),
                'change_rate': change_rate,
                'trend_direction': 'increasing' if change_rate > 0.1
                else 'decreasing' if change_rate < -0.1
                else 'stable'
            }
        except Exception as e:
            raise ProcessingError(f"Error calculating trend: {str(e)}")

    def cross_analyze(
            self,
            df: pd.DataFrame,
            other_analyzer: 'BaseAnalyzer'
    ) -> Dict:
        """
        与其他维度进行交叉分析

        参数:
            df: 数据DataFrame
            other_analyzer: 另一个分析器实例
        返回:
            Dict: 交叉分析结果
        """
        try:
            # 获取两个维度的分析结果
            this_results = self.analyze(df)
            other_results = other_analyzer.analyze(df)

            # 计算维度间的关联
            correlations = self._calculate_correlations(
                this_results,
                other_results,
                df
            )

            return {
                'dimension1': self.__class__.__name__,
                'dimension2': other_analyzer.__class__.__name__,
                'correlations': correlations,
                'insights': self._generate_cross_insights(correlations)
            }

        except Exception as e:
            self.logger.error(f"Cross analysis failed: {str(e)}")
            raise AnalysisError(f"Cross analysis failed: {str(e)}")

    def _calculate_correlations(
            self,
            results1: Dict,
            results2: Dict,
            df: pd.DataFrame
    ) -> List[Dict]:
        """
        计算两个维度间的关联关系

        参数:
            results1: 第一个维度的结果
            results2: 第二个维度的结果
            df: 原始数据
        返回:
            List[Dict]: 关联关系列表
        """
        try:
            correlations = []

            for cat1 in results1.keys():
                if cat1 == 'metadata':
                    continue

                for cat2 in results2.keys():
                    if cat2 == 'metadata':
                        continue

                    try:
                        correlation = self._calculate_single_correlation(
                            cat1,
                            cat2,
                            results1[cat1],
                            results2[cat2],
                            df
                        )

                        if correlation['strength'] > 0.1:  # 只保留显著的关联
                            correlations.append(correlation)
                    except Exception as e:
                        self.logger.warning(
                            f"Error calculating correlation for {cat1}-{cat2}: {str(e)}"
                        )
                        continue

            return correlations
        except Exception as e:
            raise ProcessingError(f"Error calculating correlations: {str(e)}")

    def _calculate_single_correlation(
            self,
            cat1: str,
            cat2: str,
            data1: Dict,
            data2: Dict,
            df: pd.DataFrame
    ) -> Dict:
        """
        计算两个类别间的具体关联关系

        参数:
            cat1: 第一个类别
            cat2: 第二个类别
            data1: 第一个类别的数据
            data2: 第二个类别的数据
            df: 原始数据
        返回:
            Dict: 关联关系
        """
        try:
            # 计算共现频率
            cooccurrence = len(
                set(data1.get('examples', [])) &
                set(data2.get('examples', []))
            )

            # 计算关联强度
            strength = cooccurrence / (
                    len(data1.get('examples', [])) +
                    len(data2.get('examples', [])) +
                    1e-10
            )

            return {
                'category1': cat1,
                'category2': cat2,
                'cooccurrence': cooccurrence,
                'strength': strength,
                'type': 'positive' if strength > 0.3 else 'weak'
            }
        except Exception as e:
            raise ProcessingError(f"Error calculating correlation: {str(e)}")

    @abstractmethod
    def _extract_categories(self, df: pd.DataFrame) -> Dict[str, Set[str]]:
        """
        从评论中提取主要类别和关键词
        这是一个抽象方法，需要由具体的分析器实现

        参数:
            df: 评论数据DataFrame
        返回:
            Dict[str, Set[str]]: {类别名称: {相关关键词集合}}
        抛出:
            ProcessingError: 当类别提取失败时
        """
        raise NotImplementedError("Subclasses must implement _extract_categories")