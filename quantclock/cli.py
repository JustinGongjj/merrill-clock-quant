"""Command-line entry point for the cross-asset Merrill-clock baseline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .backtest import performance_metrics, prices_to_monthly_returns, run_backtest
from .data import fetch_fred_panel, fetch_market_prices
from .macro import make_clock_features
from .signals import default_research_tilts, map_regimes_to_assets, regime_probabilities


def run_research(args: argparse.Namespace) -> int:
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    print("Fetching FRED macro observations and Yahoo Finance adjusted-price proxies...")
    macro = fetch_fred_panel(start=args.start)
    prices = fetch_market_prices(start=args.start)
    returns = prices_to_monthly_returns(prices)
    macro.to_csv(out / "macro_latest_vintage.csv", index_label="date")
    prices.to_csv(out / "daily_adjusted_prices_proxy.csv", index_label="date")
    returns.to_csv(out / "monthly_asset_returns.csv", index_label="date")

    features = make_clock_features(
        macro["industrial_production"], macro["cpi"], returns.index,
        ip_release_lag_days=args.ip_lag_days,
        cpi_release_lag_days=args.cpi_lag_days,
    )
    probabilities = regime_probabilities(features, window=args.z_window, smooth=args.smooth)
    asset_map = {sleeve: ticker for sleeve, ticker in {
        "equity": "SPY", "treasury_intermediate": "IEF",
        "gold": "GLD", "broad_commodities": "DBC", "cash": "BIL",
    }.items() if ticker in returns.columns}
    required = {"equity", "treasury_intermediate", "gold", "broad_commodities"}
    if not required.issubset(asset_map):
        raise RuntimeError(f"Downloaded market data lacks core sleeves. Got {returns.columns.tolist()}")
    # Do not silently convert missing ETF history into a zero-return sleeve.
    returns = returns.dropna(subset=list(asset_map.values()))
    weights = map_regimes_to_assets(probabilities, asset_map, default_research_tilts())
    result = run_backtest(returns, weights, cost_bps=args.cost_bps)
    combined = (features.join(probabilities.add_prefix("p_"), how="outer")
                .join(weights.add_prefix("w_"), how="outer").join(result, how="outer"))
    combined.to_csv(out / "clock_backtest.csv", index_label="date")
    metrics = performance_metrics(result["net_return"])
    metrics.update({
        "observations": int(result["net_return"].notna().sum()),
        "cost_bps_per_one_way_turnover": args.cost_bps,
        "weights": "illustrative research tilts; not an investment recommendation",
        "data_warning": "FRED latest revisions + Yahoo adjusted-price proxies",
    })
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Saved generated outputs to {out.resolve()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="merrill-clock-quant",
        description="Public-data Merrill-clock cross-asset research baseline (not trading advice)",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="fetch public proxies and run the illustrative baseline")
    run.add_argument("--start", default="2000-01-01", help="first date to request (YYYY-MM-DD)")
    run.add_argument("--output", default="./outputs", help="directory for generated data and metrics")
    run.add_argument("--cost-bps", type=float, default=10.0)
    run.add_argument("--ip-lag-days", type=int, default=20)
    run.add_argument("--cpi-lag-days", type=int, default=20)
    run.add_argument("--z-window", type=int, default=60)
    run.add_argument("--smooth", type=int, default=3)
    run.set_defaults(func=run_research)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
