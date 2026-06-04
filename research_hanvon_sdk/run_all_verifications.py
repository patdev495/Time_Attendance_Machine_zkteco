"""
run_all_verifications.py
Master script chay tat ca script kiem chung HANVON_PROTOCOL.md
Usage: uv run python research_hanvon_sdk/run_all_verifications.py
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import subprocess, os, time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = [
    ("Section 2 - XOR Codec",          "verify_section_2_xor.py"),
    ("Section 3 - TCP Frame Format",    "verify_section_3_frame.py"),
    ("Section 4 - Handshake",           "verify_section_4_handshake.py"),
    ("Section 5 - ClientGetRecord",     "verify_section_5_records.py"),
    ("Section 7 - Employee CRUD",       "verify_section_7_employee.py"),
    ("Section 8 - Manager CRUD",        "verify_section_8_manager.py"),
    ("Section 10 - Real-time Poll",     "verify_section_10_realtime.py"),
]

results = []
total_start = time.time()

print("=" * 70)
print("HANVON PROTOCOL VERIFICATION SUITE")
print("=" * 70)

for label, script in SCRIPTS:
    print(f"\n>>> {label}")
    print("-" * 50)
    path = os.path.join(SCRIPT_DIR, script)
    start = time.time()
    result = subprocess.run(
        ["uv", "run", "python", path],
        capture_output=True, text=True, encoding='utf-8',
        cwd=os.path.dirname(SCRIPT_DIR)
    )
    elapsed = time.time() - start
    if result.returncode == 0:
        # Print last line of output
        lines = result.stdout.strip().split('\n')
        for line in lines:
            print(line)
        results.append((label, "PASS", elapsed))
    else:
        print(result.stdout)
        print(f"STDERR: {result.stderr[:500]}")
        results.append((label, "FAIL", elapsed))

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
total = time.time() - total_start
passed = sum(1 for _, s, _ in results if s == "PASS")
failed = sum(1 for _, s, _ in results if s == "FAIL")
for label, status, elapsed in results:
    icon = "OK" if status == "PASS" else "FAIL"
    print(f"  [{icon}] {label} ({elapsed:.1f}s)")
print(f"\n  Passed: {passed}/{len(results)} | Total time: {total:.1f}s")
sys.exit(0 if failed == 0 else 1)
