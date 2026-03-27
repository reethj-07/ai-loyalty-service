#!/bin/bash
# Segment Query Commands
# Replace API_URL with your Railway deployment URL

API_URL="https://ai-loyalty-service-production.up.railway.app"

echo "AI Loyalty Service - Segment Queries"
echo "====================================="
echo ""

# 1. Get all segments overview
echo "1. Getting segment overview..."
curl -s "${API_URL}/api/v1/ai/segmentation/run?force=true" | \
  python -m json.tool | \
  head -50

echo ""
echo "---"
echo ""

# 2. Get full segmentation data
echo "2. Getting full segmentation data..."
curl -s "${API_URL}/api/v1/ai/segmentation/run?force=true" > full_segments.json
echo "✅ Saved to full_segments.json"

echo ""
echo "---"
echo ""

# 3. Extract New-Customers member IDs (requires jq)
if command -v jq &> /dev/null; then
    echo "3. Extracting New-Customers member IDs..."
    curl -s "${API_URL}/api/v1/ai/segmentation/run?force=true" | \
      jq -r '.predictions[] | select(.segment_name == "New-Customers") | .member_id' | \
      head -10
    echo "... (showing first 10)"
else
    echo "3. jq not installed - skipping extraction"
    echo "   Install with: sudo apt install jq"
fi

echo ""
echo "---"
echo ""

# 4. Get segment counts
echo "4. Getting segment counts..."
curl -s "${API_URL}/api/v1/ai/segmentation/run?force=true" | \
  python -c "
import sys, json
data = json.load(sys.stdin)
dist = data.get('segment_distribution', {})
for name, info in dist.items():
    print(f'{name}: {info[\"count\"]} members ({info[\"percentage\"]}%)')
"

echo ""
echo "✅ Done!"
