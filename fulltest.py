import send_icu
import send_ipd
import send_or

print("=" * 60)
print("FULLTEST: Testing all send functions")
print("=" * 60)

print("\n[TEST 1] Testing send_icu...")
command_dt, send_status, send_success_dt, error_reason = send_icu.send()
print(f"Result: status={send_status}, dt={command_dt}, success_dt={send_success_dt}, reason={error_reason}")

print("\n[TEST 2] Testing send_ipd...")
command_dt, send_status, send_success_dt, error_reason = send_ipd.send()
print(f"Result: status={send_status}, dt={command_dt}, success_dt={send_success_dt}, reason={error_reason}")

print("\n[TEST 3] Testing send_or...")
command_dt, send_status, send_success_dt, error_reason = send_or.send()
print(f"Result: status={send_status}, dt={command_dt}, success_dt={send_success_dt}, reason={error_reason}")

print("\n" + "=" * 60)
print("FULLTEST COMPLETED")
print("=" * 60)
