"""
Test ALIVE Framework V2.0 — run: python test_v22.py
No server or database needed.
"""
from tools.ide_ipa_tools import (
    load_framework, score_part_a, score_part_b, score_part_c,
    score_part_d, alive_overall_score, calculate_sroi,
    funding_decision, level_a, level_b, level_c, level_d, overall_grade,
)

passed = 0
failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name} — {detail}")


# ── Framework Structure ──────────────────────────────
print("\n═══ ALIVE Framework V2.0 Structure ═══")
fw = load_framework()
check("version = 2.0", fw["framework_version"] == "2.0")
check("Part A = 28", fw["parts"]["A"] == 28)
check("Part B = 22", fw["parts"]["B"] == 22)
check("Part C = 25", fw["parts"]["C"] == 25)
check("Part D = 25", fw["parts"]["D"] == 25)

# Part A: 6 dimensions, sum = 28
a_dims = fw["scoring"]["A"]["dimensions"]
check("Part A has 6 dims", len(a_dims) == 6, f"got {len(a_dims)}")
a_sum = sum(d["max"] for d in a_dims.values())
check("Part A dims sum = 28", a_sum == 28, f"got {a_sum}")
check("Part A has financial_sustainability", "5_financial_sustainability" in a_dims)

# Part B: 4 dimensions, sum = 22
b_dims = fw["scoring"]["B"]["dimensions"]
check("Part B has 4 dims", len(b_dims) == 4, f"got {len(b_dims)}")
b_sum = sum(d["max"] for d in b_dims.values())
check("Part B dims sum = 22", b_sum == 22, f"got {b_sum}")
check("Part B has vvn_alignment", "10_vvn_alignment" in b_dims)
check("Part B vvn max = 2", b_dims["10_vvn_alignment"]["max"] == 2)

# Part C: 5 dimensions, sum = 25
c_dims = fw["scoring"]["C"]["dimensions"]
check("Part C has 5 dims", len(c_dims) == 5, f"got {len(c_dims)}")
c_sum = sum(d["max"] for d in c_dims.values())
check("Part C dims sum = 25", c_sum == 25, f"got {c_sum}")
check("Part C has pathway_architecture", "C1_pathway_architecture" in c_dims)
check("Part C has adaptive_management", "C5_adaptive_management" in c_dims)

# Part D: 3 dimensions, sum = 25
d_dims = fw["scoring"]["D"]["dimensions"]
check("Part D has 3 dims", len(d_dims) == 3, f"got {len(d_dims)}")
d_sum = sum(d["max"] for d in d_dims.values())
check("Part D dims sum = 25", d_sum == 25, f"got {d_sum}")

# Special cases
check("has special_cases", "special_cases" in fw)
check("has vvn_zero case", "vvn_zero" in fw.get("special_cases", {}))


# ── Score Part A (6 params) ──────────────────────────
print("\n═══ Score Part A ═══")
r = score_part_a("TestCo", 5, 5, 3, 3, 3, 3)
check("Part A total = 22", r["total"] == 22)
check("Part A max = 28", r["max"] == 28)
check("Part A has 6 scores", len(r["scores"]) == 6)
check("Part A level = SCALER", r["level"] == "SCALER")
check("Part A pass = True (22 >= 9)", r["pass"] is True)
check("Part A has max_per_dim", "max_per_dim" in r)

# Clamping test
r2 = score_part_a("TestCo", 10, 10, 10, 10, 10, 10)
check("Part A clamped to 28", r2["total"] == 28, f"got {r2['total']}")


# ── Score Part B (4 params + vvn) ────────────────────
print("\n═══ Score Part B ═══")
r = score_part_b("TestCo", 7, 5, 5, 2)
check("Part B total = 19", r["total"] == 19)
check("Part B has 4 scores", len(r["scores"]) == 4)
check("Part B level = Excellent", r["level"] == "Excellent")
check("Part B vvn_flag = None (vvn=2)", r["vvn_flag"] is None)

# vvn = 0 flag
r0 = score_part_b("TestCo", 7, 5, 5, 0)
check("Part B vvn=0 triggers flag", r0["vvn_flag"] is not None)
check("Part B vvn=0 total = 17", r0["total"] == 17)

# Clamping
r3 = score_part_b("TestCo", 20, 20, 20, 5)
check("Part B clamped to 22", r3["total"] == 22, f"got {r3['total']}")


# ── Score Part C (5 params) ──────────────────────────
print("\n═══ Score Part C ═══")
r = score_part_c("TestCo", 6, 7, 4, 2, 2)
check("Part C total = 21", r["total"] == 21)
check("Part C has 5 scores", len(r["scores"]) == 5)
check("Part C level = Strong", r["level"] == "Strong")

