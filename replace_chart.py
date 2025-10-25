#!/usr/bin/env python3
"""
Replace hardcoded SVG chart with StrategyChart component in BuilderV2Page.jsx
"""

file_path = "frontend/src/pages/BuilderV2Page.jsx"

# Read file
with open(file_path, 'r') as f:
    lines = f.readlines()

# Find start: "        {/* Chart */"
# Find end: "          </svg>"
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if "        {/* Chart */" in line and start_idx is None:
        start_idx = i
    if "          </svg>" in line and start_idx is not None and end_idx is None:
        end_idx = i
        break

if start_idx is None or end_idx is None:
    print(f"Could not find chart bounds. start_idx={start_idx}, end_idx={end_idx}")
    exit(1)

print(f"Found chart SVG from line {start_idx+1} to {end_idx+1} ({end_idx - start_idx + 1} lines)")

# Replacement code
replacement = """        {/* Chart */}
        <div className="relative h-[400px] bg-[#0d1230] rounded-lg mb-6">
          {/* Universal Strategy Chart */}
          <StrategyChart 
            strategyId={strategyData.strategyId}
            size="full"
            currentPrice={currentPrice}
            strikes={strategyData.strikes}
            premiums={strategyData.premiums}
            volatility={strategyData.volatility || 0.348}
            daysToExpiry={420}
          />
        </div>
"""

# Build new file
new_lines = lines[:start_idx] + [replacement] + lines[end_idx+1:]

# Write back
with open(file_path, 'w') as f:
    f.writelines(new_lines)

print(f"✅ Replaced {end_idx - start_idx + 1} lines with {len(replacement.splitlines())} lines")
print(f"📝 New file has {len(new_lines)} lines (was {len(lines)})")
