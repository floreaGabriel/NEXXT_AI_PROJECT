#!/usr/bin/env python3
"""Test script for the MCP Email Server.

This script tests the MCP Email Server by sending a test email
using the email_summary_agent with MCP integration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.utils.mcp_email_client import verify_smtp_config, get_mcp_email_server_params
from src.agents.email_summary_agent import email_summary_agent

# Load environment variables
load_dotenv()


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


async def test_mcp_email_server():
    """Test the MCP Email Server functionality."""
    
    print_header("MCP Email Server Test")
    
    # Step 1: Verify configuration
    print("\n1. Verifying SMTP configuration...")
    is_valid, message = verify_smtp_config()
    
    if not is_valid:
        print(f"   ✗ Configuration error: {message}")
        print("\n   Please set the following environment variables:")
        print("   - SMTP_HOST (required)")
        print("   - SMTP_USER (optional)")
        print("   - SMTP_PASSWORD (optional)")
        print("   - SMTP_PORT (optional, default: 587)")
        print("   - FROM_EMAIL (optional)")
        return False
    
    print(f"   ✓ {message}")
    
    # Step 2: Display configuration (without sensitive data)
    print("\n2. Current SMTP configuration:")
    print(f"   - SMTP_HOST: {os.getenv('SMTP_HOST')}")
    print(f"   - SMTP_PORT: {os.getenv('SMTP_PORT', '587')}")
    print(f"   - SMTP_USER: {os.getenv('SMTP_USER', 'Not set')}")
    print(f"   - SMTP_PASSWORD: {'*' * 8 if os.getenv('SMTP_PASSWORD') else 'Not set'}")
    print(f"   - FROM_EMAIL: {os.getenv('FROM_EMAIL', os.getenv('SMTP_USER', 'Not set'))}")
    print(f"   - SMTP_TLS: {os.getenv('SMTP_TLS', 'true')}")
    
    # Step 3: Get test email address
    test_email = os.getenv("TEST_EMAIL")
    if not test_email:
        print("\n3. Test email address:")
        print("   ℹ TEST_EMAIL environment variable not set.")
        test_email = input("   Enter test email address: ").strip()
        
        if not test_email or "@" not in test_email:
            print("   ✗ Invalid email address")
            return False
    else:
        print(f"\n3. Using test email: {test_email}")
    
    # Step 4: Test the email agent with MCP server
    print("\n4. Testing MCP Email Server via email_summary_agent...")
    print("   This will send a test email using the MCP protocol.")
    
    try:
        # Prepare test data
        test_prompt = f"""
        Please send a test email with the following details:
        - To: {test_email}
        - Subject: MCP Email Server Test
        - Body: Acest email este un test al noului MCP Email Server. 
                Sistemul funcționează corect dacă primiți acest mesaj.
                
                Detalii tehnice:
                - Serverul folosește protocolul Model Context Protocol (MCP)
                - Emailul este trimis prin SMTP cu configurația din environment
                - Data: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Run the agent
        result = email_summary_agent.run(test_prompt)
        
        print(f"\n   Agent response:")
        print(f"   {result.output}")
        
        print("\n   ✓ Test completed successfully!")
        print(f"   Please check {test_email} for the test email.")
        
        return True
        
    except Exception as e:
        print(f"\n   ✗ Error: {str(e)}")
        print(f"\n   Stack trace:")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    try:
        success = asyncio.run(test_mcp_email_server())
        
        print_header("Test Summary")
        if success:
            print("\n✓ All tests passed!")
            print("\nThe MCP Email Server is working correctly.")
            sys.exit(0)
        else:
            print("\n✗ Tests failed!")
            print("\nPlease check the configuration and try again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
