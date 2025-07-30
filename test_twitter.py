#!/usr/bin/env python3
"""
Test Twitter API rate limits and functionality
"""

import tweepy
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

def test_twitter_api():
    load_dotenv()
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if not bearer_token:
        print("❌ No Twitter Bearer Token found")
        return
    
    try:
        client = tweepy.Client(bearer_token=bearer_token)
        print("✅ Twitter client initialized")
        
        # Test accounts
        test_accounts = ['aircall', 'RingCentral', 'zoom']
        week_ago = datetime.now() - timedelta(days=7)
        
        for username in test_accounts:
            try:
                print(f"\n🔍 Testing @{username}...")
                
                # Get user info
                user = client.get_user(username=username)
                if user.data:
                    print(f"   ✅ Found: {user.data.name} (ID: {user.data.id})")
                    
                    # Try to get recent tweets
                    tweets = client.get_users_tweets(
                        user.data.id,
                        max_results=5,
                        tweet_fields=['created_at'],
                        start_time=week_ago.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                        exclude=['retweets', 'replies']
                    )
                    
                    if tweets.data:
                        print(f"   ✅ Found {len(tweets.data)} tweets in past week:")
                        for tweet in tweets.data[:2]:  # Show first 2
                            print(f"      - {tweet.created_at}: {tweet.text[:100]}...")
                    else:
                        print("   ⚠️ No tweets found in past week")
                        
                else:
                    print(f"   ❌ User @{username} not found")
                    
            except Exception as e:
                print(f"   ❌ Error with @{username}: {str(e)}")
                if "429" in str(e):
                    print("   ⏳ Rate limited - wait 15 minutes")
                    break
                    
    except Exception as e:
        print(f"❌ Client error: {str(e)}")

if __name__ == "__main__":
    test_twitter_api()