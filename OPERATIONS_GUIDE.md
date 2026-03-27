# 🎯 AI Loyalty Service - Operations Manager Guide

**Version:** 1.0  
**Last Updated:** February 6, 2026  
**Access URL:** `https://ai-loyalty-service.vercel.app` (will be provided by IT)

---

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing Members](#managing-members)
4. [Managing Transactions](#managing-transactions)
5. [AI Campaign Management](#ai-campaign-management)
6. [Reports & Analytics](#reports--analytics)
7. [Common Workflows](#common-workflows)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### First Time Login

1. **Open the application**
   - Go to the URL provided: `https://ai-loyalty-service.vercel.app/login`
   - You'll see a login page

2. **Sign in**
   - Enter your email and password
   - Click "Sign In"
   - You'll be redirected to the dashboard

3. **Understanding the interface**
   - Navigation menu on the left
   - Main content area in the center
   - Your profile/logout option at the top right

---

## 📊 Dashboard Overview

### Main Sections

**Loyalty Management**
- **Members** - View and manage customer profiles
- **Transactions** - Track customer purchases and points
- **Points Activity** - Monitor points balances
- **Points Transfer** - Move points between members
- **Order Tracking** - View transaction history

**AI Intelligence**
- **AI Intelligence Hub** - View AI-generated campaign recommendations
- **Campaign Live** - Monitor active campaigns in real-time
- **Requests Tracking** - Review and approve AI campaign proposals
- **Rejects** - View rejected campaign proposals

**Campaigns**
- **Batch Campaigns** - Create and manage marketing campaigns
- **Communication Logs** - View campaign message history

**Analytics**
- **Fraudsters** - AI-detected suspicious behavior patterns
- **Members Report** - Member statistics and insights
- **Activity Report** - Transaction trends and analytics

---

## 👥 Managing Members

### View All Members

1. Click **"Members"** in the left sidebar
2. You'll see:
   - Total member count at the top
   - Search bar to find specific members
   - Table with all member details
   - Pagination controls at the bottom

**Member Information Displayed:**
- Creation Date
- First Name & Last Name
- Mobile Number
- Tier (Bronze, Silver, Gold, Platinum)
- Points Balance
- Status (active/inactive)

### Add a New Member

1. Click **"Add new"** button (top right)
2. Fill in the form:
   - **First Name** ✱ (required)
   - **Last Name** ✱ (required)
   - **Email Address** (optional)
   - **Mobile Number** (optional, but must be valid if provided)
   - **Membership Tier** (Bronze, Silver, Gold, Platinum)
3. Click **"Create Member"**
4. Success message will appear
5. New member appears in the list immediately

**✅ Expected Result:**
- Pop-up message: "Member [Name] created successfully!"
- Member appears in the table
- Total count increases by 1

### Bulk Import Members (CSV Upload)

1. Click **"Import CSV"** button
2. Select your CSV file
3. Wait for upload to complete
4. See summary: "X members imported successfully. Y failed."

**CSV Format Required:**
```csv
email,first_name,last_name,mobile,tier
john@example.com,John,Doe,+1234567890,Gold
jane@example.com,Jane,Smith,+0987654321,Silver
```

**✅ Expected Result:**
- Import summary shows how many succeeded/failed
- Successfully imported members appear in the list

### Search for Members

1. Use the search bar at the top
2. Type any of:
   - Member name
   - Mobile number
   - Email
   - Tier
3. Results filter automatically as you type
4. Clear search to see all members again

### Navigate Pages

- Use **"Rows"** dropdown to show 25, 50, or 100 per page
- Use **"Previous"** and **"Next"** buttons to move between pages
- Current page and total pages shown in the middle

---

## 💳 Managing Transactions

### View All Transactions

1. Click **"Transactions"** in the sidebar
2. See list of all customer purchases
3. Each transaction shows:
   - Date & Time
   - Member ID
   - Merchant name
   - Transaction type
   - Amount

### Create a New Transaction

1. Click **"Add new"** button
2. Fill in the form:
   - **Member ID or Email** ✱
   - **Amount** ✱ (e.g., 150.00)
   - **Merchant** (e.g., "Nike Store")
   - **Transaction Type** (purchase, refund, etc.)
3. Click **"Create Transaction"**

**✅ Expected Result:**
- Transaction created successfully
- Appears in transaction list
- **Important:** This triggers AI behavior detection
- Member's points may update automatically

**🤖 What Happens Behind the Scenes:**
- AI analyzes the transaction pattern
- If unusual behavior detected, creates a campaign proposal
- You can review the proposal in "Requests Tracking"

### Bulk Import Transactions (CSV)

1. Click **"Import CSV"** button
2. Select your CSV file
3. Wait for processing

**CSV Format:**
```csv
member_id,amount,merchant,type,category
test@example.com,250.00,Nike Store,purchase,retail
test@example.com,50.00,Starbucks,purchase,food
```

**✅ Expected Result:**
- Shows "X transactions imported. Y failed."
- All transactions trigger AI analysis
- May generate multiple campaign proposals

---

## 🤖 AI Campaign Management

### Understanding the AI Workflow

```
Transaction Created
    ↓
AI Detects Behavior Pattern
    ↓
AI Creates Campaign Proposal
    ↓
Operations Manager Reviews (YOU)
    ↓
Approve or Reject
    ↓
If Approved → Campaign Launches Automatically
```

### Review AI Campaign Proposals

1. Click **"Requests Tracking"** in sidebar
2. See all **pending proposals** waiting for your review
3. Each proposal shows:
   - Segment (who should receive it)
   - Behavior detected (e.g., "high_spender", "dormant")
   - Suggested campaign type
   - Suggested offer/message
   - Estimated ROI
   - Cost breakdown

### Approve a Campaign

1. Find the proposal in "Requests Tracking"
2. Click **"Review & Launch"** button
3. Review the details:
   - Target segment size
   - Estimated participants
   - Message preview
   - Cost per message
   - Incentive cost
   - Total cost
   - Estimated revenue
   - ROI percentage
4. **Optional:** Edit campaign name or message
5. Click **"Approve & Launch"**

**✅ Expected Result:**
- Success message appears
- Campaign status changes to "scheduled" or "active"
- Campaign appears in "Batch Campaigns" page
- If auto-execution is enabled, messages send immediately

### Reject a Campaign

1. Click **"Reject"** button on any proposal
2. Enter a reason (e.g., "Budget constraints", "Not relevant")
3. Confirm rejection

**✅ Expected Result:**
- Proposal moves to "Rejects" page
- No longer appears in pending list
- Can be viewed later for audit purposes

### Monitor Live Campaigns

1. Click **"Campaign Live"** in sidebar
2. Select a campaign from the list
3. See real-time metrics:
   - Messages sent
   - Open rate
   - Click rate
   - Conversions
   - Revenue generated
   - ROI
4. **Options:**
   - Pause campaign (stop sending)
   - Resume campaign
   - View detailed analytics

---

## 📈 Reports & Analytics

### Members Report

1. Click **"Members Report"** in sidebar
2. See key metrics:
   - Total members by tier
   - Average points balance
   - Member growth trends
3. Use for monthly reporting

### Activity Report

1. Click **"Activity Report"**
2. View transaction trends:
   - Top merchants
   - Transaction volume
   - Revenue trends
3. Filter by date range (if available)

### Fraudsters / Suspicious Behavior

1. Click **"Fraudsters"** in sidebar
2. AI shows detected unusual patterns:
   - Members with suspicious transaction patterns
   - Potential fraud indicators
   - Behavior anomalies
3. **Action Required:** Review and investigate flagged accounts

**⚠️ What to Look For:**
- Unusual spending spikes
- Rapid point accumulation
- Suspicious merchant patterns
- Multiple refunds

---

## 🔄 Common Workflows

### Workflow 1: Onboard New Members

**Goal:** Add 100 new customers to the loyalty program

1. **Prepare CSV file** with member data
2. Go to **Members** page
3. Click **"Import CSV"**
4. Upload file
5. Verify import summary
6. Search for a few members to confirm they're in the system

**Time:** 2-3 minutes for 100 members

---

### Workflow 2: Process Daily Transactions

**Goal:** Import daily transaction file from POS system

1. Receive transaction CSV from POS vendor
2. Go to **Transactions** page
3. Click **"Import CSV"**
4. Upload file
5. Wait for processing (may take 1-2 minutes for large files)
6. Check **"Requests Tracking"** after 5 minutes
7. Review any AI-generated campaign proposals

**Time:** 5-10 minutes daily

---

### Workflow 3: Review & Launch Weekly Campaigns

**Goal:** Review AI recommendations and approve relevant campaigns

1. Monday morning: Open **"Requests Tracking"**
2. Review pending proposals (typically 3-10 per week)
3. For each proposal:
   - Check target segment makes sense
   - Verify offer is appropriate
   - Review estimated cost vs ROI
   - Approve or reject with reason
4. Monitor approved campaigns in **"Campaign Live"**
5. Check results at end of week

**Time:** 15-30 minutes weekly

---

### Workflow 4: Handle Points Transfer Requests

**Goal:** Transfer points between members (e.g., gift, correction)

1. Go to **"Points Transfer"** page
2. Enter:
   - **From Member:** email or ID
   - **To Member:** email or ID
   - **Points:** amount to transfer
3. Click **"Transfer Points"**
4. Verify success message

**Time:** 1 minute per transfer

---

### Workflow 5: Monthly Reporting

**Goal:** Generate insights for management

1. Go to **"Members Report"**
   - Note total members by tier
   - Screenshot key metrics
2. Go to **"Activity Report"**
   - Review transaction trends
   - Note top merchants
3. Go to **"Batch Campaigns"**
   - Count active campaigns
   - Review ROI of completed campaigns
4. Go to **"AI Intelligence Hub"**
   - Count pending recommendations
5. Compile into monthly report for management

**Time:** 20-30 minutes monthly

---

## 🆘 Troubleshooting

### Issue: "Failed to fetch members" Error

**Cause:** Backend connection issue or authentication expired

**Solution:**
1. Refresh the page (F5)
2. If persists, log out and log back in
3. If still failing, contact IT support

---

### Issue: CSV Import Failed

**Possible Causes:**
- Wrong file format (must be .csv)
- Missing required columns
- Invalid data (e.g., bad email format)

**Solution:**
1. Check CSV file format matches the template
2. Ensure all required fields are present
3. Verify data is valid (emails have @, phones have numbers)
4. Try importing a small sample first (5-10 rows)
5. Check error message for specific issue

---

### Issue: Campaign Not Launching After Approval

**Possible Causes:**
- Auto-execution disabled (IT config)
- Backend processing delay

**Solution:**
1. Wait 2-3 minutes after approval
2. Check **"Batch Campaigns"** to see if campaign appears
3. Check campaign status (should be "scheduled" or "active")
4. If not appearing after 5 minutes, contact IT

---

### Issue: Search Not Working

**Solution:**
1. Clear the search box and try again
2. Make sure you're searching for fields that exist (name, email, mobile, tier)
3. Refresh the page
4. Try searching with fewer characters

---

### Issue: Pagination Showing Wrong Numbers

**Cause:** Data changed while viewing, or page refresh needed

**Solution:**
1. Click refresh or go back to page 1
2. Use search to find specific members instead

---

## 📋 Best Practices

### Daily Tasks
- [ ] Check **"Requests Tracking"** for pending proposals (2x per day)
- [ ] Review **"Fraudsters"** for suspicious activity (1x per day)
- [ ] Import daily transaction files (end of day)

### Weekly Tasks
- [ ] Review and approve/reject campaign proposals
- [ ] Check **"Campaign Live"** for campaign performance
- [ ] Review **"Communication Logs"** for message delivery status

### Monthly Tasks
- [ ] Generate member growth report
- [ ] Calculate campaign ROI summary
- [ ] Review tier distribution changes
- [ ] Archive rejected proposals

---

## 🔑 Quick Reference

### Status Indicators

| Icon/Color | Meaning |
|------------|---------|
| 🟢 Green dot | Active/Healthy |
| ⚫ Gray dot | Inactive |
| 🔵 Blue badge | Campaign status |
| 🟡 Yellow | Warning/Pending |
| 🔴 Red | Error/Rejected |

### Membership Tiers

| Tier | Description | Typical Benefits |
|------|-------------|------------------|
| Bronze | Entry level | 1x points |
| Silver | Mid-tier | 1.5x points |
| Gold | Premium | 2x points + exclusive offers |
| Platinum | VIP | 3x points + concierge service |

### Campaign Types

| Type | Purpose | Example |
|------|---------|---------|
| Win-back | Re-engage dormant customers | "We miss you! 20% off" |
| Bonus | Reward high spenders | "Thank you! 500 bonus points" |
| Upsell | Increase transaction value | "Spend $50 more, get $10 off" |
| Retention | Keep active customers | "Exclusive member event invite" |

---

## 📞 Support Contacts

**For Technical Issues:**
- Email: it-support@company.com
- Slack: #loyalty-tech-support

**For Business Questions:**
- Manager: [Name]
- Email: [email]

**For Training/Help:**
- Refer to this guide
- Internal wiki: [link]
- Training videos: [link]

---

## ✅ Testing Checklist

Use this checklist when first accessing the system or after system updates:

### Initial Access Test
- [ ] Can log in successfully
- [ ] Dashboard loads without errors
- [ ] All menu items accessible
- [ ] Can log out and log back in

### Members Functionality
- [ ] View members list (should see data)
- [ ] Search for a member by name
- [ ] Add a new test member
- [ ] Verify new member appears in list
- [ ] Test pagination (Next/Previous buttons)

### Transactions Functionality
- [ ] View transaction list
- [ ] Create a test transaction
- [ ] Verify transaction appears in list
- [ ] Check if AI generated a proposal (wait 1-2 min)

### Campaign Review
- [ ] Open "Requests Tracking"
- [ ] See if test transaction created a proposal
- [ ] Review proposal details
- [ ] (Optional) Approve or reject
- [ ] Check campaign appears in "Batch Campaigns"

### Reports
- [ ] Open "Members Report" - verify data displays
- [ ] Open "Activity Report" - verify charts load
- [ ] Open "Fraudsters" - should load (may be empty)

---

## 🎓 Training Scenarios

### Scenario 1: New Customer Onboarding
**Situation:** 50 new customers signed up at the store today

**Steps:**
1. Collect their information (name, email, phone)
2. Create CSV file with their data
3. Import via "Members" page
4. Verify all 50 appear in system
5. Send welcome email (external to this system)

**Success Criteria:** All 50 members visible, can search and find them

---

### Scenario 2: High-Spender Detection
**Situation:** Loyal customer just made a $500 purchase

**Steps:**
1. Create transaction for $500
2. Wait 2 minutes
3. Check "Requests Tracking"
4. Should see AI proposal: "High Spender - Bonus Campaign"
5. Review and approve
6. Monitor in "Campaign Live"

**Success Criteria:** AI detects behavior, creates proposal, campaign launches after approval

---

### Scenario 3: Dormant Customer Win-Back
**Situation:** Customer hasn't transacted in 60 days

**Steps:**
1. AI automatically detects dormancy (no action needed)
2. Check "Requests Tracking" for "Dormant Customer" proposal
3. Review suggested re-engagement offer
4. Approve if offer is reasonable
5. Campaign sends within 24 hours

**Success Criteria:** Receive proposal, approve, campaign activates

---

## 📌 Important Notes

⚠️ **Data Privacy**
- Never share customer data outside the system
- Do not export member lists without approval
- Follow company data privacy policies

⚠️ **Campaign Approvals**
- Always review costs before approving
- Verify offers are current and valid
- Check target segment makes sense
- Document rejection reasons

⚠️ **System Limits**
- Members page shows up to 100 at a time (use pagination)
- CSV imports limited to 1,000 rows (split large files)
- Search works on current page + server-side
- Real-time updates may take 30-60 seconds

---

**End of Operations Guide**

*For questions or clarifications, contact your system administrator or refer to the technical documentation.*
