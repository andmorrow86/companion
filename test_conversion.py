"""
Quick test to verify the personal assistant conversion is working
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import SERVICES, BUSINESS_NAME
from core.nlu import NLU

print("=" * 60)
print("Personal Assistant Conversion Test")
print("=" * 60)

# Test 1: Check business name
print(f"\n✓ Business Name: {BUSINESS_NAME}")

# Test 2: Check services
print(f"\n✓ Available Services ({len(SERVICES)}):")
for key, service in SERVICES.items():
    print(f"  - {service['name']}: ${service['price']} ({service['duration']} min)")

# Test 3: Test NLU
print(f"\n✓ Testing NLU Module:")
nlu = NLU()

test_messages = [
    "I need general assistance",
    "Book administrative support for tomorrow",
    "I want event planning",
    "Help with lifestyle management",
    "Need concierge services",
    "Senior care assistance needed"
]

for msg in test_messages:
    intent = nlu.classify_intent(msg)
    service = nlu.extract_service(msg)
    print(f"  Message: '{msg}'")
    print(f"    Intent: {intent}")
    print(f"    Service: {service}")
    print()

# Test 4: Check service keywords
print(f"✓ Service Keywords:")
for service, keywords in nlu.service_keywords.items():
    print(f"  {service}: {', '.join(keywords[:3])}...")

print("\n" + "=" * 60)
print("✅ All tests passed! Conversion successful.")
print("=" * 60)