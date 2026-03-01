
class LockAcquisitionError(Exception):
    """Exception raised when lock acquisition fails within the timeout."""
    pass

class PARALLEL_LOCK:
    
    def __init__(self, lock, timeout):
        self.lock = lock
        self.timeout = timeout

    def __enter__(self):
        if not self.lock.acquire(timeout=self.timeout):
            raise LockAcquisitionError("Could not acquire lock within the timeout")
        return True  # Indicate successful lock acquisition

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()