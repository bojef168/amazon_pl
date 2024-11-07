"""
数据预处理模块
功能：清洗和标准化评论数据，为后续分析做准备
"""
import pandas as pd
import numpy as np
import re
import spacy
from typing import Dict, List
from textblob import TextBlob
import warnings
warnings.filterwarnings('ignore')

# 添加异常类定义
class DataProcessingError(Exception):
    """数据处理过程中的异常"""
    pass


class DataProcessor:
    def __init__(self):
        """初始化数据处理器"""
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            import os
            os.system('python -m spacy download en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')

        # 加载停用词
        self.stop_words = set(self.nlp.Defaults.stop_words)

        # 定义要保留的标点符号
        self.keep_punctuation = {'.', '!', '?', ','}

        # 定义常见的拼写错误修正
        self.spelling_corrections = {
            'dont': "don't",
            'cant': "can't",
            'wont': "won't",
            'isnt': "isn't",
            # 可以根据需要添加更多
        }

    def load_data(self, file_path: str, nrows: int = None) -> pd.DataFrame:
        """
        加载数据文件

        参数:
            file_path: 文件路径
            nrows: 要读取的行数（可选，用于测试）
        返回:
            pd.DataFrame: 加载的数据
        """
        try:
            # 根据文件类型读取数据
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, nrows=nrows)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=nrows)
            else:
                raise DataProcessingError("Unsupported file format")

            # 确保必要的列存在
            required_columns = {'评论人', '内容', '评论时间'}  # 修改这里，将'评论日期'改为'评论时间'
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                raise ValueError(f"数据文件缺少必要的列: {missing_columns}")

            # 删除完全重复的行
            df = df.drop_duplicates()

            # 重置索引
            df = df.reset_index(drop=True)

            # 打印加载信息
            print(f"成功加载 {len(df)} 条评论数据")
            print(f"数据列: {df.columns.tolist()}")

            return df

        except Exception as e:
            raise DataProcessingError(f"加载数据文件时出错: {str(e)}")

    def preprocess_text(self, text: str) -> str:
        """
        预处理文本

        参数:
            text: 原始文本
        返回:
            str: 处理后的文本
        """
        if pd.isna(text):
            return ""

        # 转换为小写
        text = text.lower()

        # 修正常见拼写错误
        for wrong, correct in self.spelling_corrections.items():
            text = re.sub(r'\b' + wrong + r'\b', correct, text)

        # 去除URL
        text = re.sub(r'http\S+|www.\S+', '', text)

        # 去除邮箱
        text = re.sub(r'\S+@\S+', '', text)

        # 去除多余的空白字符
        text = re.sub(r'\s+', ' ', text)

        # 去除不需要的标点符号
        text = ''.join(char for char in text if char.isalnum() or
                      char.isspace() or char in self.keep_punctuation)

        return text.strip()

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理整个DataFrame

        参数:
            df: 原始DataFrame
        返回:
            pd.DataFrame: 处理后的DataFrame
        """
        from tqdm.auto import tqdm
        tqdm.pandas()  # 初始化 tqdm 的 pandas 支持

        # 创建副本以避免修改原始数据
        processed_df = df.copy()

        # 处理内容
        processed_df['内容'] = processed_df['内容'].progress_apply(self.preprocess_text)

        # 删除内容为空的行
        processed_df = processed_df.dropna(subset=['内容'])

        # 添加额外的特征
        print("计算基础特征...")
        processed_df['评论长度'] = processed_df['内容'].str.len()
        processed_df['词数'] = processed_df['内容'].str.split().str.len()

        # 添加基础情感分数
        print("分析情感倾向...")
        processed_df['情感分数'] = processed_df['内容'].progress_apply(self._get_sentiment_score)

        # 提取关键词
        print("提取关键词...")
        processed_df['关键词'] = processed_df['内容'].progress_apply(self._extract_keywords)

        return processed_df

    def _get_sentiment_score(self, text: str) -> float:
        """
        获取文本的情感分数

        参数:
            text: 文本内容
        返回:
            float: 情感分数 (-1到1之间)
        """
        try:
            return TextBlob(text).sentiment.polarity
        except:
            return 0.0

    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        提取文本中的关键词

        参数:
            text: 文本内容
            max_keywords: 最大关键词数量
        返回:
            List[str]: 关键词列表
        """
        doc = self.nlp(text)

        # 提取名词和形容词短语
        keywords = []
        for token in doc:
            if token.pos_ in {'NOUN', 'ADJ'} and token.text not in self.stop_words:
                # 获取完整的短语
                phrase = ' '.join([t.text for t in token.subtree
                                 if not t.is_stop and not t.is_punct])
                if phrase:
                    keywords.append(phrase)

        # 去重并限制数量
        keywords = list(set(keywords))[:max_keywords]

        return keywords

    def generate_summary_stats(self, df: pd.DataFrame) -> Dict:
        """
        生成数据摘要统计

        参数:
            df: 处理后的DataFrame
        返回:
            Dict: 统计信息
        """
        stats = {
            '评论总数': len(df),
            '平均评论长度': df['评论长度'].mean(),
            '平均词数': df['词数'].mean(),
            '情感分布': {
                '正面': len(df[df['情感分数'] > 0]),
                '中性': len(df[df['情感分数'] == 0]),
                '负面': len(df[df['情感分数'] < 0])
            },
            '最常见关键词': self._get_top_keywords(df['关键词'])
        }

        return stats

    def _get_top_keywords(self, keywords_series: pd.Series, top_n: int = 10) -> Dict[str, int]:
        """
        获取最常见的关键词

        参数:
            keywords_series: 关键词Series
            top_n: 返回的关键词数量
        返回:
            Dict[str, int]: {关键词: 出现次数}
        """
        # 展平所有关键词列表
        all_keywords = [keyword for keywords in keywords_series for keyword in keywords]

        # 统计频率
        keyword_freq = pd.Series(all_keywords).value_counts()

        return keyword_freq.head(top_n).to_dict()
"""
数据加载和验证：
读取Excel文件
验证必要列的存在
去除重复数据
文本清洗：
统一大小写
修正拼写错误
去除URL和邮箱
规范化标点符号
特征提取：
计算评论长度和词数
添加情感分数
提取关键词
数据统计：
生成基础统计信息
分析情感分布
统计高频关键词
"""