import requests
import sys
from datetime import datetime
import json

class WebStudioAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            self.test_results.append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success,
                "response_preview": response.text[:200] if not success else "OK"
            })

            return success, response.json() if success and response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": "ERROR",
                "success": False,
                "response_preview": str(e)
            })
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        success, response = self.run_test(
            "API Root",
            "GET",
            "",
            200
        )
        return success

    def test_create_contact_message(self):
        """Test creating a contact message"""
        test_data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "message": "Olá, gostaria de saber mais sobre os vossos serviços de desenvolvimento web."
        }
        
        success, response = self.run_test(
            "Create Contact Message",
            "POST",
            "contact",
            200,
            data=test_data
        )
        
        if success and 'id' in response:
            print(f"   Created contact message with ID: {response['id']}")
            return response['id']
        return None

    def test_get_contact_messages(self):
        """Test retrieving contact messages"""
        success, response = self.run_test(
            "Get Contact Messages",
            "GET",
            "contact",
            200
        )
        
        if success:
            print(f"   Retrieved {len(response)} contact messages")
            return len(response)
        return 0

    def test_create_status_check(self):
        """Test creating a status check"""
        test_data = {
            "client_name": "Test Client"
        }
        
        success, response = self.run_test(
            "Create Status Check",
            "POST",
            "status",
            200,
            data=test_data
        )
        return success

    def test_get_status_checks(self):
        """Test retrieving status checks"""
        success, response = self.run_test(
            "Get Status Checks",
            "GET",
            "status",
            200
        )
        return success

def main():
    print("🚀 Starting Web & Studio API Tests")
    print("=" * 50)
    
    # Setup
    tester = WebStudioAPITester()
    
    # Test API availability
    if not tester.test_api_root():
        print("❌ API root endpoint failed, stopping tests")
        return 1

    # Test contact endpoints (main functionality)
    print("\n📧 Testing Contact Endpoints...")
    contact_id = tester.test_create_contact_message()
    if not contact_id:
        print("❌ Contact message creation failed")
    
    message_count = tester.test_get_contact_messages()
    if message_count == 0:
        print("⚠️  No contact messages retrieved (might be expected if database is empty)")

    # Test status endpoints (additional functionality)
    print("\n📊 Testing Status Endpoints...")
    tester.test_create_status_check()
    tester.test_get_status_checks()

    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    # Print detailed results
    print("\n📋 Detailed Test Results:")
    for result in tester.test_results:
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {result['name']}: {result['actual_status']} (expected {result['expected_status']})")
        if not result["success"]:
            print(f"   Error: {result['response_preview']}")

    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
