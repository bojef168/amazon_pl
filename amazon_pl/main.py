"""
主程序
功能：整合所有模块，实现完整的分析流程
"""
import argparse
import logging
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 修改导入语句
from src.utils.sentiment_analyzer import SentimentAnalyzer, SentimentAnalysisError
from src.data_processor import DataProcessor, DataProcessingError
from src.utils.insight_generator import InsightGenerator
from src.report_generator import ReportGenerator
from src.analyzers.base_analyzer import ProcessingError
from src.analyzers.user_analyzer import UserAnalyzer
from src.analyzers.timing_analyzer import TimingAnalyzer
from src.analyzers.location_analyzer import LocationAnalyzer
from src.analyzers.purpose_analyzer import PurposeAnalyzer
from src.analyzers.scenario_analyzer import ScenarioAnalyzer
from src.analyzers.motivation_analyzer import MotivationAnalyzer
from src.analyzers.experience_analyzer import ExperienceAnalyzer
from src.analyzers.design_expectation_analyzer import DesignExpectationAnalyzer


class ReviewAnalyzer:
    def __init__(self, config_path: str = 'config.yaml'):
        """初始化评论分析器"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting ReviewAnalyzer initialization...")

        # 确保只初始化一次
        self._initialized = False
        if self._initialized:
            return

        try:
            # 加载配置
            self.logger.info("Loading configuration...")
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.logger.info("Configuration loaded from config.yaml")

            # 初始化组件（使用单例模式或确保只初始化一次）
            self.logger.info("Initializing data processor...")
            self.data_processor = DataProcessor()

            self.logger.info("Initializing insight generator...")
            self.insight_generator = InsightGenerator()

            self.logger.info("Initializing report generator...")
            self.report_generator = ReportGenerator()

            # 初始化分析器
            self.logger.info("Initializing analyzers...")
            self.analyzers = self._initialize_analyzers()

            self._initialized = True
            self.logger.info("ReviewAnalyzer initialization completed successfully")

        except Exception as e:
            self.logger.error(f"Error in initialization: {str(e)}")
            self.logger.error("Traceback:", exc_info=True)
            raise

        logging.info("ReviewAnalyzer initialization completed successfully")

    def _initialize_analyzers(self) -> Dict[str, Any]:
        """
        初始化所有分析器

        返回:
            Dict[str, Any]: 分析器字典 {分析器名称: 分析器实例}
        """
        try:
            analyzers = {
                'user_analysis': UserAnalyzer(),
                'timing_analysis': TimingAnalyzer(),
                'location_analysis': LocationAnalyzer(),
                'purpose_analysis': PurposeAnalyzer(),
                'scenario_analysis': ScenarioAnalyzer(),
                'motivation_analysis': MotivationAnalyzer(),
                'experience_analysis': ExperienceAnalyzer(),
                'design_analysis': DesignExpectationAnalyzer()
            }

            self.logger.info("All analyzers initialized successfully")
            return analyzers

        except Exception as e:
            self.logger.error(f"Error initializing analyzers: {str(e)}")
            raise

    def _setup_logging(self):
        """设置日志配置"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'analysis_{timestamp}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件

        参数:
            config_path: 配置文件路径
        返回:
            Dict: 配置信息
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logging.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logging.error(f"Error loading config: {str(e)}")
            return {}

    def analyze(self, input_file: str, output_name: str = None) -> str:
        """
        执行完整的分析流程
        """
        try:
            # 1. 加载和预处理数据
            print("\n=== 数据加载阶段 ===")
            df = self.data_processor.load_data(input_file, nrows=100)
            print(f"加载数据形状: {df.shape}")
            print(f"数据列: {df.columns.tolist()}")

            print("\n=== 数据处理阶段 ===")
            processed_df = self.data_processor.process_dataframe(df)
            print(f"处理后数据形状: {processed_df.shape}")

            # 2. 执行各维度分析
            print("\n=== 维度分析阶段 ===")
            analysis_results = {}
            for name, analyzer in self.analyzers.items():
                try:
                    print(f"\n开始 {name} 分析...")
                    results = analyzer.analyze(processed_df)
                    analysis_results[name] = results
                    print(f"{name} 分析完成，结果大小: {len(results) if results else 0}")
                except Exception as e:
                    print(f"Error in {name} analysis: {str(e)}")
                    continue

            # 3. 生成洞察
            print("\n=== 洞察生成阶段 ===")
            insights = self.insight_generator.generate_comprehensive_insights(
                analysis_results
            )
            print(f"生成洞察数量: {len(insights) if insights else 0}")

            # 4. 生成报告
            print("\n=== 报告生成阶段 ===")
            report_path = self.report_generator.generate_report(
                analysis_results,
                insights,
                output_name
            )
            print(f"报告已生成: {report_path}")

            return report_path

        except Exception as e:
            print(f"\nError in analysis process: {str(e)}")
            raise
def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Amazon Product Review Analyzer')
    parser.add_argument('input_file', help='Path to the input Excel file')
    parser.add_argument(
        '--output',
        help='Name of the output report file',
        default=None
    )
    parser.add_argument(
        '--config',
        help='Path to the configuration file',
        default='config.yaml'
    )

    args = parser.parse_args()

    try:
        # 创建分析器实例
        analyzer = ReviewAnalyzer(args.config)

        # 执行分析
        report_path = analyzer.analyze(args.input_file, args.output)

        print(f"\nAnalysis completed successfully!")
        print(f"Report saved to: {report_path}")

    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    # 添加NLTK资源初始化，包含重试机制
    from src.utils.nltk_initializer import initialize_nltk_resources

    initialize_nltk_resources(max_retries=3, retry_delay=2)

    # 执行主程序
    main()