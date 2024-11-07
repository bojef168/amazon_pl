"""
文本处理工具
功能：提供文本清洗、分词、词形还原等文本处理功能
"""
import re
import nltk
from typing import List, Set, Dict
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.util import ngrams
from collections import Counter
import string
import emoji

class TextProcessor:
    def __init__(self):
        """初始化文本处理器"""
        # 确保必要的NLTK数据已下载
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            nltk.download('averaged_perceptron_tagger')

        # 初始化工具
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

        # 添加自定义停用词
        self.stop_words.update(['amazon', 'product', 'buy', 'purchased'])

        # 编译正则表达式
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self.email_pattern = re.compile(
            r'[\w\.-]+@[\w\.-]+\.\w+'
        )
        self.number_pattern = re.compile(r'\d+')

    def clean_text(
            self,
            text: str,
            remove_urls: bool = True,
            remove_emails: bool = True,
            remove_numbers: bool = False,
            remove_punctuation: bool = True,
            remove_emojis: bool = True,
            lowercase: bool = True
        ) -> str:
        """
        清理文本

        参数:
            text: 待清理文本
            remove_urls: 是否删除URL
            remove_emails: 是否删除邮箱
            remove_numbers: 是否删除数字
            remove_punctuation: 是否删除标点
            remove_emojis: 是否删除表情符号
            lowercase: 是否转换为小写
        返回:
            str: 清理后的文本
        """
        if not isinstance(text, str):
            text = str(text)

        # 删除URL
        if remove_urls:
            text = self.url_pattern.sub(' ', text)

        # 删除邮箱
        if remove_emails:
            text = self.email_pattern.sub(' ', text)

        # 删除表情符号
        if remove_emojis:
            text = emoji.replace_emoji(text, '')

        # 删除数字
        if remove_numbers:
            text = self.number_pattern.sub(' ', text)

        # 删除标点符号
        if remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))

        # 转换为小写
        if lowercase:
            text = text.lower()

        # 规范化空白字符
        text = ' '.join(text.split())

        return text

    def tokenize_text(
            self,
            text: str,
            remove_stopwords: bool = True,
            lemmatize: bool = True
        ) -> List[str]:
        """
        文本分词

        参数:
            text: 输入文本
            remove_stopwords: 是否删除停用词
            lemmatize: 是否进行词形还原
        返回:
            List[str]: 分词结果
        """
        # 分词
        tokens = word_tokenize(text)

        # 删除停用词
        if remove_stopwords:
            tokens = [t for t in tokens if t.lower() not in self.stop_words]

        # 词形还原
        if lemmatize:
            tokens = [self.lemmatizer.lemmatize(t) for t in tokens]

        return tokens

    def extract_phrases(
            self,
            text: str,
            n: int = 2,
            min_freq: int = 2
        ) -> List[str]:
        """
        提取文本中的常见短语

        参数:
            text: 输入文本
            n: n-gram大小
            min_freq: 最小频率阈值
        返回:
            List[str]: 常见短语列表
        """
        tokens = self.tokenize_text(text, remove_stopwords=True)

        # 生成n-grams
        n_grams = list(ngrams(tokens, n))

        # 统计频率
        phrase_freq = Counter(n_grams)

        # 筛选常见短语
        common_phrases = [
            ' '.join(phrase)
            for phrase, freq in phrase_freq.items()
            if freq >= min_freq
        ]

        return common_phrases

    def extract_keywords(
            self,
            text: str,
            keywords: Set[str],
            match_lemmas: bool = True
        ) -> List[str]:
        """
        从文本中提取关键词

        参数:
            text: 待分析文本
            keywords: 关键词集合
            match_lemmas: 是否匹配词形还原后的形式
        返回:
            List[str]: 匹配到的关键词列表
        """
        # 清理和分词
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize_text(cleaned_text, remove_stopwords=False)

        if match_lemmas:
            # 对关键词进行词形还原
            lemmatized_keywords = {
                self.lemmatizer.lemmatize(k.lower()) for k in keywords
            }
            # 对文本词形还原并匹配
            matched = [
                token for token in tokens
                if self.lemmatizer.lemmatize(token.lower()) in lemmatized_keywords
            ]
        else:
            # 直接匹配原形
            matched = [
                token for token in tokens
                if token.lower() in {k.lower() for k in keywords}
            ]

        return matched

    def segment_sentences(self, text: str) -> List[str]:
        """
        将文本分割为句子

        参数:
            text: 输入文本
        返回:
            List[str]: 句子列表
        """
        return sent_tokenize(text)

    def get_text_stats(self, text: str) -> Dict:
        """
        获取文本统计信息

        参数:
            text: 输入文本
        返回:
            Dict: 包含各种统计信息的字典
        """
        # 分词和分句
        tokens = self.tokenize_text(text, remove_stopwords=False)
        sentences = self.segment_sentences(text)

        # 计算统计信息
        stats = {
            'char_count': len(text),
            'word_count': len(tokens),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(t) for t in tokens) / len(tokens) if tokens else 0,
            'avg_sentence_length': len(tokens) / len(sentences) if sentences else 0,
            'unique_words': len(set(t.lower() for t in tokens)),
            'lexical_diversity': len(set(tokens)) / len(tokens) if tokens else 0
        }

        return stats

    """
    增强的文本清理：
    URL和邮箱检测与删除
    表情符号处理
    数字处理选项
    灵活的清理选项控制
    词形还原和停用词：
    使用WordNet词形还原
    可配置的停用词过滤
    自定义停用词支持
    短语提取：
    n - gram生成
    频率统计
    常用短语识别
    文本统计：
    字符数统计
    词数统计
    句子统计
    词汇多样性分析
    """