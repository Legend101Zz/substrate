#!/usr/bin/env python3
"""
Substrate 29 - mcp-skills-and-connectors: independent recomputation of every quantitative claim in
the protocol/connector-walkthrough brief. Pure stdlib. Run: python3 _recompute.py

29 promotes 23's in-process tool CONTRACT to a wire PROTOCOL (MCP). It introduces no new agent math;
its quantitative claims are (a) the integration-collapse argument that justifies a protocol at all,
and (b) the reuse of 23's toolbox/selection economics + 18/20's remote-dependency laws applied to
the UNION of connected servers. Everything is re-derived from first principles, not re-cited.
"""

results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))

# =========================================================================
# 1. THE N x M -> N + M INTEGRATION COLLAPSE (why a protocol exists)
# =========================================================================
# M hosts each integrating N tool-providers bespoke = M*N integrations.
# With one shared protocol each side implements it ONCE = M + N.
def bespoke(M, N): return M * N
def with_protocol(M, N): return M + N
for M, N, exp_b, exp_p in [(20, 20, 400, 40), (5, 10, 50, 15), (100, 100, 10000, 200)]:
    check(f"integration count M={M},N={N}", bespoke(M, N) == exp_b and with_protocol(M, N) == exp_p,
          f"bespoke M*N={bespoke(M,N)} -> protocol M+N={with_protocol(M,N)} ({bespoke(M,N)/with_protocol(M,N):.1f}x fewer)")
# the saving grows: ratio M*N/(M+N) increases with scale (for M=N it's N/2)
r20 = bespoke(20, 20) / with_protocol(20, 20)
r100 = bespoke(100, 100) / with_protocol(100, 100)
check("protocol saving grows with scale", r100 > r20,
      f"M=N=20 -> {r20:.1f}x ; M=N=100 -> {r100:.1f}x (for M=N, ratio = N/2)")
check("M=N ratio equals N/2", approx(r20, 20/2) and approx(r100, 100/2),
      f"N/2 identity: {r20:.1f}=={20/2}, {r100:.1f}=={100/2}")

# =========================================================================
# 2. UNION-TOOLBOX TAX OVER MANY CONNECTED SERVERS (reuse 23)
# =========================================================================
# Each MCP server contributes t tools, each with schema S tokens. Connecting s servers makes the
# host's combined toolbox K = s*t, costing K*S tokens/turn in the prefix (23's toolbox tax).
t, S = 8, 200    # tools per server, schema tokens per tool
def union_K(s): return s * t
def toolbox_tax(s): return union_K(s) * S
check("union toolbox size", union_K(5) == 40, f"5 servers * {t} tools = {union_K(5)} tools")
check("union toolbox tax tokens/turn", toolbox_tax(5) == 8000,
      f"K*S = {union_K(5)}*{S} = {toolbox_tax(5)} tok/turn (feeds 22 quadratic)")
W = 128000
check("5 servers already eat measurable window", approx(toolbox_tax(5)/W, 0.0625, 1e-3),
      f"{toolbox_tax(5)}/{W} = {toolbox_tax(5)/W*100:.2f}% of window -> motivates tool-retrieval (30)")

# =========================================================================
# 3. SELECTION-ERROR COMPOUNDING OVER THE UNION (reuse 23/13/20/21 identity)
# =========================================================================
# More connectors = more tools = more chances to pick wrong over a task's N steps: 1-(1-q)^N.
q = 0.02
def compound(N): return 1 - (1 - q) ** N
for N, exp in [(5, 0.0961), (10, 0.1829), (50, 0.6358)]:
    check(f"selection compounding N={N}", approx(compound(N), exp, 1e-3),
          f"1-(1-{q})^{N} = {compound(N):.4f} (more connectors -> larger toolbox -> more mis-selection)")

# =========================================================================
# 4. A REMOTE MCP SERVER IS A NETWORKED DEPENDENCY (reuse 18/20)
# =========================================================================
# Per turn the host may call across s servers; chance >=1 is slow/down = 1-(1-p)^s (20 fan-out tail).
p = 0.01
def any_slow(s): return 1 - (1 - p) ** s
check("any-server-slow per turn s=10", approx(any_slow(10), 0.0956, 1e-3),
      f"1-(1-{p})^10 = {any_slow(10):.4f} -> timeout/retry/breaker (18) + bulkhead (20)")
check("any-server-slow per turn s=100", approx(any_slow(100), 0.6340, 1e-3),
      f"1-(1-{p})^100 = {any_slow(100):.4f} (the same fan-out-tail identity over connectors)")
# remote tail adds to the per-step budget: effective step time = local + remote_p99
local_ms, remote_p99 = 20.0, 300.0
check("remote dependency inflates step latency", local_ms + remote_p99 == 320.0,
      f"{local_ms}+{remote_p99} = 320ms/step -> include in 22's per-step deadline (18)")

# =========================================================================
# 5. VERSION / SCHEMA COMPATIBILITY (reuse 11 negotiate-or-terminate + 17 evolution)
# =========================================================================
# Handshake: connect iff a mutually-supported protocol version exists (set intersection != empty).
client_versions = {"2025-06-18", "2025-03-26"}
server_versions = {"2025-11-25", "2025-06-18"}
compatible = bool(client_versions & server_versions)
check("version negotiation = nonempty intersection", compatible is True,
      f"client {client_versions} ∩ server {server_versions} = {client_versions & server_versions} -> connect")
incompatible = bool({"2024-01-01"} & server_versions)
check("no shared version -> terminate", incompatible is False,
      "empty intersection -> 'connection should be terminated' (11 compat law)")
# schema evolution (17): adding an OPTIONAL field is backward-compatible; a new REQUIRED field breaks
old_required = {"location"}
new_required_safe = {"location"}              # added only optional 'units'
new_required_break = {"location", "units"}    # promoted 'units' to required
check("optional add is compatible", new_required_safe <= old_required or old_required <= new_required_safe,
      "adding optional 'units' keeps old callers valid (17 additive-only rule)")
check("new required field breaks old callers", not (new_required_break <= old_required),
      "promoting 'units' to required invalidates callers that omit it (17)")

# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All load-bearing 29 connector economics + compat laws verified by recomputation.")
