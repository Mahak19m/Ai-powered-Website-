"""
Test Runner to execute all test suites.
"""
import sys
import traceback
import test_database_layer
import test_phase3_dashboard_api
import test_phase4_e2e_integration
import test_multi_page_suite
import test_exact_refinement_suite
import test_exact_skills
import test_user_scenario
import test_api

modules = [
    test_database_layer,
    test_phase3_dashboard_api,
    test_phase4_e2e_integration,
    test_multi_page_suite,
    test_exact_refinement_suite,
    test_exact_skills,
    test_user_scenario,
    test_api
]

total = 0
passed = 0
failed = 0

print("=" * 60)
print("RUNNING ALL WEBCRAFT AI TEST SUITES")
print("=" * 60)

for mod in modules:
    mod_name = mod.__name__
    print(f"\n--- Testing module: {mod_name} ---")
    test_funcs = [getattr(mod, name) for name in dir(mod) if (name.startswith("test_") or name.startswith("run_")) and callable(getattr(mod, name))]
    for func in test_funcs:
        total += 1
        try:
            func()
            passed += 1
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            failed += 1
            print(f"  [FAIL] {func.__name__}")
            traceback.print_exc()

print("\n" + "=" * 60)
print(f"RESULTS: Total={total}, Passed={passed}, Failed={failed}")
print("=" * 60)

if failed > 0:
    sys.exit(1)
else:
    print("ALL TESTS PASSED SUCCESSFULLY! 100% OK")
