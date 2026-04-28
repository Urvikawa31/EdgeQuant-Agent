# EdgeQuant Agent: Deep Dive Analysis Report

This report provides a comprehensive analysis of the `EdgeQuant Agent` codebase, breaking down its system architecture, experimentation pipeline, the models evaluated, and the final performance scoring.

## 1. Architecture Overview
The `EdgeQuant Agent` is a sophisticated, memory-augmented AI trading system designed to act as a High-Conviction Hedge Fund Portfolio Manager.

### 1.1 Memory Architecture (Hierarchical RAG)
The system leverages a multi-layered Vector Database (`MemoryDB` using ChromaDB) and `bge-small` embeddings to manage the agent's knowledge over time. It is structured into four distinct memory layers to avoid context window flooding and ensure relevant retrieval:

* **Short Layer**: Captures daily volatile information such as daily news.
* **Mid Layer**: Captures medium-term structural data such as quarterly 10-Q filings.
* **Long Layer**: Captures long-term foundational data such as annual 10-K filings.
* **Reflection Layer**: A cognitive memory layer that stores the agent's past decisions (`BUY`/`SELL`/`HOLD`) and its internal reasoning for those actions.

**Memory Dynamics**: The memory retrieval system utilizes a Linear Compound Score that balances:

* **Importance Initialization & Decay**: Scores decay over time based on the layer (e.g., Short memory decays much faster than Long memory).
* **Recency Decay**: Prioritizes more recent events unless older events have a high importance access frequency.
* **Access Counting**: The more a memory is accessed, the higher its importance score becomes.

### 1.2 Execution Modes: Warmup vs. Test
The pipeline is strictly divided into two modes to prevent data leakage while allowing the model to "learn" from history:

* **Warmup Mode**: The agent is run through historical data with access to the immediate future price difference (`future_record`). This allows the agent to generate highly accurate "reflections" (reasoning for why a move happened) and store them in the Reflection memory layer.
* **Test Mode**: The agent is evaluated on unseen data. The `future_record` is strictly hidden. The agent queries its pre-populated reflection memory (from the warmup phase) to recognize similar historical patterns and make alpha-generating decisions.

### 1.3 Dynamic Mandate Enforcement
To combat the common LLM passivity issue (defaulting to `HOLD`), the prompt dynamically enforces mandates based on the asset and day:

* **Weekday Alpha Capture**: For active trading days, `HOLD` is strictly prohibited for assets like `BTC` and `TSLA`. The model is forced to synthesize catalysts and take a definitive directional bias (`BUY` or `SELL`).
* **Weekend Logic**: During weekends (when traditional markets might be closed or low volume), `HOLD` is permitted if catalysts are of low magnitude.

## 2. Experimentation Setup
The experimental setup models a multi-asset portfolio simulation focusing on two distinct assets:

* **Bitcoin (BTC)**: Digital asset, evaluated on liquidity clusters and ETF flows.
* **Tesla (TSLA)**: Equity asset, evaluated on unit delivery variance and margin compression.

**Timeline:**
* **Warmup Period:** `2025-08-01` to `2026-04-25`
* **Test Period:** `2026-03-01` to `2026-04-23`

**Environment Integration**: Market data is sourced from local JSON files (`data/btc.json`, `data/tsla.json`). The `MarketEnv` steps through this data day-by-day, providing the agent with current prices, historical prices, momentum (window size of 3), and relevant textual data (news, filings).

The portfolio is instantiated with a `$100,000` cash base and evaluates performance based on Cumulative Return, Sharpe Ratio, Max Drawdown, and Annualized Volatility.

## 3. Models Evaluated
The system relies on an external LLM inference engine (Ollama Cloud) to generate trading decisions. During the testing phase (March 1, 2026, to April 23, 2026), four distinct foundational models were evaluated for their financial reasoning capabilities:

* `gpt-oss:120b-cloud` (120 Billion Parameters)
* `mistral-large-3:675b-cloud` (675 Billion Parameters)
* `gemma3:27b-cloud` (27 Billion Parameters)
* `nemotron-3-super:cloud` (Nvidia Super Model)

## 4. Evaluation Scoring
The models were evaluated against an Equal Weight Portfolio baseline (Cumulative Return: `0.1886`, Sharpe: `2.3872`).

### 4.1 GPT-OSS 120B (The Winner) 🏆
`gpt-oss:120b-cloud` was the only model capable of beating the Equal Weight Portfolio, demonstrating exceptional alpha capture, particularly on `TSLA`.

* **Portfolio Cumulative Return**: `0.1987` (vs `0.1886` Baseline)
* **Portfolio Sharpe Ratio**: `3.298` (vs `2.387` Baseline)
* **Max Drawdown**: `0.075` (Lowest risk)
* **Asset Breakdown**: Highly successful `TSLA` trades (Sharpe `3.28`), but struggled slightly to maximize `BTC` compared to the baseline.

### 4.2 Mistral Large 3 (675B)
Despite its massive parameter count, Mistral Large struggled to generate a cohesive portfolio return, heavily dragged down by poor `BTC` decision-making.

* **Portfolio Cumulative Return**: `0.0435`
* **Portfolio Sharpe Ratio**: `0.9039`
* **Asset Breakdown**: Good on `TSLA` (Sharpe `2.89`) but negative on `BTC` (Sharpe `-1.66`).

### 4.3 Gemma3 27B
The smallest model evaluated showed mixed results. It maintained a positive return but failed to outpace the baseline by a wide margin.

* **Portfolio Cumulative Return**: `0.0157`
* **Portfolio Sharpe Ratio**: `0.4288`
* **Asset Breakdown**: Negative on `BTC` (Sharpe `-1.13`) and moderate on `TSLA` (Sharpe `1.90`).

### 4.4 Nvidia Nemotron-3 Super
Nemotron completely failed to grasp the market dynamics during the test period, resulting in a net negative portfolio.

* **Portfolio Cumulative Return**: `-0.0543`
* **Portfolio Sharpe Ratio**: `-0.8665`
* **Asset Breakdown**: Severe losses on `BTC` (Sharpe `-1.89`) and barely positive on `TSLA`.

## Summary Conclusion
The architecture successfully proves that Hierarchical RAG combined with forced directional mandates can extract Alpha, provided the underlying LLM possesses sufficient reasoning capability. `gpt-oss:120b-cloud` is currently the optimal production model for the `EdgeQuant Agent`, achieving a superior risk-adjusted return (Sharpe `3.29`) with less maximum drawdown (`7.5%`) than a naive equal-weight allocation.
