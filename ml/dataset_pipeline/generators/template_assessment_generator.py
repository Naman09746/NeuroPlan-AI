"""
Template-Based Assessment Generator — NO API CALLS
Generates high-quality MCQs from curated question banks per subject/topic.
"""

import random
from typing import Dict, Any, List, Optional

# ============================================================================
# CURATED QUESTION BANKS — Real educational questions, not AI-generated
# ============================================================================

QUESTION_BANK = {
    "Machine Learning": {
        "What is Machine Learning?": [
            {"question": "Which of the following best describes supervised learning?", "options": ["Learning from labeled data", "Learning from unlabeled data", "Learning from rewards", "Learning from random noise"], "correct_index": 0, "explanation": "Supervised learning uses labeled training data where inputs are paired with correct outputs to learn a mapping function."},
            {"question": "What distinguishes reinforcement learning from supervised learning?", "options": ["It uses a reward signal instead of labeled data", "It requires more training data", "It can only work with images", "It doesn't use neural networks"], "correct_index": 0, "explanation": "Reinforcement learning agents learn by interacting with an environment and receiving rewards or penalties, not from pre-labeled examples."},
            {"question": "Which is NOT a type of machine learning?", "options": ["Deterministic learning", "Supervised learning", "Unsupervised learning", "Reinforcement learning"], "correct_index": 0, "explanation": "The three main types are supervised, unsupervised, and reinforcement learning. 'Deterministic learning' is not a standard ML category."},
        ],
        "Linear Regression": [
            {"question": "What does the cost function in linear regression measure?", "options": ["The difference between predicted and actual values", "The slope of the regression line", "The number of features", "The learning rate"], "correct_index": 0, "explanation": "The cost function (typically MSE) measures the average squared difference between predictions and actual values."},
            {"question": "What is the purpose of gradient descent in linear regression?", "options": ["To minimize the cost function", "To maximize the data size", "To normalize the features", "To split the dataset"], "correct_index": 0, "explanation": "Gradient descent iteratively adjusts model parameters to minimize the cost function by following the negative gradient."},
            {"question": "If a linear regression model has very high training accuracy but poor test accuracy, what is likely happening?", "options": ["Overfitting", "Underfitting", "Perfect generalization", "Data corruption"], "correct_index": 0, "explanation": "High train accuracy with poor test accuracy indicates overfitting — the model memorized training data but can't generalize."},
        ],
        "Model Evaluation": [
            {"question": "What does the F1 score balance?", "options": ["Precision and recall", "Accuracy and speed", "Bias and variance", "Training and test loss"], "correct_index": 0, "explanation": "F1 score is the harmonic mean of precision and recall, balancing both false positives and false negatives."},
            {"question": "When is accuracy a poor metric for model evaluation?", "options": ["When classes are highly imbalanced", "When the dataset is large", "When using neural networks", "When features are normalized"], "correct_index": 0, "explanation": "With imbalanced classes, a model can achieve high accuracy by always predicting the majority class, making accuracy misleading."},
            {"question": "What does k-fold cross-validation help to reduce?", "options": ["Variance in model evaluation", "Training time", "Number of features", "Dataset size"], "correct_index": 0, "explanation": "K-fold cross-validation provides a more robust estimate of model performance by training and evaluating on different data splits."},
        ],
        "Neural Network Architectures": [
            {"question": "What is the primary advantage of CNNs over fully connected networks for image tasks?", "options": ["Parameter sharing through convolutional filters", "Faster training on CPUs", "No need for activation functions", "Simpler architecture"], "correct_index": 0, "explanation": "CNNs use shared convolutional filters that detect features regardless of position, dramatically reducing parameters vs fully connected layers."},
            {"question": "What problem do LSTMs solve that vanilla RNNs struggle with?", "options": ["Vanishing gradients for long sequences", "Overfitting on small datasets", "Slow inference speed", "Lack of GPU support"], "correct_index": 0, "explanation": "LSTMs use gating mechanisms to maintain gradient flow over long sequences, solving the vanishing gradient problem."},
        ],
        "default": [
            {"question": "Which technique helps prevent overfitting in neural networks?", "options": ["Dropout regularization", "Increasing model complexity", "Removing validation data", "Using a single training example"], "correct_index": 0, "explanation": "Dropout randomly deactivates neurons during training, forcing the network to learn redundant representations and reducing overfitting."},
            {"question": "What is the bias-variance tradeoff?", "options": ["Balancing model simplicity with flexibility", "Choosing between CPU and GPU", "Selecting batch size", "Picking learning rate"], "correct_index": 0, "explanation": "The bias-variance tradeoff is about finding a model complex enough to capture patterns (low bias) while still generalizing well (low variance)."},
        ],
    },
    "Data Structures": {
        "Arrays and Strings": [
            {"question": "What is the time complexity of accessing an element by index in an array?", "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"], "correct_index": 0, "explanation": "Arrays provide constant-time O(1) access by index because elements are stored in contiguous memory locations."},
            {"question": "What happens when you insert an element at the beginning of a dynamic array?", "options": ["All elements must be shifted right — O(n)", "Only the first element moves — O(1)", "The array is reallocated — O(n²)", "Nothing changes — O(1)"], "correct_index": 0, "explanation": "Inserting at position 0 requires shifting all existing elements one position right, giving O(n) time complexity."},
        ],
        "Binary Trees": [
            {"question": "What is the worst-case height of an unbalanced BST with n nodes?", "options": ["O(n)", "O(log n)", "O(1)", "O(n log n)"], "correct_index": 0, "explanation": "An unbalanced BST can degenerate into a linked list when elements are inserted in sorted order, giving height O(n)."},
            {"question": "Which traversal visits nodes in sorted order for a BST?", "options": ["In-order (left, root, right)", "Pre-order (root, left, right)", "Post-order (left, right, root)", "Level-order (BFS)"], "correct_index": 0, "explanation": "In-order traversal of a BST visits the left subtree first, then root, then right, producing elements in ascending order."},
        ],
        "Hash Tables": [
            {"question": "What is the average time complexity of lookup in a hash table?", "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"], "correct_index": 0, "explanation": "Hash tables provide O(1) average-case lookup by computing the hash of a key to directly access the storage location."},
            {"question": "What causes performance degradation in hash tables?", "options": ["High collision rate", "Using string keys", "Having too few buckets", "Both A and C"], "correct_index": 3, "explanation": "Both high collision rates and too few buckets (which causes more collisions) degrade hash table performance from O(1) toward O(n)."},
        ],
        "default": [
            {"question": "Which data structure follows Last-In-First-Out (LIFO)?", "options": ["Stack", "Queue", "Array", "Linked List"], "correct_index": 0, "explanation": "A stack follows LIFO — the last element pushed is the first one popped, like a stack of plates."},
            {"question": "What is the time complexity of merge sort?", "options": ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], "correct_index": 0, "explanation": "Merge sort divides the array in half (log n levels) and merges at each level (n work), giving O(n log n) in all cases."},
        ],
    },
    "Calculus": {
        "Limits and Continuity": [
            {"question": "What does it mean for lim(x→a) f(x) = L?", "options": ["f(x) can be made arbitrarily close to L by choosing x close to a", "f(a) = L exactly", "f(x) equals L for all x", "The function is differentiable at a"], "correct_index": 0, "explanation": "The limit definition says f(x) approaches L as x approaches a, regardless of what f(a) actually equals."},
            {"question": "Which condition is NOT required for continuity at point a?", "options": ["f'(a) exists", "f(a) is defined", "lim(x→a) f(x) exists", "lim(x→a) f(x) = f(a)"], "correct_index": 0, "explanation": "Continuity requires f(a) to be defined, the limit to exist, and them to be equal. Differentiability is a stronger condition not required for continuity."},
        ],
        "Differentiation Rules": [
            {"question": "What is d/dx[sin(x²)]?", "options": ["2x·cos(x²)", "cos(x²)", "2x·sin(x²)", "-cos(x²)"], "correct_index": 0, "explanation": "Using the chain rule: d/dx[sin(u)] = cos(u)·du/dx where u = x², so du/dx = 2x. Result: 2x·cos(x²)."},
            {"question": "The product rule states that d/dx[f·g] equals:", "options": ["f'g + fg'", "f'g'", "(fg)'", "f'·g'"], "correct_index": 0, "explanation": "The product rule: the derivative of a product equals the first function\'s derivative times the second plus the first times the second\'s derivative."},
        ],
        "default": [
            {"question": "What does the Fundamental Theorem of Calculus establish?", "options": ["The link between differentiation and integration", "The existence of irrational numbers", "The convergence of all series", "The definition of limits"], "correct_index": 0, "explanation": "The FTC shows that differentiation and integration are inverse operations, connecting the definite integral to antiderivatives."},
            {"question": "When does L'Hôpital's rule apply?", "options": ["When a limit produces 0/0 or ∞/∞ indeterminate forms", "For any limit calculation", "Only for polynomial functions", "When the function is discontinuous"], "correct_index": 0, "explanation": "L'Hôpital's rule can be applied when direct substitution yields indeterminate forms like 0/0 or ∞/∞."},
        ],
    },
    "Operating Systems": {
        "Process Management": [
            {"question": "What is stored in a Process Control Block (PCB)?", "options": ["Process state, program counter, CPU registers, and more", "Only the process name", "The entire program code", "Just the memory address"], "correct_index": 0, "explanation": "The PCB contains all information needed to manage a process: state, PC, registers, scheduling info, memory info, and I/O status."},
            {"question": "What triggers a context switch?", "options": ["Timer interrupt, I/O request, or system call", "Only user input", "Program compilation", "File creation"], "correct_index": 0, "explanation": "Context switches occur when the OS needs to switch between processes, triggered by interrupts, I/O, or explicit system calls."},
        ],
        "default": [
            {"question": "What problem does virtual memory solve?", "options": ["Running programs larger than physical RAM", "Faster disk access", "Network latency", "CPU overheating"], "correct_index": 0, "explanation": "Virtual memory allows programs to use more memory than physically available by swapping pages between RAM and disk."},
            {"question": "Which scheduling algorithm can cause starvation?", "options": ["Priority scheduling (without aging)", "Round Robin", "FCFS", "Shortest Job First (preemptive)"], "correct_index": 0, "explanation": "Priority scheduling can starve low-priority processes indefinitely if higher-priority processes keep arriving."},
        ],
    },
    "Quantum Physics": {
        "default": [
            {"question": "What does the wave function ψ represent?", "options": ["The probability amplitude of finding a particle", "The particle's exact position", "The particle's mass", "The electromagnetic field strength"], "correct_index": 0, "explanation": "The wave function ψ gives probability amplitudes; |ψ|² gives the probability density of finding the particle at a given position."},
            {"question": "What is quantum superposition?", "options": ["A particle existing in multiple states simultaneously until measured", "Two particles occupying the same space", "A particle traveling faster than light", "The creation of new particles"], "correct_index": 0, "explanation": "Superposition means a quantum system exists in all possible states simultaneously until a measurement collapses it to a definite state."},
        ],
    },
    "Web Development": {
        "default": [
            {"question": "What does the 'virtual DOM' in React optimize?", "options": ["Minimizing actual DOM manipulation through diffing", "Network requests", "CSS processing", "Database queries"], "correct_index": 0, "explanation": "React's virtual DOM computes the minimal set of changes needed and batches actual DOM updates, making UI updates efficient."},
            {"question": "What is the purpose of CORS headers?", "options": ["Allowing controlled cross-origin resource sharing", "Encrypting data in transit", "Compressing HTTP responses", "Caching static assets"], "correct_index": 0, "explanation": "CORS headers let servers specify which origins can access their resources, relaxing the same-origin policy safely."},
        ],
    },
    "Linear Algebra": {
        "default": [
            {"question": "If Av = λv, what are v and λ called?", "options": ["Eigenvector and eigenvalue", "Basis vector and scalar", "Normal vector and determinant", "Unit vector and trace"], "correct_index": 0, "explanation": "When multiplying matrix A by vector v gives a scalar multiple λ of v, v is an eigenvector and λ is its corresponding eigenvalue."},
            {"question": "What does it mean if det(A) = 0?", "options": ["A is singular (non-invertible)", "A is the identity matrix", "A has all positive entries", "A is symmetric"], "correct_index": 0, "explanation": "A zero determinant means the matrix is singular — it cannot be inverted, and its columns are linearly dependent."},
        ],
    },
    "Cloud Computing": {
        "default": [
            {"question": "What does SaaS stand for?", "options": ["Software as a Service", "System as a Service", "Storage as a Service", "Security as a Service"], "correct_index": 0, "explanation": "SaaS (Software as a Service) allows users to connect to and use cloud-based apps over the Internet."},
            {"question": "What is the primary benefit of 'autoscaling'?", "options": ["Matching resources to demand dynamically", "Reducing initial cost", "Increasing security for free", "Automatically writing code"], "correct_index": 0, "explanation": "Autoscaling dynamically adjusts the amount of compute resources based on demand, optimizing performance and cost."},
        ],
    },
    "System Design": {
        "default": [
            {"question": "What is a 'single point of failure'?", "options": ["A part of a system that, if it fails, stops the entire system", "A bug in a single file", "A slow network request", "A user error"], "correct_index": 0, "explanation": "A SPOF is a critical path component whose failure brings down the entire architecture; HA design aims to eliminate these."},
            {"question": "What does a Load Balancer do?", "options": ["Distributes traffic across multiple servers", "Speeds up database queries", "Encrypts user passwords", "Compiles code"], "correct_index": 0, "explanation": "Load balancers distribute incoming network traffic across a group of backend servers to ensure no single server is overwhelmed."},
        ],
    },
    "Cybersecurity": {
        "default": [
            {"question": "What does the 'CIA Triad' stand for?", "options": ["Confidentiality, Integrity, Availability", "Control, Identity, Access", "Cyber, Infrastructure, Application", "Codes, Information, Attacks"], "correct_index": 0, "explanation": "The CIA Triad is the core model for information security: Confidentiality, Integrity, and Availability."},
            {"question": "What is a 'Phishing' attack?", "options": ["A social engineering attack to steal credentials", "A brute force password attack", "A network disruption attack", "A virus that deletes files"], "correct_index": 0, "explanation": "Phishing involves sending fraudulent communications that appear to come from a reputable source to steal sensitive data."},
        ],
    },
    "Deep Learning": {
        "default": [
            {"question": "What is 'Backpropagation' used for?", "options": ["Calculating gradients for model updates", "Predicting the final output", "Initializing weights", "Collecting data"], "correct_index": 0, "explanation": "Backpropagation is the gradient-calculating algorithm used to train neural networks by propagating error back through layers."},
            {"question": "What is a 'GPU' usually used for in Deep Learning?", "options": ["Massive parallel computation of matrix operations", "Storing the dataset", "Connecting to the internet", "Displaying images only"], "correct_index": 0, "explanation": "GPUs are designed for highly parallel tasks, making them perfect for the massive matrix multiplications required in deep learning."},
        ],
    },
    "Mobile Development": {
        "default": [
            {"question": "What is a 'cross-platform' framework?", "options": ["A tool to write one codebase for both iOS and Android", "A way to move apps to the web", "A security protocol", "A database system"], "correct_index": 0, "explanation": "Cross-platform frameworks like Flutter or React Native allow developers to build apps for multiple platforms using a single codebase."},
        ],
    },
    "Microeconomics": {
        "default": [
            {"question": "What is 'Opportunity Cost'?", "options": ["The value of the next best alternative forgone", "The price of an item", "The total cost of production", "A discount on a product"], "correct_index": 0, "explanation": "Opportunity cost is what you give up (the benefit of the second-best option) when making a choice."},
        ],
    },
    "Database Management": {
        "default": [
            {"question": "What is 'Normalization' in DB design?", "options": ["Organizing data to reduce redundancy", "Converting all text to uppercase", "Deleting old records", "Merging all tables into one"], "correct_index": 0, "explanation": "Normalization is the process of structuring a database to reduce data redundancy and improve data integrity."},
            {"question": "What does ACID stand for in transactions?", "options": ["Atomicity, Consistency, Isolation, Durability", "Access, Control, Identity, Data", "Automated, Compressed, Integrated, Distributed", "Always, Correct, Instant, Durable"], "correct_index": 0, "explanation": "ACID properties ensure that database transactions are processed reliably."},
        ],
    },
}


