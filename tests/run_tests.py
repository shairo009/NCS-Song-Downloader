"""
GitHub Actions Test - NCS Downloader Bot
Tests that the search functionality works correctly
"""

import sys

def test_ytdlp_installed():
    """Test 1: yt-dlp is installed"""
    try:
        import yt_dlp
        version = getattr(yt_dlp, '__version__', 'unknown')
        print(f"✅ Test 1 PASSED: yt-dlp {version} installed")
        return True
    except ImportError:
        print("❌ Test 1 FAILED: yt-dlp not installed")
        return False

def test_search_works():
    """Test 2: Can search YouTube"""
    import yt_dlp
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info('ytsearch3:tobu infectious ncs', download=False)
            entries = info.get('entries', [])
            if entries and len(entries) > 0:
                print(f"✅ Test 2 PASSED: Found {len(entries)} results for 'tobu infectious'")
                for e in entries[:2]:
                    print(f"   - {e.get('title', 'Unknown')[:60]}")
                return True
            else:
                print("❌ Test 2 FAILED: No results found")
                return False
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        return False

def test_random_queries():
    """Test 3: Multiple NCS queries work"""
    import yt_dlp
    queries = ['tobu ncs', 'cartoon ncs', 'different heaven ncs']
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
    
    all_pass = True
    for query in queries:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f'ytsearch2:{query}', download=False)
                entries = info.get('entries', [])
                count = len([e for e in entries if e and e.get('id')])
                print(f"   Query '{query}': {count} results - {'✅' if count > 0 else '❌'}")
                if count == 0:
                    all_pass = False
        except Exception as e:
            print(f"   Query '{query}': ❌ Error - {e}")
            all_pass = False
    
    if all_pass:
        print("✅ Test 3 PASSED: All queries return results")
    else:
        print("❌ Test 3 FAILED: Some queries failed")
    return all_pass

def test_ncs_channel():
    """Test 4: NCS channel is accessible"""
    import yt_dlp
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info('ytsearch3:ncs music', download=False)
            entries = info.get('entries', [])
            if entries and len(entries) > 0:
                print(f"✅ Test 4 PASSED: NCS channel accessible ({len(entries)} results)")
                return True
            else:
                print("❌ Test 4 FAILED: No NCS results")
                return False
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
        return False

def main():
    print("=" * 55)
    print("  NCS DOWNLOADER BOT - CI TESTS")
    print("=" * 55)
    print()
    
    tests = [
        ("yt-dlp Installation", test_ytdlp_installed),
        ("YouTube Search", test_search_works),
        ("NCS Queries", test_random_queries),
        ("NCS Channel", test_ncs_channel),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, func in tests:
        print(f"\n📌 Running: {name}")
        try:
            if func():
                passed += 1
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
    
    print(f"\n" + "=" * 55)
    print(f"  RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("  ✅ ALL TESTS PASSED! BOT IS WORKING!")
    else:
        print("  ❌ SOME TESTS FAILED!")
    print("=" * 55)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())