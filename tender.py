import requests
from datetime import datetime, timedelta
import json

def get_contracts_finder_active():
    """
    Get active contracts from Contracts Finder (last 7 days)
    """
    url = "https://www.contractsfinder.service.gov.uk/api/rest/2/search_notices/json"
    
    # Calculate dates
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    # Format dates as DD/MM/YYYY
    published_from = week_ago.strftime("%d/%m/%Y")
    published_to = today.strftime("%d/%m/%Y")
    
    payload = {
        "searchCriteria": {
            "statuses": ["Open"],  # Open for bidding
            "publishedFrom": published_from,
            "publishedTo": published_to
        },
        "size": 1000  # Max results per request
    }
    
    print(f"📋 Fetching Contracts Finder (Open contracts from {published_from} to {published_to})...")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        total = data.get('totalResults', 0)
        contracts = data.get('noticeList', {}).get('notice', [])
        
        print(f"✅ Found {total} active contracts on Contracts Finder")
        return contracts
        
    except Exception as e:
        print(f"❌ Error fetching Contracts Finder: {e}")
        return []


def get_find_a_tender_active():
    """
    Get active tenders from Find a Tender (last 7 days)
    """
    url = "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages"
    
    # Calculate dates
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    # Format dates as YYYY-MM-DDTHH:MM:SS
    updated_from = week_ago.strftime("%Y-%m-%dT%H:%M:%S")
    updated_to = today.strftime("%Y-%m-%dT%H:%M:%S")
    
    params = {
        "stages": "tender",  # Open for bidding
        "updatedFrom": updated_from,
        "updatedTo": updated_to,
        "limit": 100
    }
    
    print(f"\n📋 Fetching Find a Tender (Open tenders from {updated_from} to {updated_to})...")
    
    all_releases = []
    
    try:
        while True:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            releases = data.get('releases', [])
            all_releases.extend(releases)
            
            # Check if there are more results (pagination)
            cursor = data.get('cursor')
            if not cursor or not releases:
                break
            
            params['cursor'] = cursor
            print(f"   Fetching more results (cursor: {cursor[:20]}...)...")
        
        print(f"✅ Found {len(all_releases)} active tenders on Find a Tender")
        return all_releases
        
    except Exception as e:
        print(f"❌ Error fetching Find a Tender: {e}")
        return []


def display_summary(cf_contracts, fat_tenders):
    """
    Display summary of results
    """
    print("\n" + "="*60)
    print("📊 SUMMARY - ACTIVE CONTRACTS (LAST 7 DAYS)")
    print("="*60)
    
    print(f"\n🔹 Contracts Finder: {len(cf_contracts)} contracts")
    if cf_contracts:
        print("\n   Sample contracts:")
        for i, contract in enumerate(cf_contracts[:3], 1):
            title = contract.get('title', 'N/A')
            org = contract.get('organisation', {}).get('name', 'N/A')
            value = contract.get('value', 'N/A')
            print(f"   {i}. {title}")
            print(f"      Org: {org} | Value: £{value}")
    
    print(f"\n🔹 Find a Tender: {len(fat_tenders)} tenders")
    if fat_tenders:
        print("\n   Sample tenders:")
        for i, tender in enumerate(fat_tenders[:3], 1):
            title = tender.get('tender', {}).get('title', 'N/A')
            buyer = tender.get('buyer', {}).get('name', 'N/A')
            ocid = tender.get('ocid', 'N/A')
            print(f"   {i}. {title}")
            print(f"      Buyer: {buyer} | OCID: {ocid}")
    
    print(f"\n📈 TOTAL ACTIVE OPPORTUNITIES: {len(cf_contracts) + len(fat_tenders)}")
    print("="*60)


def save_to_files(cf_contracts, fat_tenders):
    """
    Save results to JSON files
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save Contracts Finder data
    cf_filename = f"contracts_finder_active_{timestamp}.json"
    with open(cf_filename, 'w') as f:
        json.dump(cf_contracts, f, indent=2)
    print(f"\n💾 Saved Contracts Finder data to: {cf_filename}")
    
    # Save Find a Tender data
    fat_filename = f"find_a_tender_active_{timestamp}.json"
    with open(fat_filename, 'w') as f:
        json.dump(fat_tenders, f, indent=2)
    print(f"💾 Saved Find a Tender data to: {fat_filename}")


# Main execution
if __name__ == "__main__":
    print("🚀 Starting Active Contracts Pull...\n")
    
    # Fetch from both sources
    cf_contracts = get_contracts_finder_active()
    fat_tenders = get_find_a_tender_active()
    
    # Display summary
    display_summary(cf_contracts, fat_tenders)
    
    # Save to files
    save_to_files(cf_contracts, fat_tenders)
    
    print("\n✅ Done!")
