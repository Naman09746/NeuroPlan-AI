"""
Template-Based Study Card Generator — NO API CALLS
Creates comprehensive study materials using curated educational content.
"""

import random
from typing import Dict, Any, Optional

# ============================================================================
# CURATED EDUCATIONAL TEMPLATES
# ============================================================================

STUDY_TIPS_BY_STYLE = {
    "Visual": [
        "Draw concept maps connecting {topic} to related ideas",
        "Use color-coded diagrams to visualize {concept}",
        "Watch video explanations and pause to sketch key diagrams",
        "Create infographics summarizing the main relationships",
        "Use flowcharts to map decision processes in {topic}",
    ],
    "Auditory": [
        "Record yourself explaining {topic} and listen during breaks",
        "Discuss {concept} with peers in study groups",
        "Listen to lecture recordings at 1.25x speed for review",
        "Use mnemonic phrases to remember key formulas",
        "Teach {topic} out loud to an imaginary student",
    ],
    "Kinesthetic": [
        "Solve practice problems hands-on before reading theory for {topic}",
        "Build small projects applying {concept} in code",
        "Use physical flashcards you can shuffle and sort",
        "Walk around while reviewing {topic} concepts mentally",
        "Implement {concept} from scratch to build muscle memory",
    ],
    "Reading/Writing": [
        "Write detailed notes summarizing {topic} in your own words",
        "Create a glossary of key terms for {concept}",
        "Write practice essays explaining {topic} to a beginner",
        "Keep a learning journal tracking insights about {concept}",
        "Rewrite textbook explanations in simpler language",
    ],
}

