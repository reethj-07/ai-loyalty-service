#!/usr/bin/env python3
"""
Test script to query member segments
Usage: python test_segmentation.py
"""
import requests
import json
from datetime import datetime

# Configuration
API_URL = "https://ai-loyalty-service-production.up.railway.app"  # Replace with your Railway URL
# For local testing: API_URL = "http://localhost:8000"

def run_segmentation():
    """Run customer segmentation and get all segments"""
    print("🔄 Running customer segmentation...\n")

    response = requests.get(
        f"{API_URL}/api/v1/ai/segmentation/run?force=true",
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        print("✅ Segmentation completed successfully!\n")
        print("="*70)
        print(f"Total Members Segmented: {data.get('members_segmented', 0)}")
        print("="*70)

        # Display segment distribution
        segment_dist = data.get('segment_distribution', {})
        print("\n📊 SEGMENT DISTRIBUTION:\n")

        for segment_name, segment_info in segment_dist.items():
            print(f"  🏷️  {segment_name}")
            print(f"      Count: {segment_info['count']} members ({segment_info['percentage']}%)")
            print(f"      Avg Recency: {segment_info['avg_recency_days']} days")
            print(f"      Avg Frequency: {segment_info['avg_frequency']} transactions")
            print(f"      Avg Monetary: ${segment_info['avg_monetary']:.2f}")
            print()

        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def get_members_by_segment(segment_name):
    """Get all members in a specific segment"""
    print(f"🔍 Finding members in '{segment_name}' segment...\n")

    # First run segmentation to get fresh data
    response = requests.get(
        f"{API_URL}/api/v1/ai/segmentation/run?force=true",
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        predictions = data.get('predictions', [])

        # Filter members by segment
        segment_members = [
            pred for pred in predictions
            if pred['segment_name'].lower() == segment_name.lower()
        ]

        print(f"✅ Found {len(segment_members)} members in '{segment_name}' segment\n")
        print("="*70)

        # Display first 10 members
        for i, member in enumerate(segment_members[:10], 1):
            print(f"\n  {i}. Member ID: {member['member_id']}")
            print(f"     Segment: {member['segment_name']}")
            print(f"     Confidence: {member['confidence']:.1%}")

            profile = member.get('segment_profile', {})
            print(f"     Profile:")
            print(f"       - Recency: {profile.get('avg_recency_days', 0):.1f} days")
            print(f"       - Frequency: {profile.get('avg_frequency', 0):.1f} txns")
            print(f"       - Monetary: ${profile.get('avg_monetary', 0):.2f}")

        if len(segment_members) > 10:
            print(f"\n  ... and {len(segment_members) - 10} more members")

        print("\n" + "="*70)

        return segment_members
    else:
        print(f"❌ Error: {response.status_code}")
        return []

def get_member_segment(member_id):
    """Get the segment assignment for a specific member"""
    print(f"🔍 Finding segment for member: {member_id}\n")

    response = requests.get(
        f"{API_URL}/api/v1/ai/segmentation/run?force=true",
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        predictions = data.get('predictions', [])

        # Find the specific member
        member_segment = next(
            (pred for pred in predictions if pred['member_id'] == member_id),
            None
        )

        if member_segment:
            print("✅ Member found!\n")
            print("="*70)
            print(f"  Member ID: {member_segment['member_id']}")
            print(f"  Segment: {member_segment['segment_name']}")
            print(f"  Segment ID: {member_segment['segment_id']}")
            print(f"  Confidence: {member_segment['confidence']:.1%}")

            profile = member_segment.get('segment_profile', {})
            print(f"\n  Segment Profile:")
            print(f"    Name: {profile.get('name')}")
            print(f"    Description: {profile.get('description')}")
            print(f"    Size: {profile.get('size')} members")
            print(f"    Avg Recency: {profile.get('avg_recency_days', 0):.1f} days")
            print(f"    Avg Frequency: {profile.get('avg_frequency', 0):.1f} transactions")
            print(f"    Avg Monetary: ${profile.get('avg_monetary', 0):.2f}")

            characteristics = profile.get('characteristics', {})
            print(f"\n  Characteristics:")
            print(f"    High Value: {'✅' if characteristics.get('high_value') else '❌'}")
            print(f"    Frequent: {'✅' if characteristics.get('frequent') else '❌'}")
            print(f"    Recent: {'✅' if characteristics.get('recent') else '❌'}")
            print("="*70)

            return member_segment
        else:
            print(f"❌ Member {member_id} not found in segmentation results")
            return None
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def find_members_for_campaign_testing(count=5):
    """Find members suitable for campaign testing"""
    print(f"🎯 Finding {count} members for campaign testing...\n")

    # Get all segments
    response = requests.get(
        f"{API_URL}/api/v1/ai/segmentation/run?force=true",
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        predictions = data.get('predictions', [])

        # Get members from each segment
        segments = {}
        for pred in predictions:
            segment_name = pred['segment_name']
            if segment_name not in segments:
                segments[segment_name] = []
            segments[segment_name].append(pred)

        print("✅ Test Members by Segment:\n")
        print("="*70)

        for segment_name, members in segments.items():
            print(f"\n📋 {segment_name} Segment:")
            print(f"   Total: {len(members)} members")
            print(f"\n   Top {min(count, len(members))} Members for Testing:")

            for i, member in enumerate(members[:count], 1):
                print(f"\n   {i}. Member ID: {member['member_id']}")
                print(f"      Confidence: {member['confidence']:.1%}")

                # Show command to create test transaction
                print(f"\n      📝 Test Transaction Command:")
                print(f"      curl -X POST \"{API_URL}/api/v1/transactions\" \\")
                print(f"        -H \"Content-Type: application/json\" \\")
                print(f"        -d '{{")
                print(f"          \"member_id\": \"{member['member_id']}\",")
                print(f"          \"amount\": 100.00,")
                print(f"          \"merchant\": \"Test Store\",")
                print(f"          \"type\": \"purchase\"")
                print(f"        }}'")

        print("\n" + "="*70)
        return segments
    else:
        print(f"❌ Error: {response.status_code}")
        return {}

def export_segments_to_json(filename="segments.json"):
    """Export all segment assignments to JSON file"""
    print(f"💾 Exporting segments to {filename}...\n")

    response = requests.get(
        f"{API_URL}/api/v1/ai/segmentation/run?force=true",
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Exported segmentation data to {filename}")
        print(f"   Members: {data.get('members_segmented', 0)}")
        print(f"   Segments: {len(data.get('segment_distribution', {}))}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  AI LOYALTY SERVICE - SEGMENT QUERY TOOL")
    print("="*70 + "\n")

    # Menu
    print("What would you like to do?\n")
    print("1. View all segments (overview)")
    print("2. Get members in a specific segment")
    print("3. Find segment for a specific member")
    print("4. Get test members for campaign testing")
    print("5. Export all segments to JSON")
    print("6. Run all queries")
    print()

    choice = input("Enter choice (1-6): ").strip()

    print("\n")

    if choice == "1":
        run_segmentation()

    elif choice == "2":
        segment_name = input("Enter segment name (e.g., 'New-Customers', 'At-Risk'): ").strip()
        get_members_by_segment(segment_name)

    elif choice == "3":
        member_id = input("Enter member ID: ").strip()
        get_member_segment(member_id)

    elif choice == "4":
        count = input("How many members per segment? (default: 5): ").strip()
        count = int(count) if count else 5
        find_members_for_campaign_testing(count)

    elif choice == "5":
        filename = input("Enter filename (default: segments.json): ").strip()
        filename = filename if filename else "segments.json"
        export_segments_to_json(filename)

    elif choice == "6":
        # Run all
        print("🚀 Running all queries...\n")
        run_segmentation()
        print("\n")
        input("Press Enter to continue...")
        find_members_for_campaign_testing(3)
        print("\n")
        input("Press Enter to continue...")
        export_segments_to_json()

    else:
        print("❌ Invalid choice")

    print("\n✅ Done!\n")
