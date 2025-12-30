"""Logging module for send operations."""
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), "send_log.txt")


def ensure_log_file() -> None:
    """Create log file if it doesn't exist."""
    if not os.path.exists(LOG_PATH):
        open(LOG_PATH, "a", encoding="utf-8").close()


def log_send(
    command: str,
    func_name: str,
    command_dt: str,
    send_status: str,
    send_success_dt: str,
    error_reason: str = "",
) -> None:
    """
    Write a log entry for a send operation.
    
    Format: command_dt,command,status_func,success_dt[,error_reason]
    error_reason is only appended when status is 'fail' and reason is provided.
    """
    if send_status == "fail" and error_reason:
        line = f"{command_dt},{command},{send_status}_{func_name},{send_success_dt},{error_reason}\n"
    else:
        line = f"{command_dt},{command},{send_status}_{func_name},{send_success_dt}\n"
    
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as exc:
        print(f"Failed to write log: {exc}")