RESOURCE_TEMPLATES = {
    "Machine Learning": [
        {"title": "Stanford CS229 - Machine Learning", "url": "https://cs229.stanford.edu/", "type": "course"},
        {"title": "3Blue1Brown - Neural Networks", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi", "type": "video"},
        {"title": "Scikit-learn Documentation", "url": "https://scikit-learn.org/stable/", "type": "documentation"},
        {"title": "Kaggle Learn - Intro to ML", "url": "https://www.kaggle.com/learn/intro-to-machine-learning", "type": "hands-on"},
    ],
    "Data Structures": [
        {"title": "MIT 6.006 - Intro to Algorithms", "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/", "type": "course"},
        {"title": "VisuAlgo - Visualizing Algorithms", "url": "https://visualgo.net/", "type": "interactive"},
        {"title": "LeetCode Patterns", "url": "https://leetcode.com/", "type": "practice"},
        {"title": "GeeksforGeeks - DSA", "url": "https://www.geeksforgeeks.org/data-structures/", "type": "article"},
    ],
    "Calculus": [
        {"title": "Khan Academy - Calculus", "url": "https://www.khanacademy.org/math/calculus-1", "type": "course"},
        {"title": "3Blue1Brown - Essence of Calculus", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr", "type": "video"},
        {"title": "Paul's Online Math Notes", "url": "https://tutorial.math.lamar.edu/", "type": "article"},
        {"title": "Desmos Graphing Calculator", "url": "https://www.desmos.com/calculator", "type": "tool"},
    ],
    "Quantum Physics": [
        {"title": "MIT 8.04 - Quantum Mechanics", "url": "https://ocw.mit.edu/courses/8-04-quantum-physics-i-spring-2016/", "type": "course"},
        {"title": "Feynman Lectures", "url": "https://www.feynmanlectures.caltech.edu/", "type": "textbook"},
        {"title": "Quantum Computing Playground", "url": "https://quantum-computing.ibm.com/", "type": "interactive"},
    ],
    "Operating Systems": [
        {"title": "OSTEP - Operating Systems: Three Easy Pieces", "url": "https://pages.cs.wisc.edu/~remzi/OSTEP/", "type": "textbook"},
        {"title": "MIT 6.S081 - Operating System Engineering", "url": "https://pdos.csail.mit.edu/6.S081/2021/", "type": "course"},
        {"title": "Linux Kernel Documentation", "url": "https://www.kernel.org/doc/html/latest/", "type": "documentation"},
    ],
    "Web Development": [
        {"title": "MDN Web Docs", "url": "https://developer.mozilla.org/", "type": "documentation"},
        {"title": "freeCodeCamp", "url": "https://www.freecodecamp.org/", "type": "hands-on"},
        {"title": "The Odin Project", "url": "https://www.theodinproject.com/", "type": "course"},
        {"title": "JavaScript.info", "url": "https://javascript.info/", "type": "article"},
    ],
    "Linear Algebra": [
        {"title": "3Blue1Brown - Essence of Linear Algebra", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab", "type": "video"},
        {"title": "MIT 18.06 - Linear Algebra", "url": "https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/", "type": "course"},
        {"title": "Immersive Linear Algebra", "url": "http://immersivemath.com/ila/index.html", "type": "interactive"},
    ],
    "Cloud Computing": [
        {"title": "AWS Cloud Practitioner Essentials", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "type": "course"},
        {"title": "Google Cloud Training", "url": "https://cloud.google.com/training", "type": "course"},
        {"title": "Cloud Resume Challenge", "url": "https://cloudresumechallenge.dev/", "type": "hands-on"},
    ],
    "System Design": [
        {"title": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "type": "textbook"},
        {"title": "Grokking the System Design Interview", "url": "https://www.designgurus.io/course/grokking-the-system-design-interview", "type": "course"},
        {"title": "High Scalability Blog", "url": "http://highscalability.com/", "type": "article"},
    ],
    "Cybersecurity": [
        {"title": "TryHackMe", "url": "https://tryhackme.com/", "type": "hands-on"},
        {"title": "Cybrary", "url": "https://www.cybrary.it/", "type": "course"},
        {"title": "OWASP Juice Shop", "url": "https://owasp.org/www-project-juice-shop/", "type": "hands-on"},
    ],
    "Deep Learning": [
        {"title": "DeepLearning.AI - Neural Networks and Deep Learning", "url": "https://www.coursera.org/learn/neural-networks-deep-learning", "type": "course"},
        {"title": "PyTorch Tutorials", "url": "https://pytorch.org/tutorials/", "type": "documentation"},
        {"title": "Fast.ai", "url": "https://www.fast.ai/", "type": "course"},
    ],
    "Mobile Development": [
        {"title": "Flutter Documentation", "url": "https://docs.flutter.dev/", "type": "documentation"},
        {"title": "Android Developers", "url": "https://developer.android.com/", "type": "documentation"},
        {"title": "iOS Dev Weekly", "url": "https://iosdevweekly.com/", "type": "article"},
    ],
    "Microeconomics": [
        {"title": "MIT OCW - Principles of Microeconomics", "url": "https://ocw.mit.edu/courses/14-01sc-principles-of-microeconomics-fall-2011/", "type": "course"},
        {"title": "Marginal Revolution University", "url": "https://mru.org/", "type": "video"},
    ],
    "Database Management": [
        {"title": "CMU 15-445/645 - Intro to Database Systems", "url": "https://15445.courses.cs.cmu.edu/", "type": "course"},
        {"title": "SQLZoo", "url": "https://sqlzoo.net/", "type": "interactive"},
        {"title": "PostgreSQL Documentation", "url": "https://www.postgresql.org/docs/", "type": "documentation"},
    ],
}

FORMULA_TEMPLATES = {
    "Machine Learning": {
        "Linear Regression": ["y = wx + b", "MSE = (1/n) Σ(yᵢ - ŷᵢ)²", "∂L/∂w = -(2/n) Σxᵢ(yᵢ - ŷᵢ)"],
        "Logistic Regression": ["σ(z) = 1/(1 + e^(-z))", "L = -[y·log(ŷ) + (1-y)·log(1-ŷ)]"],
        "default": ["accuracy = TP+TN / (TP+TN+FP+FN)", "F1 = 2·(P·R)/(P+R)"],
    },
    "Calculus": {
        "Differentiation Rules": ["d/dx[xⁿ] = nxⁿ⁻¹", "d/dx[f·g] = f'g + fg'", "(f∘g)' = f'(g(x))·g'(x)"],
        "Integration Techniques": ["∫xⁿdx = xⁿ⁺¹/(n+1) + C", "∫udv = uv - ∫vdu"],
        "default": ["lim(h→0) [f(x+h) - f(x)]/h", "∫ₐᵇ f(x)dx = F(b) - F(a)"],
    },
    "Linear Algebra": {
        "Determinants": ["det(A) = Σ(-1)^(i+j)·aᵢⱼ·Mᵢⱼ", "det(AB) = det(A)·det(B)"],
        "Eigenvalues and Eigenvectors": ["Av = λv", "det(A - λI) = 0"],
        "default": ["(AB)ᵀ = BᵀAᵀ", "A⁻¹A = I"],
    },
    "Quantum Physics": {
        "Schrödinger Equation": ["iℏ ∂ψ/∂t = Ĥψ", "Ĥψ = Eψ (time-independent)"],
        "Uncertainty Principle": ["ΔxΔp ≥ ℏ/2", "ΔEΔt ≥ ℏ/2"],
        "default": ["⟨A⟩ = ⟨ψ|Â|ψ⟩", "P = |⟨φ|ψ⟩|²"],
    },
    "Cloud Computing": {
        "default": ["Cost = Usage x Rate", "Reliability = 1 - (Downtime / Total Time)"],
    },
    "System Design": {
        "default": ["Throughput = Tasks / Time", "Response Time = Service + Wait"],
    },
    "Cybersecurity": {
        "default": ["Risk = Probability x Impact", "Entropy = -Σ p(x) log p(x)"],
    },
    "Deep Learning": {
        "Neural Networks Foundation": ["y = f(Wx + b)", "L = Σ(y - ŷ)²"],
        "default": ["w = w - η ∂L/∂w"],
    },
    "Microeconomics": {
        "Supply and Demand": ["Qₛ = Qd (Equilibrium)", "PEd = (%ΔQd) / (%ΔP)"],
        "default": ["Utility = U(x, y)", "MC = dTC/dQ"],
    },
    "Database Management": {
        "default": ["Selectivity = Cards(A) / Cards(R)"],
    },
}

PRACTICE_PROBLEMS = {
    "easy": [
        "Define {concept} in your own words and give a real-world example.",
        "List three key properties of {concept}.",
        "Compare {concept} with {alt_concept} — what are the similarities?",
    ],
    "medium": [
        "Solve a step-by-step problem involving {concept}.",
        "Explain why {concept} is important in the context of {topic}.",
        "Given a specific scenario, apply {concept} to reach a solution.",
        "Identify and correct errors in a provided solution involving {concept}.",
    ],
    "hard": [
        "Derive {concept} from first principles.",
        "Design a system that optimally uses {concept} under constraints.",
        "Analyze the tradeoffs between {concept} and {alt_concept} in production.",
        "Prove or disprove: {concept} always leads to optimal results.",
        "Write a research-level analysis of recent advances in {topic}.",
    ],
}


def generate_study_card(topic_name: str, subject: str, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate a complete study card WITHOUT any API call.
    Uses curated content + style-adaptive formatting.
    """
    style = profile.get("learning_style", "Visual")
    level = profile.get("level", "Beginner")
    concepts = profile.get("key_concepts", ["fundamental principles", "core mechanisms"])
    
    if isinstance(concepts, str):
        concepts = [concepts]
    if not concepts:
        concepts = ["core concepts", "fundamental ideas"]
    
    # 1. Generate summary
    summaries = [
        f"{topic_name} is a foundational concept in {subject} that connects {concepts[0]} with practical applications. Understanding this topic builds the framework for more advanced study.",
        f"This module explores {topic_name} within {subject}, focusing on how {concepts[0]} relates to real-world problem solving. Mastery here is essential for progression.",
        f"{topic_name} in {subject} covers the critical relationship between {concepts[0]} and {concepts[-1] if len(concepts) > 1 else 'its applications'}. This knowledge forms the basis for advanced work.",
    ]
    
    # 2. Style-adapted tips
    tips_pool = STUDY_TIPS_BY_STYLE.get(style, STUDY_TIPS_BY_STYLE["Visual"])
    tips = [t.format(topic=topic_name, concept=concepts[0]) for t in random.sample(tips_pool, min(3, len(tips_pool)))]
    
    # 3. Subject-specific formulas
    formula_bank = FORMULA_TEMPLATES.get(subject, {})
    formulas = formula_bank.get(topic_name, formula_bank.get("default", [f"No specific formula for {topic_name}"]))
    
    # 4. Resources
    resources = RESOURCE_TEMPLATES.get(subject, [{"title": f"{subject} Wikipedia", "url": f"https://en.wikipedia.org/wiki/{subject.replace(' ', '_')}", "type": "article"}])
    
    # 5. Practice problems adapted to difficulty
    diff = "easy" if level == "Beginner" else ("hard" if level == "Advanced" else "medium")
    problems_pool = PRACTICE_PROBLEMS[diff]
    alt_concept = concepts[1] if len(concepts) > 1 else "alternative approaches"
    problems = [
        p.format(concept=concepts[0], alt_concept=alt_concept, topic=topic_name)
        for p in random.sample(problems_pool, min(3, len(problems_pool)))
    ]
    
    return {
        "summary": random.choice(summaries),
        "key_concepts": concepts,
        "formulas": formulas[:3],
        "study_tips": tips,
        "resources": random.sample(resources, min(2, len(resources))),
        "practice_problems": problems,
    }
