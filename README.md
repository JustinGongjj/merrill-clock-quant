# Merrill Clock Quant

**Author:** JustinGongjj · **License:** MIT

一个可检查、可独立运行的 Python 研究原型：用宏观增长与通胀动能构造美林时钟四象限概率，将其映射为跨资产研究权重，并提供回测、预测基线、离线 Q-learning 与合约级期货换月工具。仅用于研究、教学和软件测试，不是投资建议或交易系统。

## 功能

- **美林时钟状态**：把美国工业生产和 CPI 的动能变化转为四象限软概率；按假设发布滞后对齐宏观数据。
- **跨资产研究回测**：支持月频收益、下一期执行、换手成本扣减、描述性绩效指标和 walk-forward 切分。默认使用 ETF 作为资产类别代理。
- **模型基线**：扩展窗口 Ridge 预测，以及固定动作集合的离线表格 Q-learning 实验。没有附带模型权重。
- **期货换月**：可用调用者提供的逐合约结算价与 first-notice 日期构造换月收益代理，避免把跨月价差误算成收益。

## 安装与运行

需要 Python 3.10 或更新版本。

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[market,test]"

# 会联网请求 FRED 与 Yahoo Finance；输出只写入本地 outputs/
merrill-clock-quant run --start 2000-01-01 --output ./outputs/us-clock
```

不安装 `market` extra 仍可使用核心函数和 CSV 输入接口；当前 CLI 的在线示例会下载公开数据。没有自动下载或嵌入真实期货曲线。

Python API 示例：

```python
from quantclock.backtest import run_backtest, performance_metrics
from quantclock.futures import front_month_returns
from quantclock.signals import regime_probabilities
```

## 测试

```bash
python -m pip install -e ".[test]"
python -m pytest -q
```

测试使用确定性合成序列，不需要联网；覆盖范围见 [TESTING.md](TESTING.md)。

## 数据来源与方法边界

- FRED 工业生产与 CPI 默认返回当前可见的修订值。代码设置的滞后天数仅为近似，不能替代真实发布日期与 ALFRED 点时版本。
- Yahoo Finance ETF 调整价只是第三方代理数据，需自行核验企业行动、质量与使用/再分发条款。债券 ETF、黄金 ETF、商品 ETF 和现金 ETF 并非对应现货、国债现金流或真实期货持仓。
- 四象限概率不是经校准的经济周期标签、衰退概率或收益预测；示例权重只是研究先验。回测成本是简化换手扣减，不是滑点/冲击成本模型。
- Ridge 与强化学习实验不证明样本外有效或可盈利；请保留独立测试区间并与简单基准比较。
- 期货换月工具不模拟合约乘数、保证金、交易时点、交易所日历、手续费或真实滑点。
- 仓库不含真实行情、回测快照、个人数据、密钥、生成报告或模型权重。运行产生的数据和报告请勿未经审查就提交。

详见 [DATA_SOURCES.md](DATA_SOURCES.md)。软件按 MIT 许可发布；许可证不覆盖第三方数据及商标。

## 免责声明

历史数据与模拟结果不代表未来表现。该软件不提供证券建议、不连接券商、不下单，也不保证数据完整、准确或持续可用。使用者须自行核验数据、授权、模型假设及适用法规。
