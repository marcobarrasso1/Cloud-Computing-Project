import sys, os
import pandas as pd
import matplotlib.pyplot as plt

csv = sys.argv[1] if len(sys.argv) > 1 else "size_times.csv"
if not os.path.exists(csv):
    raise FileNotFoundError(f"CSV not found: {csv}")

df = pd.read_csv(csv)

# keep only success codes (2xx)
df = df[df["code"].astype(str).str.startswith("2")]

order = ["1KB","512KB","2MB","8MB","32MB","128MB"]
df["size_label"] = pd.Categorical(df["size_label"], order, ordered=True)

up = df[df["op"]=="upload"].sort_values("size_label")
dl = df[df["op"]=="download"].sort_values("size_label")

plt.figure()
plt.plot(up["size_label"], up["time_s"], marker="o", label="Upload time")
plt.plot(dl["size_label"], dl["time_s"], marker="o", label="Download time")
plt.xlabel("File size")
plt.ylabel("Time (s)")
plt.title("Upload/Download time vs file size ")
plt.grid(True)
plt.legend()
plt.tight_layout()

out = "size_vs_time_curl.png"
plt.savefig(out, dpi=150)
print(f"Wrote {out}")