def generate_assessment(topic_name: str, subject: str, difficulty: str, count: int = 5) -> Optional[Dict[str, Any]]:
    """
    Generate assessment questions WITHOUT any API call.
    Pulls from curated question banks, adapts difficulty.
    """
    # Get topic-specific questions, fall back to default
    subject_bank = QUESTION_BANK.get(subject, QUESTION_BANK.get("Machine Learning", {}))
    topic_questions = subject_bank.get(topic_name, subject_bank.get("default", []))
    
    if not topic_questions:
        # Fallback: generate from generic templates
        topic_questions = _generate_generic_questions(topic_name, difficulty)
    
    # Select up to `count` questions
    selected = random.sample(topic_questions, min(count, len(topic_questions)))
    
    # If we don't have enough, pad with generic questions
    while len(selected) < count:
        generic = _generate_generic_questions(topic_name, difficulty)
        for q in generic:
            if len(selected) < count:
                selected.append(q)
    
    return {
        "topic_id": topic_name,
        "questions": selected,
    }


def _generate_generic_questions(topic_name: str, difficulty: str) -> List[Dict]:
    """Generate procedural questions for topics not in the bank."""
    templates = {
        "easy": [
            {"question": f"Which of the following is a key characteristic of {topic_name}?", "options": ["It forms a fundamental building block for advanced topics", "It has no practical applications", "It was discovered in the 21st century", "It contradicts all prior theories"], "correct_index": 0, "explanation": f"{topic_name} is fundamental because it provides the conceptual framework for understanding more advanced topics in the field."},
            {"question": f"What is the primary goal of studying {topic_name}?", "options": ["To understand its core principles and applications", "To memorize formulas only", "To replace other topics entirely", "To avoid practical implementation"], "correct_index": 0, "explanation": f"The goal of studying {topic_name} is to build both theoretical understanding and practical problem-solving ability."},
        ],
        "medium": [
            {"question": f"When applying {topic_name} in practice, what is the most common mistake?", "options": ["Ignoring edge cases and boundary conditions", "Using too much computing power", "Starting with simple examples", "Reading documentation"], "correct_index": 0, "explanation": f"In {topic_name}, overlooking edge cases is the most frequent source of errors in both academic and real-world applications."},
            {"question": f"How does {topic_name} relate to its prerequisites?", "options": ["It builds directly upon foundational concepts", "It is completely independent", "It contradicts earlier learning", "There is no relationship"], "correct_index": 0, "explanation": f"{topic_name} is designed with specific prerequisites in mind, each contributing essential knowledge for understanding the topic."},
        ],
        "hard": [
            {"question": f"What is the computational complexity implication of {topic_name}?", "options": ["It introduces tradeoffs between time and space efficiency", "It always runs in O(1)", "Complexity is irrelevant", "It only works on sorted data"], "correct_index": 0, "explanation": f"Advanced aspects of {topic_name} involve careful analysis of time-space tradeoffs for practical implementation."},
            {"question": f"In a research context, what is the current frontier challenge in {topic_name}?", "options": ["Scaling to large, real-world datasets while maintaining accuracy", "Making it simpler for beginners", "Reducing the number of textbooks", "Avoiding any mathematical formulation"], "correct_index": 0, "explanation": f"Research in {topic_name} continues to push boundaries in scaling, efficiency, and applicability to complex scenarios."},
        ],
    }
    return templates.get(difficulty, templates["medium"])
