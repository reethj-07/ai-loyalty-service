# 🎯 Segment Query Guide

Quick reference for querying which members are in which segment.

---

## 🚀 Quick Start

### **Easiest Method: Python Script**

```bash
# Install dependencies (if needed)
pip install requests tabulate

# View all segments
python get_test_members.py

# View specific segment
python get_test_members.py "New-Customers"
python get_test_members.py "At-Risk"
```

**Output Example:**
```
📊 SEGMENT SUMMARY
┌────────────────┬───────┬───────┬──────────────┬────────────────┬──────────────┐
│ Segment        │ Count │   %   │ Avg Recency  │ Avg Frequency  │ Avg Monetary │
├────────────────┼───────┼───────┼──────────────┼────────────────┼──────────────┤
│ At-Risk        │  211  │ 84.7% │  999.0 days  │   0.0 txns     │    $0.00     │
│ New-Customers  │   38  │ 15.3% │   10.3 days  │   7.1 txns     │ $1531.82     │
└────────────────┴───────┴───────┴──────────────┴────────────────┴──────────────┘

👥 SAMPLE TEST MEMBERS (3 per segment)

🏷️  At-Risk:
   1. abc123... (confidence: 92.3%)
   2. def456... (confidence: 89.1%)
   3. ghi789... (confidence: 87.5%)

🏷️  New-Customers:
   1. fc42bb88-8c79-421e-a9dd-109489460fae (confidence: 85.3%)
   2. 2d0619b5-7b57-4c03-94f2-781112bb8962 (confidence: 82.1%)
   3. f333b0bb-9ea9-4596-b6d5-6a1c5debfd26 (confidence: 79.8%)
```

---

## 📋 Methods Overview

| Method | Use Case | Output |
|--------|----------|--------|
| **Python Script** | Easy, visual, with test commands | ⭐ Recommended |
| **API Direct** | CI/CD, automation | JSON response |
| **Shell Script** | Quick command-line | Formatted text |
| **jq Filtering** | Advanced filtering | Specific data extraction |

---

## 📡 API Endpoint Reference

### **Base Endpoint**
```
GET /api/v1/ai/segmentation/run?force=true
```

**Response Structure:**
```json
{
  "status": "success",
  "timestamp": "2026-02-09T...",
  "members_segmented": 415,

  "segment_distribution": {
    "Segment-Name": {
      "count": 38,
      "percentage": 15.3,
      "avg_recency_days": 10.3,
      "avg_frequency": 7.1,
      "avg_monetary": 1531.82
    }
  },

  "predictions": [
    {
      "member_id": "uuid-here",
      "segment_id": 1,
      "segment_name": "New-Customers",
      "confidence": 0.853,
      "segment_profile": {
        "name": "New-Customers",
        "description": "Recently joined, building relationship",
        "size": 38,
        "characteristics": {
          "high_value": false,
          "frequent": true,
          "recent": true
        }
      }
    }
  ]
}
```

---

## 🔧 Usage Examples

### **1. Get All Segments**

```bash
# Via curl
curl -X GET "https://your-app.railway.app/api/v1/ai/segmentation/run?force=true"

# Via Python
python get_test_members.py
```

### **2. Get Members in "New-Customers" Segment**

```bash
# Via Python (recommended)
python get_test_members.py "New-Customers"

# Via curl + jq
curl -s "https://your-app.railway.app/api/v1/ai/segmentation/run?force=true" | \
  jq -r '.predictions[] | select(.segment_name == "New-Customers") | .member_id'
```

### **3. Find Segment for Specific Member**

```bash
python test_segmentation.py
# Choose option 3, enter member ID
```

### **4. Export All Segments to JSON**

```bash
curl "https://your-app.railway.app/api/v1/ai/segmentation/run?force=true" > segments.json

# Or use the script
python test_segmentation.py
# Choose option 5
```

---

## 🧪 Testing Campaign Metrics

### **Step-by-Step: Make Metrics Populate**

**1. Identify Target Segment**
```bash
# Your campaign targets: "new_customers"
python get_test_members.py "New-Customers"
```

**2. Pick a Member ID**
```
# From output, pick first member:
fc42bb88-8c79-421e-a9dd-109489460fae
```

**3. Create Test Transaction**
```bash
curl -X POST "https://your-app.railway.app/api/v1/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "fc42bb88-8c79-421e-a9dd-109489460fae",
    "amount": 150.00,
    "merchant": "Test Store",
    "type": "purchase"
  }'
```

