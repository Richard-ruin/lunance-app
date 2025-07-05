# run_tests.py
import pytest
import sys
import os

def run_tests():
    """Run tests with proper environment setup"""
    
    # Set environment variables for testing
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017/lunance_test"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-very-long-and-secure"
    os.environ["USE_MOCK_EMAIL"] = "true"
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    print("🧪 Running Lunance API Tests...")
    print(f"📁 Working directory: {current_dir}")
    
    # Start with basic tests first
    test_args = [
        "app/tests/test_basic.py",  # Start with basic tests
        "-v",                       # Verbose output
        "--tb=short",              # Short traceback format
        "--disable-warnings",      # Disable warnings
        "--color=yes",             # Colored output
        "-s"                       # Don't capture output
    ]
    
    try:
        print("\n🏃‍♂️ Running basic tests first...")
        exit_code = pytest.main(test_args)
        
        if exit_code == 0:
            print("\n✅ Basic tests passed! Running all tests...")
            
            # Now run all tests
            all_test_args = [
                "app/tests/",
                "-v",
                "--tb=short",
                "--disable-warnings",
                "--color=yes",
                "-x"  # Stop on first failure
            ]
            
            exit_code = pytest.main(all_test_args)
            
            if exit_code == 0:
                print("\n🎉 All tests passed!")
            else:
                print(f"\n❌ Some tests failed with exit code: {exit_code}")
        else:
            print(f"\n❌ Basic tests failed with exit code: {exit_code}")
            
        return exit_code
        
    except Exception as e:
        print(f"\n💥 Error running tests: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)