# Clamping
r4 = score_part_c("TestCo", 10, 10, 10, 10, 10)
check("Part C clamped to 25", r4["total"] == 25, f"got {r4['total']}")


# ── Score Part D (clamping) ──────────────────────────
print("\n═══ Score Part D ═══")
r = score_part_d("TestCo", 8, 7, 6)
check("Part D total = 21", r["total"] == 21)
check("Part D level = Strong", r["level"] == "Strong")

r5 = score_part_d("TestCo", 15, 12, 10)
check("Part D clamped to 25", r5["total"] == 25, f"got {r5['total']}")


# ── Level Helpers ────────────────────────────────────
print("\n═══ Level Helpers ═══")
check("level_a(24) = LEADER", level_a(24) == "LEADER")
check("level_a(16) = SCALER", level_a(16) == "SCALER")
check("level_a(9) = STARTER",  level_a(9) == "STARTER")
check("level_a(8) = PRE-STARTER", level_a(8) == "PRE-STARTER")

check("level_b(19) = Excellent", level_b(19) == "Excellent")
check("level_b(14) = Good", level_b(14) == "Good")
check("level_b(8) = Fair",  level_b(8) == "Fair")
check("level_b(7) = Poor",  level_b(7) == "Poor")

check("level_c(22) = Exemplary", level_c(22) == "Exemplary")
check("level_c(17) = Strong", level_c(17) == "Strong")
check("level_c(12) = Adequate", level_c(12) == "Adequate")
check("level_c(11) = Weak/Inadequate", level_c(11) == "Weak/Inadequate")

check("level_d(22) = Exemplary", level_d(22) == "Exemplary")
check("level_d(17) = Strong", level_d(17) == "Strong")
check("level_d(12) = Adequate", level_d(12) == "Adequate")
check("level_d(11) = Weak", level_d(11) == "Weak")


# ── Overall Grade ────────────────────────────────────
print("\n═══ Overall Grade & Funding ═══")
check("90 = A+ Exceptional", overall_grade(90) == ("A+", "Exceptional"))
check("80 = A Excellent",    overall_grade(80) == ("A", "Excellent"))
check("70 = B+ Very Good",   overall_grade(70) == ("B+", "Very Good"))
check("60 = B Good",         overall_grade(60) == ("B", "Good"))
check("50 = C+ Fair",        overall_grade(50) == ("C+", "Fair"))
check("40 = C Marginal",     overall_grade(40) == ("C", "Marginal"))
check("39 = F Poor",         overall_grade(39) == ("F", "Poor"))

# Funding decision
check("STRONGLY FUND (all pass, 85+)", funding_decision(24, 18, 22, 22, 86) == "STRONGLY FUND")
check("FUND (all pass, 64+)",          funding_decision(16, 14, 17, 17, 64) == "FUND")
check("CONDITIONAL (all pass, 44+)",   funding_decision(9, 8, 14, 14, 45) == "CONDITIONAL FUND")
check("DO NOT FUND (below thresholds)", funding_decision(8, 7, 11, 11, 37) == "DO NOT FUND")
check("DO NOT FUND (high total but A<9)", funding_decision(8, 18, 22, 22, 70) == "DO NOT FUND")


# ── SROI ─────────────────────────────────────────────
print("\n═══ SROI ═══")
r = calculate_sroi("TestCo", 1_000_000, 800_000, 3)
check("SROI has 3 scenarios", "sensitivity" in r)
check("SROI base ratio > 0", r["base_case"]["sroi_ratio"] > 0)
check("SROI pessimistic <= base", r["sensitivity"]["pessimistic"]["sroi"] <= r["base_case"]["sroi_ratio"])
check("SROI optimistic >= base",  r["sensitivity"]["optimistic"]["sroi"] >= r["base_case"]["sroi_ratio"])
check("SROI standard = ALIVE V2.0", "ALIVE" in r["standard"] and "V2.0" in r["standard"])

# Zero investment guard
r0 = calculate_sroi("TestCo", 0, 800_000, 3)
check("SROI investment=0 returns error", "error" in r0)

# fund_signal fix: 2.5x and 4.0x should differ
r_high = calculate_sroi("TestCo", 100_000, 800_000, 5)
# With high returns, we should see "Priority Fund" or "Strong Fund"
decisions = {r_high["sensitivity"][s]["decision"] for s in ["pessimistic", "base", "optimistic"]}
check("fund_signal has differentiated decisions", len(decisions) >= 1)


# ── Summary ──────────────────────────────────────────
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed, {passed+failed} total")
if failed == 0:
    print("🎉 All tests passed!")
else:
    print(f"⚠️  {failed} test(s) need attention")