**4. Check Campaign Metrics**
```bash
# Wait 30 seconds, then check UI
# Or via API:
curl "https://your-app.railway.app/api/v1/ai/campaign/YOUR_CAMPAIGN_ID/metrics"
```

**Expected Result:**
- Participants: 0 → 1
- Transactions: 0 → 1
- Revenue: $0 → $150
- Actual ROI: 0% → [calculated]

---

## 📊 Understanding Segments

### **Segment Types in Your System**

Based on K-Means clustering with 2-5 segments:

| Segment | Characteristics | Typical Count |
|---------|----------------|---------------|
| **Champions** | Recent + Frequent + High-Value | Varies |
| **High-Value** | Recent purchases + High spending | Varies |
| **At-Risk** | No purchase in 90+ days | ~211 (84.7%) |
| **New-Customers** | Signed up <60 days ago | ~38 (15.3%) |
| **Segment-N** | Other behavioral patterns | Varies |

### **Features Used for Segmentation**

```
1. recency_days          Days since last purchase
2. frequency_lifetime    Total number of purchases
3. monetary_total        Total amount spent
4. monetary_avg          Average transaction value
5. category_diversity    Variety of purchase categories
6. days_since_signup     Account age
7. tier_encoded          Loyalty tier (0-3)
8. monetary_trend        Spending trend indicator
```

---

## 🎯 Campaign Testing Workflow

```
1. Run Segmentation
   ↓
2. Identify Target Segment Members
   ↓
3. Launch Campaign (targets that segment)
   ↓
4. Create Transaction from Target Member
   ↓
5. Wait 30 seconds
   ↓
6. Check Campaign Live Metrics
   ↓
7. See Populated Metrics! ✅
```

---

## 💡 Pro Tips

1. **Use force=true** to get fresh segmentation results:
   ```
   /api/v1/ai/segmentation/run?force=true
   ```

2. **Segment names are case-insensitive**:
   ```bash
   python get_test_members.py "new-customers"  # Works
   python get_test_members.py "New-Customers"  # Also works
   ```

3. **Save segmentation results** for reference:
   ```bash
   curl "..." > segments_$(date +%Y%m%d).json
   ```

4. **Create multiple test transactions** from the same segment to see metrics increase:
   ```bash
   # Transaction 1
   curl -X POST ... -d '{"member_id": "member1", "amount": 100}'

   # Transaction 2 (same or different member in segment)
   curl -X POST ... -d '{"member_id": "member2", "amount": 150}'

   # Campaign metrics will now show:
   # Participants: 2, Transactions: 2, Revenue: $250
   ```

---

## 🐛 Troubleshooting

### **"No members found in segment"**

**Cause:** Segment name doesn't match exactly.

**Solution:**
```bash
# First, get exact segment names:
python get_test_members.py

# Then use the exact name:
python get_test_members.py "New-Customers"  # Correct capitalization
```

### **"Segmentation takes too long"**

**Cause:** Processing 415 members with ML model.

**Solution:** Wait 10-30 seconds. The API has a 30s timeout.

### **"Members in segment but metrics still 0"**

**Cause:** Transaction created BEFORE campaign launch, or wrong member.

**Solution:**
1. Check campaign start time
2. Verify member is in target segment
3. Create new transaction AFTER campaign start
4. Use member ID from segment query results

---

## 📞 Quick Reference Commands

```bash
# View all segments
python get_test_members.py

# View specific segment with test commands
python get_test_members.py "New-Customers"

# Interactive query tool
python test_segmentation.py

# Export to JSON
curl "https://your-app.railway.app/api/v1/ai/segmentation/run?force=true" > segments.json

# Create test transaction
curl -X POST "https://your-app.railway.app/api/v1/transactions" \
  -H "Content-Type: application/json" \
  -d '{"member_id": "MEMBER_ID_HERE", "amount": 100, "merchant": "Test", "type": "purchase"}'
```

---

## ✅ Success Checklist

Use this to verify segmentation is working:

- [ ] Can run segmentation and see 2+ segments
- [ ] Can see member count for each segment
- [ ] Can extract specific member IDs from a segment
- [ ] Can find which segment a specific member belongs to
- [ ] Can create a transaction for a segment member
- [ ] Can verify campaign metrics update after transaction

---

**🎉 You're all set!** Use these tools to query segments and test your campaigns.

For more help, see:
- [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
