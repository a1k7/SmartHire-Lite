import random

# 🔮 Hiring success prediction
def predict_success(score, experience, missing_count):
    base = score

    # penalize missing skills
    penalty = missing_count * 3

    # experience boost
    exp_boost = min(experience * 2, 15)

    success = base - penalty + exp_boost

    return max(min(success, 100), 0)


# 🚀 Growth potential (unique feature)
def growth_potential(missing_count, experience):
    if experience < 2 and missing_count <= 5:
        return "📈 High Growth Potential"
    elif experience >= 2 and missing_count <= 3:
        return "⚡ Stable Performer"
    else:
        return "⚠️ Limited Growth"


# 🧾 Explainability engine
def explain_decision(score, matched, missing):
    reasons = []

    if score > 75:
        reasons.append("Strong alignment with job requirements")
    else:
        reasons.append("Partial alignment")

    if matched:
        reasons.append(f"Key strengths: {', '.join(matched[:3])}")

    if missing:
        reasons.append(f"Critical gaps: {', '.join(missing[:3])}")

    return " | ".join(reasons)


# 🔮 What-if simulation
def simulate_improvement(score, missing_count):
    improvement = score + (missing_count * 5)
    return min(improvement, 100)