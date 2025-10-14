#!/usr/bin/env python3
"""
Detailed Chart Data Analysis Test
Deep dive into the chart data structure and content
"""

import requests
import json


def test_chart_data_details():
    """Test detailed chart data structure"""
    url = "http://localhost:8000/api/unusual-whales/trading-strategies"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return False

        data = response.json()
        strategies = data.get("trading_strategies", [])

        print("🎯 DETAILED CHART DATA ANALYSIS")
        print(f"Found {len(strategies)} strategies")

        for i, strategy in enumerate(strategies):
            print(f"\n📋 Strategy {i+1}: {strategy.get('strategy_name', 'Unknown')}")
            print(f"   Ticker: {strategy.get('ticker', 'N/A')}")
            print(f"   Type: {strategy.get('strategy_type', 'N/A')}")

            if "chart" in strategy:
                chart = strategy["chart"]
                print(f"   📊 Chart Type: {chart.get('chart_type', 'N/A')}")

                # Check for chart metrics
                metrics = ["max_profit", "max_loss", "breakeven", "breakeven_points"]
                for metric in metrics:
                    if metric in chart:
                        print(f"   💰 {metric}: {chart[metric]}")

                # Analyze plotly chart
                if "plotly_chart" in chart:
                    try:
                        plotly_data = json.loads(chart["plotly_chart"])
                        print("   📈 Plotly Structure:")
                        print(f"     - Has data: {'data' in plotly_data}")
                        print(f"     - Has layout: {'layout' in plotly_data}")

                        if "data" in plotly_data:
                            traces = plotly_data["data"]
                            print(f"     - Number of traces: {len(traces)}")

                            if traces:
                                first_trace = traces[0]
                                x_data = first_trace.get("x", [])
                                y_data = first_trace.get("y", [])
                                print(f"     - X data points: {len(x_data)}")
                                print(f"     - Y data points: {len(y_data)}")

                                if x_data and y_data:
                                    print(
                                        f"     - X range: ${min(x_data):.2f} - ${max(x_data):.2f}"
                                    )
                                    print(
                                        f"     - Y range: ${min(y_data):.2f} - ${max(y_data):.2f}"
                                    )

                        if "layout" in plotly_data:
                            layout = plotly_data["layout"]
                            print(f"     - Title: {layout.get('title', 'N/A')}")
                            print(f"     - Template: {layout.get('template', 'N/A')}")

                    except Exception as e:
                        print(f"   ❌ Plotly parsing error: {str(e)}")
                else:
                    print("   ❌ No plotly_chart field")
            else:
                print("   ❌ No chart field")

        return True

    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        return False


if __name__ == "__main__":
    test_chart_data_details()
