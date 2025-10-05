import sys
import os
import re
import time
import threading
import traceback
import inspect
from pathlib import Path

# ensure project root is on sys.path (project_root/tools -> project_root)
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# pattern to detect in the stream
pattern = re.compile(r'Online erfasste Vitaldaten')

# Create an OS-level pipe and dup stdout (fd 1) into the pipe writer so we can
# capture all low-level writes (including C-level writes) that bypass Python's
# sys.stdout/os.write hooks.
orig_fd = os.dup(1)
pipe_r, pipe_w = os.pipe()

# Make read end non-blocking
try:
    os.set_blocking(pipe_r, False)
except Exception:
    pass

# Replace stdout fd with pipe writer
os.dup2(pipe_w, 1)

stop_reader = threading.Event()
captured_buffer = []
buffer_lock = threading.Lock()


def reader_thread():
    """Continuously read from the pipe read-end and inspect the data for the pattern.
    When detected, print a stack trace to stderr (which still points to the terminal)
    and dump a snapshot of the captured text to a temporary file for inspection.
    """
    acc = ""
    last_report = 0
    tmp_path = project_root / 'tools' / 'captured_stdout_snapshot.txt'
    while not stop_reader.is_set():
        try:
            chunk = os.read(pipe_r, 32768)
            if not chunk:
                time.sleep(0.01)
                continue
            try:
                text = chunk.decode('utf-8', errors='replace')
            except Exception:
                text = str(chunk)
            acc += text
            # keep acc manageable
            if len(acc) > 200000:
                acc = acc[-200000:]
            # store into captured buffer for later
            with buffer_lock:
                captured_buffer.append(text)
            # detection heuristics
            if pattern.search(acc) or len(acc) > 50000:
                now = time.time()
                # throttle reports to once every 2 seconds
                if now - last_report > 2:
                    last_report = now
                    # print stack to stderr
                    traceback.print_stack(limit=10, file=sys.stderr)
                    caller = inspect.stack()[2] if len(inspect.stack()) > 2 else inspect.stack()[1]
                    print(f"Captured FD-level stdout writing; caller {caller.filename}:{caller.lineno} in {caller.function}", file=sys.stderr)
                    # dump snapshot for offline inspection
                    try:
                        with open(tmp_path, 'w', encoding='utf-8') as f:
                            f.write(acc)
                        print(f"Wrote snapshot to {tmp_path}", file=sys.stderr)
                    except Exception as e:
                        print(f"Failed to write snapshot: {e}", file=sys.stderr)
        except BlockingIOError:
            time.sleep(0.01)
        except OSError:
            # pipe closed or other OS-level error
            break
        except Exception as e:
            print(f"Reader thread exception: {e}", file=sys.stderr)
            break


reader = threading.Thread(target=reader_thread, daemon=True)
reader.start()


try:
    # import and run main under the redirected stdout
    import main
    main.main()
finally:
    # ask reader to stop and restore original stdout
    stop_reader.set()
    # small sleep to allow reader to drain
    time.sleep(0.1)
    try:
        os.dup2(orig_fd, 1)
    except Exception:
        pass
    # close our pipe fds
    try:
        os.close(pipe_r)
    except Exception:
        pass
    try:
        os.close(pipe_w)
    except Exception:
        pass
    try:
        os.close(orig_fd)
    except Exception:
        pass
