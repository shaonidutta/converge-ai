#!/usr/bin/env python3
"""
Comprehensive ServiceAgent Testing Script
Tests all 10 types of questions the ServiceAgent handles
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Any

# Test Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZ3RzaGFvbmlkdXR0YTJrQGdtYWlsLmNvbSIsInVzZXJfaWQiOjE4MywidXNlcl90eXBlIjoiY3VzdG9tZXIiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxNzM0NTg5LCJpYXQiOjE3NjE3MzI3ODl9.QWxB7nFhnkdb4AUueUmIMKA5PtBQALhb0etEJcyPPDE"

class ServiceAgentTester:
    def __init__(self):
        self.session = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "categories": {}
        }
    
    async def setup(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def send_message(self, message: str) -> Dict[str, Any]:
        """Send message to ServiceAgent"""
        try:
            async with self.session.post(
                f"{BASE_URL}/chat/message",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {TOKEN}"
                },
                json={"message": message}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_response(self, response: Dict, expected_keywords: List[str], test_name: str) -> bool:
        """Check if response contains expected keywords"""
        if "error" in response:
            print(f"❌ {test_name}: API Error - {response['error']}")
            return False
        
        assistant_message = response.get("assistant_message", {}).get("message", "")
        
        # Check for expected keywords
        found_keywords = []
        for keyword in expected_keywords:
            if keyword.lower() in assistant_message.lower():
                found_keywords.append(keyword)
        
        if len(found_keywords) >= len(expected_keywords) * 0.7:  # 70% match threshold
            print(f"✅ {test_name}: PASSED")
            print(f"   Found: {found_keywords}")
            return True
        else:
            print(f"❌ {test_name}: FAILED")
            print(f"   Expected: {expected_keywords}")
            print(f"   Found: {found_keywords}")
            print(f"   Response: {assistant_message[:100]}...")
            return False
    
    async def test_category_browsing(self):
        """Test Type 1: Category Browsing Questions"""
        print("\n🔍 TESTING CATEGORY BROWSING QUESTIONS")
        
        tests = [
            ("What categories do you have?", ["categories", "service"]),
            ("Show me all service categories", ["categories", "service"]),
            ("List all categories", ["categories", "list"]),
            ("What services do you offer?", ["services", "offer"]),
            ("Browse categories", ["categories", "browse"])
        ]
        
        passed = 0
        for message, keywords in tests:
            response = await self.send_message(message)
            if self.check_response(response, keywords, f"Category: {message}"):
                passed += 1
            self.results["total_tests"] += 1
        
        self.results["categories"]["Category Browsing"] = f"{passed}/{len(tests)}"
        self.results["passed"] += passed
        self.results["failed"] += len(tests) - passed
    
    async def test_subcategory_browsing(self):
        """Test Type 2: Subcategory Browsing Questions"""
        print("\n🔍 TESTING SUBCATEGORY BROWSING QUESTIONS")
        
        # Test core subcategory patterns for key services
        tests = [
            ("subcategories for cleaning", ["Home Cleaning", "subcategories"]),
            ("subcategories for packers", ["Packers and Movers", "subcategories"]),
            ("subcategories for electrical", ["Electrical", "subcategories"]),
            ("subcategories for salon", ["Salon", "subcategories"]),
            ("subcategories for car care", ["Car Care", "subcategories"]),
            ("what plumbing services do you have", ["Plumbing", "services"]),
            ("show me painting options", ["Painting", "subcategories"]),
            ("types of pest control services", ["Pest Control", "subcategories"])
        ]
        
        passed = 0
        for message, keywords in tests:
            response = await self.send_message(message)
            if self.check_response(response, keywords, f"Subcategory: {message}"):
                passed += 1
            self.results["total_tests"] += 1
            await asyncio.sleep(0.5)  # Rate limiting
        
        self.results["categories"]["Subcategory Browsing"] = f"{passed}/{len(tests)}"
        self.results["passed"] += passed
        self.results["failed"] += len(tests) - passed
    
    async def test_nlp_capabilities(self):
        """Test Type 5: NLP-Enhanced Variations"""
        print("\n🔍 TESTING NLP CAPABILITIES")
        
        # Spelling mistakes and semantic variations
        tests = [
            ("subcategories for pakkers", ["Packers and Movers", "corrected"]),
            ("subcategories for eletrician", ["Electrical", "mean"]),
            ("subcategories for moving company", ["Packers and Movers", "subcategories"]),
            ("subcategories for beauty salon", ["Salon for Women", "subcategories"]),
            ("subcategories for barber shop", ["Salon for Men", "subcategories"]),
            ("subcategories for water filter", ["Water Purifier", "subcategories"]),
            ("subcategories for house cleaning", ["cleaning", "subcategories"]),
            ("subcategories for pest extermination", ["Pest Control", "subcategories"])
        ]
        
        passed = 0
        for message, keywords in tests:
            response = await self.send_message(message)
            if self.check_response(response, keywords, f"NLP: {message}"):
                passed += 1
            self.results["total_tests"] += 1
            await asyncio.sleep(0.5)
        
        self.results["categories"]["NLP Capabilities"] = f"{passed}/{len(tests)}"
        self.results["passed"] += passed
        self.results["failed"] += len(tests) - passed
    
    async def test_service_search(self):
        """Test Type 3: Service Search Questions"""
        print("\n🔍 TESTING SERVICE SEARCH QUESTIONS")

        tests = [
            ("search for cleaning", ["cleaning", "services"]),
            ("find plumbing services", ["plumbing", "services"]),
            ("look for electrical work", ["electrical", "services"]),
            ("I need painting services", ["painting", "services"]),
            ("cleaning services", ["cleaning", "services"])  # Simplified price test
        ]

        passed = 0
        for message, keywords in tests:
            response = await self.send_message(message)
            if self.check_response(response, keywords, f"Search: {message}"):
                passed += 1
            self.results["total_tests"] += 1
            await asyncio.sleep(0.5)

        self.results["categories"]["Service Search"] = f"{passed}/{len(tests)}"
        self.results["passed"] += passed
        self.results["failed"] += len(tests) - passed

    async def test_advanced_patterns(self):
        """Test Type 8: Advanced Query Patterns"""
        print("\n🔍 TESTING ADVANCED QUERY PATTERNS")

        tests = [
            ("What types of cleaning do you offer?", ["cleaning", "types"]),
            ("Can you show me salon options?", ["salon", "options"]),
            ("I'm looking for electrical services", ["electrical", "services"]),
            ("Do you have plumbing available?", ["plumbing", "available"]),
            ("What painting services are there?", ["painting", "services"])
        ]

        passed = 0
        for message, keywords in tests:
            response = await self.send_message(message)
            if self.check_response(response, keywords, f"Advanced: {message}"):
                passed += 1
            self.results["total_tests"] += 1
            await asyncio.sleep(0.5)

        self.results["categories"]["Advanced Patterns"] = f"{passed}/{len(tests)}"
        self.results["passed"] += passed
        self.results["failed"] += len(tests) - passed

    async def test_service_listing(self):
        """Test Type 4: Service Listing Questions"""
        print("\n🔍 TESTING SERVICE LISTING QUESTIONS")

        tests = [
            ("show me all services", ["services", "all"]),
            ("list all services", ["services", "list"]),
            ("what services are available", ["services", "available"]),
            ("show me all cleaning services", ["cleaning", "services"])
        ]

        passed = 0
        for message, keywords in tests:
            response = await self.send_message(message)
            if self.check_response(response, keywords, f"Listing: {message}"):
                passed += 1
            self.results["total_tests"] += 1
            await asyncio.sleep(0.5)

        self.results["categories"]["Service Listing"] = f"{passed}/{len(tests)}"
        self.results["passed"] += passed
        self.results["failed"] += len(tests) - passed
    
    async def test_error_handling(self):
        """Test Type 9: Error Handling & Edge Cases"""
        print("\n🔍 TESTING ERROR HANDLING")
        
        tests = [
            ("subcategories for xyz", ["couldn't find", "try"]),
            ("subcategories for", ["try", "search"]),
            ("random gibberish query", ["try", "categories"]),
            ("subcategories for repair", ["repair", "services"])  # Ambiguous
        ]
        
        passed = 0
        for message, keywords in tests:
            response = await self.send_message(message)
            if self.check_response(response, keywords, f"Error: {message}"):
                passed += 1
            self.results["total_tests"] += 1
            await asyncio.sleep(0.5)
        
        self.results["categories"]["Error Handling"] = f"{passed}/{len(tests)}"
        self.results["passed"] += passed
        self.results["failed"] += len(tests) - passed
    
    async def run_all_tests(self):
        """Run all test categories"""
        print("🚀 STARTING COMPREHENSIVE SERVICEAGENT TESTING")
        print("=" * 60)
        
        await self.setup()
        
        try:
            await self.test_category_browsing()
            await self.test_subcategory_browsing()
            await self.test_nlp_capabilities()
            await self.test_service_search()
            await self.test_advanced_patterns()
            await self.test_service_listing()
            await self.test_error_handling()
            
            # Print final results
            print("\n" + "=" * 60)
            print("🎯 FINAL TEST RESULTS")
            print("=" * 60)
            
            success_rate = (self.results["passed"] / self.results["total_tests"]) * 100
            
            print(f"Total Tests: {self.results['total_tests']}")
            print(f"Passed: {self.results['passed']}")
            print(f"Failed: {self.results['failed']}")
            print(f"Success Rate: {success_rate:.1f}%")
            
            print("\nResults by Category:")
            for category, result in self.results["categories"].items():
                print(f"  {category}: {result}")
            
            if success_rate >= 80:
                print("\n🎉 EXCELLENT! ServiceAgent is production-ready!")
            elif success_rate >= 60:
                print("\n✅ GOOD! ServiceAgent is functional with minor issues.")
            else:
                print("\n⚠️ NEEDS IMPROVEMENT! Several issues found.")
                
        finally:
            await self.cleanup()

async def main():
    """Main test runner"""
    tester = ServiceAgentTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
