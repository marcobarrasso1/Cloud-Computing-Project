# Benchmarks exactly one file size per run (clean results)
import os, time, random
from locust import HttpUser, task, between
from requests.auth import HTTPBasicAuth

USER_PREFIX  = os.getenv("NC_USER_PREFIX", "locust_user")
USER_COUNT   = int(os.getenv("NC_USER_COUNT", "30"))
PASSWORD     = os.getenv("NC_PASS", "test_password1234!")
TEST_DIR     = os.getenv("NC_TEST_DIR", "sizebench")
BENCH_SIZE   = os.getenv("NC_BENCH_SIZE", "1kb")  # one of: 1kb, 512kb, 2mb, 8mb, 32mb, 128mb
TIMEOUT      = (5, 600)

FILES = {
    "1kb":    "/test-data/file_1kb",
    "512kb":  "/test-data/file_512kb",
    "2mb":    "/test-data/file_2mb",
    "8mb":    "/test-data/file_8mb",
    "32mb":   "/test-data/file_32mb",
    "128mb":  "/test-data/file_128mb",
}

class SizeBenchUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        idx = random.randrange(0, USER_COUNT)
        self.user = f"{USER_PREFIX}{idx}"
        self.auth = HTTPBasicAuth(self.user, PASSWORD)
        self.base = f"/remote.php/dav/files/{self.user}"

        # Make a working dir (idempotent)
        self.client.request("MKCOL", f"{self.base}/{TEST_DIR}",
                            auth=self.auth, name="MKCOL bench dir",
                            timeout=TIMEOUT)

        if BENCH_SIZE not in FILES:
            raise RuntimeError(f"Unknown NC_BENCH_SIZE='{BENCH_SIZE}'. Choices: {list(FILES)}")

        self.local_path = FILES[BENCH_SIZE]

        # Seed one file for consistent GET timing
        self.seed_remote = f"{self.base}/{TEST_DIR}/seed_{BENCH_SIZE}.bin"
        with open(self.local_path, "rb") as f:
            self.client.put(self.seed_remote, data=f, auth=self.auth,
                            name=f"PUT seed {BENCH_SIZE}", timeout=TIMEOUT)

    @task(3)
    def upload(self):
        remote = f"{self.base}/{TEST_DIR}/{BENCH_SIZE}_{int(time.time()*1000)}.bin"
        with open(self.local_path, "rb") as f:
            self.client.put(remote, data=f, auth=self.auth,
                            name=f"PUT {BENCH_SIZE}", timeout=TIMEOUT)

    @task(2)
    def download(self):
        self.client.get(self.seed_remote, auth=self.auth,
                        name=f"GET {BENCH_SIZE}", timeout=TIMEOUT)
