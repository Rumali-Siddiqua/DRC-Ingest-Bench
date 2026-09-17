"""Plot report tokens vs. violation count from the verified scale sweep (Run 4)."""
import matplotlib
matplotlib.use("Agg")  # save to file only; no window needed
import matplotlib.pyplot as plt

markers = [384, 2400, 9600, 38400]
header = 48992
items = [41852, 262050, 1067980, 4381560]
total = [header + i for i in items]

fig, ax = plt.subplots(figsize=(6, 4))
ax.loglog(markers, total, "o-", label="Total report tokens")
ax.loglog(markers, items, "s--", label="Marker tokens")
ax.axhline(header, color="gray", linestyle=":", label="Rule catalogue (fixed)")
ax.set_xlabel("Violations (markers)")
ax.set_ylabel("Tokens (cl100k_base)")
ax.set_title("KLayout marker database cost vs. violation count")
ax.legend()
ax.grid(True, which="both", alpha=0.3)
fig.tight_layout()
fig.savefig("docs/scale_tokens.png", dpi=150)
print("Saved docs/scale_tokens.png")
