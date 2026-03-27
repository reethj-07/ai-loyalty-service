#!/usr/bin/env python3
"""
Quick script to get member IDs for campaign testing
Usage: python get_test_members.py [segment_name]
Example: python get_test_members.py "New-Customers"
"""
import requests
import sys
from tabulate import tabulate

API_URL = "https://ai-loyalty-service-production.up.railway.app"

def get_segment_members(segment_name=None):
    """Get members by segment for easy testing"""

    print(f"🔄 Fetching segmentation data...\n")

    try:
        response = requests.get(
            f"{API_URL}/api/v1/ai/segmentation/run?force=true",
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        predictions = data.get('predictions', [])
        segment_dist = data.get('segment_distribution', {})

        if not segment_name:
            # Show all segments summary
            print("=" * 80)
            print("📊 SEGMENT SUMMARY")
            print("=" * 80)

            table_data = []
            for name, info in segment_dist.items():
                table_data.append([
                    name,
                    info['count'],
                    f"{info['percentage']}%",
                    f"{info['avg_recency_days']:.1f} days",
                    f"{info['avg_frequency']:.1f} txns",
                    f"${info['avg_monetary']:.2f}"
                ])

            print(tabulate(
                table_data,
                headers=['Segment', 'Count', '%', 'Avg Recency', 'Avg Frequency', 'Avg Monetary'],
                tablefmt='grid'
            ))

            print(f"\n✅ Total Members: {data.get('members_segmented', 0)}\n")

            # Show sample members from each segment
            segments = {}
            for pred in predictions:
                seg = pred['segment_name']
                if seg not in segments:
                    segments[seg] = []
                if len(segments[seg]) < 3:  # Keep first 3 members per segment
                    segments[seg].append(pred)

            print("=" * 80)
            print("👥 SAMPLE TEST MEMBERS (3 per segment)")
            print("=" * 80)

            for seg_name in sorted(segments.keys()):
                print(f"\n🏷️  {seg_name}:")
                for i, member in enumerate(segments[seg_name], 1):
                    print(f"   {i}. {member['member_id']} (confidence: {member['confidence']:.1%})")

        else:
            # Show specific segment
            segment_members = [
                p for p in predictions
                if p['segment_name'].lower() == segment_name.lower()
            ]

            if not segment_members:
                print(f"❌ No members found in segment '{segment_name}'")
                print(f"\nAvailable segments:")
                for name in segment_dist.keys():
                    print(f"  - {name}")
                return

            print("=" * 80)
            print(f"🏷️  {segment_name.upper()} SEGMENT")
            print("=" * 80)

            # Show segment profile
            profile = segment_members[0]['segment_profile']
            print(f"\n📋 Profile:")
            print(f"   Description: {profile.get('description', 'N/A')}")
            print(f"   Total Members: {profile.get('size', 0)}")
            print(f"   Avg Recency: {profile.get('avg_recency_days', 0):.1f} days")
            print(f"   Avg Frequency: {profile.get('avg_frequency', 0):.1f} transactions")
            print(f"   Avg Monetary: ${profile.get('avg_monetary', 0):.2f}")

            # Show characteristics
            chars = profile.get('characteristics', {})
            print(f"\n✨ Characteristics:")
            print(f"   High Value: {'✅ Yes' if chars.get('high_value') else '❌ No'}")
            print(f"   Frequent: {'✅ Yes' if chars.get('frequent') else '❌ No'}")
            print(f"   Recent: {'✅ Yes' if chars.get('recent') else '❌ No'}")

            # Show member IDs
            print(f"\n👥 Members ({len(segment_members)} total):")
            print("=" * 80)

            table_data = []
            for i, member in enumerate(segment_members[:20], 1):  # Show first 20
                table_data.append([
                    i,
                    member['member_id'],
                    f"{member['confidence']:.1%}"
                ])

            print(tabulate(
                table_data,
                headers=['#', 'Member ID', 'Confidence'],
                tablefmt='grid'
            ))

            if len(segment_members) > 20:
                print(f"\n... and {len(segment_members) - 20} more members")

            # Show test transaction commands
            print("\n" + "=" * 80)
            print("🧪 TEST TRANSACTION COMMANDS")
            print("=" * 80)

            print("\n📝 Copy and paste these commands to test campaign metrics:\n")

            for i, member in enumerate(segment_members[:5], 1):
                print(f"# Test Transaction {i} - Member: {member['member_id'][:8]}...")
                print(f"curl -X POST \"{API_URL}/api/v1/transactions\" \\")
                print(f"  -H \"Content-Type: application/json\" \\")
                print(f"  -d '{{")
                print(f"    \"member_id\": \"{member['member_id']}\",")
                print(f"    \"amount\": {100 + (i * 50)}.00,")
                print(f"    \"merchant\": \"Test Store {i}\",")
                print(f"    \"type\": \"purchase\"")
                print(f"  }}'\n")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        print(f"\nMake sure the backend is running at: {API_URL}")
        sys.exit(1)

if __name__ == "__main__":
    segment_name = sys.argv[1] if len(sys.argv) > 1 else None

    if segment_name == "--help" or segment_name == "-h":
        print(__doc__)
        sys.exit(0)

    get_segment_members(segment_name)

    if not segment_name:
        print("\n💡 TIP: Run with a segment name to see detailed members:")
        print("   python get_test_members.py \"New-Customers\"")
        print("   python get_test_members.py \"At-Risk\"")

    print("\n✅ Done!\n")
