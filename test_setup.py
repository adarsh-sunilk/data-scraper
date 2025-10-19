"""
Test script to verify the Clinical Trials Data Scraper setup
"""
import sys
import importlib.util

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    modules_to_test = [
        'requests',
        'pandas', 
        'pydantic',
        'click',
        'tqdm'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing dependencies with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required modules imported successfully!")
        return True

def test_project_modules():
    """Test if project modules can be imported"""
    print("\nTesting project modules...")
    
    project_modules = [
        'config',
        'models', 
        'clinical_trials_api',
        'data_processor',
        'main'
    ]
    
    failed_imports = []
    
    for module in project_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import project modules: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All project modules imported successfully!")
        return True

def test_api_connection():
    """Test basic API connection"""
    print("\nTesting API connection...")
    
    try:
        from clinical_trials_api import ClinicalTrialsAPI
        api = ClinicalTrialsAPI()
        
        # Test with a simple search
        trials = api.search_trials(query="cancer", max_results=5)
        
        if trials:
            print(f"✅ API connection successful! Retrieved {len(trials)} trials")
            print(f"   Example trial: {trials[0].brief_title}")
            return True
        else:
            print("⚠️  API connection successful but no trials returned")
            return True
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Clinical Trials Data Scraper - Setup Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n❌ Setup test failed due to missing dependencies")
        sys.exit(1)
    
    # Test project modules
    modules_ok = test_project_modules()
    
    if not modules_ok:
        print("\n❌ Setup test failed due to project module issues")
        sys.exit(1)
    
    # Test API connection
    api_ok = test_api_connection()
    
    if not api_ok:
        print("\n⚠️  Setup test completed with API connection issues")
        print("   The scraper may still work, but API connectivity should be checked")
    else:
        print("\n✅ All tests passed! The scraper is ready to use.")
    
    print("\n" + "=" * 50)
    print("Setup test completed!")

if __name__ == "__main__":
    main()
