"""
NeuroPlan AI Client — Production Engine
========================================
Every method is purpose-built for serious students.
Prompts follow Bloom's Taxonomy, spaced-repetition science,
and real-time DKT mastery grounding.

Public API (consumed by services):
  - decompose_subject()
  - generate_study_card()
  - generate_probe_questions()
  - generate_assessment()
  - generate_adaptive_recommendation()
  - optimize_schedule()
  - get_structured_completion()
"""

import json
import re
import logging
import asyncio
import hashlib
from typing import List, Dict, Any, Optional, Type, AsyncGenerator
import openai
from pydantic import BaseModel
from app.config import settings
from app.services.cache_service import CacheService

logger = logging.getLogger("neuroplan.ai")

# ──────────────────────────────────────────────────────────────
# JSON Extraction Utility
# ──────────────────────────────────────────────────────────────

_JSON_BLOCK_RE = re.compile(
    r"```(?:json)?\s*\n?(.*?)```", re.DOTALL
)
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)
_JSON_ARRAY_RE = re.compile(r"\[.*\]", re.DOTALL)


def _extract_json(text: str) -> Any:
    """
    Aggressively extract JSON from model output.
    Handles: raw JSON, ```json blocks, markdown wrapping,
    and trailing prose after valid JSON.
    """
    if not text:
        return None

    cleaned = text.strip()

    # 1. Try raw parse first (fastest path)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. Try extracting from markdown code blocks
    match = _JSON_BLOCK_RE.search(cleaned)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. Try extracting the first { ... } object
    match = _JSON_OBJECT_RE.search(cleaned)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # 4. Try extracting the first [ ... ] array
    match = _JSON_ARRAY_RE.search(cleaned)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


# ──────────────────────────────────────────────────────────────
# Mastery Interpretation
# ──────────────────────────────────────────────────────────────

def _mastery_label(score: float) -> str:
    if score >= 0.85:
        return "Advanced"
    if score >= 0.65:
        return "Proficient"
    if score >= 0.40:
        return "Developing"
    return "Beginner"


def _difficulty_from_mastery(score: float) -> str:
    if score >= 0.75:
        return "hard"
    if score >= 0.40:
        return "medium"
    return "easy"


# ──────────────────────────────────────────────────────────────
# AIClient
# ──────────────────────────────────────────────────────────────

class AIClient:
    """
    NeuroPlan AI — Proprietary Inference Client
    =============================================
    Routes ALL inference through our local model served via Ollama.
    NO external API dependency. The model IS the product.

    Architecture:
    - Primary:  Lily-NeuroPlan (Qwen2.5-1.5B, local via Ollama)
    - Fallback: Groq / OpenAI ONLY if local model is unavailable
    """

    def __init__(self):
        # ── Primary: Local Ollama ──
        self.custom_url = settings.CUSTOM_AI_URL or "http://localhost:11434/v1"
        self.custom_model = settings.CUSTOM_AI_MODEL or "lily-neuroplan"
        self.use_custom = settings.USE_CUSTOM_AI

        self.custom_client = openai.AsyncOpenAI(
            api_key="ollama",
            base_url=self.custom_url,
            timeout=90.0,
            max_retries=0,
        )
        
        self.cache = CacheService()

        # ── Fallback: External APIs ──
        self.groq_key = settings.GROQ_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

        if self.groq_key:
            self.fallback_client = openai.AsyncOpenAI(
                api_key=self.groq_key,
                base_url="https://api.groq.com/openai/v1",
            )
            self.fallback_model = "llama-3.3-70b-versatile"
        elif self.openai_key:
            self.fallback_client = openai.AsyncOpenAI(api_key=self.openai_key)
            self.fallback_model = "gpt-4o-mini"
        else:
            self.fallback_client = None
            self.fallback_model = None

        # Backward-compat aliases
        if self.use_custom:
            self.client = self.custom_client
            self.model = self.custom_model
            logger.info("🧠 AI Engine: %s @ %s", self.custom_model, self.custom_url)
        elif self.fallback_client:
            self.client = self.fallback_client
            self.model = self.fallback_model
            logger.info("⚠️  Fallback AI: %s", self.fallback_model)
        else:
            self.client = None
            self.model = None
            logger.warning("❌ No AI backend configured!")

    # ──────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────

    def _get_client_and_model(self, use_custom: bool = True):
        if use_custom and self.use_custom:
            return self.custom_client, self.custom_model
        if self.fallback_client:
            return self.fallback_client, self.fallback_model
        if self.use_custom:
            return self.custom_client, self.custom_model
        raise ValueError(
            "No AI backend configured. Start Ollama or set GROQ_API_KEY."
        )

    def _build_adaptive_context(
        self,
        profile: str,
        mastery_snapshot: Optional[Dict[str, float]] = None,
    ) -> str:
        """Rich learner context block injected into every prompt."""
        ctx = f"## LEARNER PROFILE\n{profile}\n"
        if mastery_snapshot:
            struggling = sorted(
                [(k, v) for k, v in mastery_snapshot.items() if v < 0.4],
                key=lambda x: x[1],
            )
            strong = [k for k, v in mastery_snapshot.items() if v >= 0.7]
            developing = [
                k for k, v in mastery_snapshot.items()
                if 0.4 <= v < 0.7
            ]
            ctx += "\n## MASTERY SNAPSHOT (from Deep Knowledge Tracing)\n"
            if struggling:
                ctx += "🔴 Struggling: " + ", ".join(
                    f"{k} ({v*100:.0f}%)" for k, v in struggling
                ) + "\n"
            if developing:
                ctx += "🟡 Developing: " + ", ".join(developing) + "\n"
            if strong:
                ctx += "🟢 Strong: " + ", ".join(strong) + "\n"
        return ctx

    async def _call_ai(
        self,
        prompt: str,
        system_msg: str,
        use_custom: bool = True,
        temperature: float = 0.3,
        response_model: Optional[Type[BaseModel]] = None,
        json_mode: bool = True,
    ) -> Any:
        """Core inference loop with automatic fallback and retry."""
        # 1. Check Cache
        cached = await self.cache.get_ai_response(prompt, system_msg)
        if cached:
            if response_model:
                try:
                    return response_model.model_validate(cached)
                except Exception:
                    pass # Fallback to real call if model schema changed
            else:
                return cached

        client, model = self._get_client_and_model(use_custom)

        for attempt in range(settings.AI_MAX_RETRIES):
            try:
                effective_system = system_msg
                if response_model:
                    effective_system += (
                        "\n\nIMPORTANT: Respond ONLY with a valid JSON object."
                        " No markdown, no explanation, no code blocks."
                    )
                
                kwargs = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": effective_system},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": temperature,
                }
                
                # Dynamic max_tokens scaling
                if "decomposition" in system_msg.lower():
                    kwargs["max_tokens"] = 4096
                elif "study card" in system_msg.lower():
                    kwargs["max_tokens"] = 2560
                elif "assessment" in system_msg.lower():
                    kwargs["max_tokens"] = 1536
                else:
                    kwargs["max_tokens"] = 1024

                import time
                start_time = time.time()
                
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                response = await client.chat.completions.create(**kwargs)
                latency = time.time() - start_time
                logger.info("AI Completion: %s | Latency: %.2fs", model, latency)

                content = response.choices[0].message.content
                
                # Cache successful response
                if content:
                    try:
                        # Store as dict if JSON, else raw string
                        cache_val = json.loads(content) if json_mode else content
                        await self.cache.set_ai_response(prompt, system_msg, cache_val)
                    except Exception:
                        await self.cache.set_ai_response(prompt, system_msg, content)

                if response_model:
                    try:
                        return response_model.model_validate_json(content)
                    except Exception:
                        logger.warning(
                            "Pydantic parse failed (attempt %d), raw: %.200s",
                            attempt + 1, content,
                        )
                        continue

                return content

            except Exception as e:
                logger.error("AI call failed (attempt %d): %s", attempt + 1, e)

                # On first failure of custom model, try fallback
                if use_custom and self.fallback_client and attempt == 0:
                    logger.info("Switching to fallback API…")
                    client = self.fallback_client
                    model = self.fallback_model
                    continue

                await asyncio.sleep(min(2 ** attempt, 8))

        return None

    async def stream_ai(
        self,
        prompt: str,
        system_msg: str,
        temperature: float = 0.7,
        use_custom: bool = True,
    ) -> AsyncGenerator[str, None]:
        """Stream the AI response chunk by chunk."""
        client, model = self._get_client_and_model(use_custom)
        
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "stream": True
        }
        
        try:
            response = await client.chat.completions.create(**kwargs)
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            # Fallback to Groq if local fails
            if use_custom and self.groq_key:
                logger.info("Falling back to Groq for streaming...")
                async for chunk in self.stream_ai(prompt, system_msg, temperature, use_custom=False):
                    yield chunk

    # ──────────────────────────────────────────────────────
    # PUBLIC METHODS
    # ──────────────────────────────────────────────────────

    async def get_structured_completion(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        system_prompt: str = "You are a specialized AI assistant.",
    ) -> Any:
        """Generic Pydantic-guaranteed JSON output."""
        return await self._call_ai(
            prompt=prompt,
            system_msg=system_prompt,
            use_custom=self.use_custom,
            response_model=response_model,
        )

    # ──────────────────────────────────────────────────────
    # 1. SUBJECT DECOMPOSITION
    # ──────────────────────────────────────────────────────

    async def decompose_subject(
        self,
        subject_name: str,
        profile: str,
        context: str = "",
        mastery_scores: Optional[Dict[str, float]] = None,
        target_level: str = "intermediate",
    ) -> List[Dict[str, Any]]:
        """
        Break a subject into a full syllabus: Topics → Subtopics.
        Each topic contains detailed `key_concepts` that act as
        the actual learning points / subtopics a student must cover.
        """
        # Scale topic count and subtopic depth by target level
        level_config = {
            "beginner":     {"topics": "8–12",  "subtopics": "3–5",  "depth": "Cover only fundamentals and basics. Skip advanced theory."},
            "intermediate": {"topics": "12–18", "subtopics": "4–7",  "depth": "Cover core theory + practical applications. Include worked examples."},
            "advanced":     {"topics": "18–25", "subtopics": "5–8",  "depth": "Cover full theory, edge cases, optimizations, and real-world applications."},
            "expert":       {"topics": "25–35", "subtopics": "6–10", "depth": "Cover research-level depth, mathematical proofs, implementation internals, and industry best practices."},
        }
        cfg = level_config.get(target_level, level_config["intermediate"])

        system = (
            "You are the NeuroPlan Curriculum Architect.\n"
            "You design COMPLETE SYLLABI — not just topic lists.\n\n"
            f"DEPTH LEVEL: {target_level.upper()}\n"
            "RULES:\n"
            "1. Each topic is a CHAPTER. Order by prerequisite dependency.\n"
            "2. Each topic's `key_concepts` are the SUBTOPICS / LEARNING POINTS within that chapter.\n"
            "   These are NOT vague labels. They are specific things the student must learn.\n"
            "   Example for 'Tokenization': ['Word Tokenization (splitting by whitespace and punctuation)',\n"
            "   'Sentence Tokenization (NLTK sent_tokenize vs spaCy)', 'Subword Tokenization (BPE algorithm)',\n"
            "   'WordPiece and SentencePiece tokenizers', 'Handling special characters and Unicode',\n"
            "   'Tokenization for different languages (CJK, Arabic)']\n"
            "3. Difficulty must reflect Bloom's Taxonomy (Remember → Analyze → Create).\n"
            "4. If mastery data exists, compress topics the student already knows.\n"
            "5. Respond ONLY with a valid JSON object."
        )

        adaptive_ctx = self._build_adaptive_context(profile, mastery_scores)

        prompt = f"""{adaptive_ctx}

## TASK
Create a COMPLETE SYLLABUS for **{subject_name}** at **{target_level.upper()}** level.
{cfg['depth']}"""

        if context:
            prompt += f"\n\n## STUDENT'S GOAL\n{context}"

        prompt += f"""

## REQUIRED JSON FORMAT
{{
  "topics": [
    {{
      "name": "Chapter/Topic Name (specific)",
      "difficulty": "easy" | "medium" | "hard",
      "estimated_hours": 2.0,
      "sort_order": 1,
      "prerequisites": ["Other Topic Name if any"],
      "key_concepts": [
        "Subtopic 1: Specific learning point with brief description",
        "Subtopic 2: Another specific concept to master",
        "Subtopic 3: Include types, methods, or formulas where relevant"
      ]
    }}
  ]
}}

Generate {cfg['topics']} topics, each with {cfg['subtopics']} detailed subtopics in key_concepts.
Every subtopic should be a concrete, teachable point — NOT a vague label."""

        result = await self._call_ai(prompt, system, use_custom=True, temperature=0.4)
        if not result:
            return []

        parsed = _extract_json(result)
        if parsed is None:
            logger.error("Decomposition JSON extraction failed. Raw: %.500s", result)
            return []

        if isinstance(parsed, dict):
            return parsed.get("topics", [])
        if isinstance(parsed, list):
            return parsed
        return []

    # ──────────────────────────────────────────────────────
    # 2. STUDY CARD GENERATION
    # ──────────────────────────────────────────────────────

    _EMPTY_CARD = {
        "summary": "",
        "key_concepts": [],
        "formulas": [],
        "study_tips": [],
        "resources": [],
        "practice_problems": [],
    }

    async def generate_study_card(
        self,
        topic_name: str,
        subject_name: str,
        profile: str,
        topic_mastery: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Generate a rich, personalized study card for a single topic.
        Content depth adapts to the student's current mastery level.
        """
        mastery = topic_mastery or 0.5
        level = _mastery_label(mastery)

        system = (
            "You are the NeuroPlan Study Card Engine.\n"
            "You generate comprehensive, exam-ready study material for serious students.\n\n"
            "RULES:\n"
            "1. The summary must teach the core idea clearly in 2–4 sentences.\n"
            "2. Key concepts: 4–8 specific, detailed points — not generic definitions.\n"
            "3. Formulas/definitions: include actual formulas with variable meanings, "
            "or precise definitions. Write 'N/A' if the topic has none.\n"
            "4. Study tips: practical, actionable strategies specific to THIS topic.\n"
            "5. Resources: real, well-known educational sources (Khan Academy, MIT OCW, "
            "3Blue1Brown, GeeksforGeeks, etc.). Use plausible URLs.\n"
            "6. Practice problems: thought-provoking questions that test deep understanding, "
            "not trivial recall.\n"
            "7. Respond ONLY with a valid JSON object. No markdown, no explanation."
        )

        depth_instruction = {
            "Beginner": (
                "The student is a BEGINNER on this topic. "
                "Use simple language, analogies, and build from first principles. "
                "Focus on 'what' and 'why' before 'how'."
            ),
            "Developing": (
                "The student has DEVELOPING understanding. "
                "Reinforce fundamentals while introducing connections to other concepts. "
                "Include worked examples in practice problems."
            ),
            "Proficient": (
                "The student is PROFICIENT. "
                "Focus on edge cases, common mistakes, and exam-style tricky scenarios. "
                "Challenge them with application-level problems."
            ),
            "Advanced": (
                "The student has ADVANCED mastery. "
                "Focus on synthesis: how this topic connects to others, real-world applications, "
                "and research-level depth. Include problems that require combining multiple concepts."
            ),
        }

        adaptive_ctx = self._build_adaptive_context(profile)

        prompt = f"""{adaptive_ctx}

## CONTEXT
- **Subject:** {subject_name}
- **Topic:** {topic_name}
- **Current Mastery:** {mastery*100:.0f}% ({level})

## ADAPTATION INSTRUCTION
{depth_instruction.get(level, depth_instruction["Developing"])}

## REQUIRED JSON FORMAT
{{
  "summary": "Clear 2–4 sentence explanation of the topic's core idea",
  "key_concepts": [
    "Specific concept with brief explanation (e.g., 'Binary Search — O(log n) divide-and-conquer algorithm that halves the search space each iteration')"
  ],
  "formulas": [
    "Actual formula or definition (e.g., 'Time Complexity: T(n) = T(n/2) + O(1)')"
  ],
  "study_tips": [
    "Actionable tip specific to this topic (e.g., 'Draw the recursion tree to visualize the divide step')"
  ],
  "resources": [
    {{
      "title": "Resource Name",
      "url": "https://real-educational-url.com/relevant-page",
      "type": "Video | Article | Interactive | Book"
    }}
  ],
  "practice_problems": [
    "A thought-provoking question that tests deep understanding"
  ]
}}

Generate the study card now. Make it genuinely useful for exam preparation."""

        result = await self._call_ai(prompt, system, use_custom=True, temperature=0.5)
        if not result:
            return {**self._EMPTY_CARD, "summary": "AI engine did not respond. Please retry."}

        parsed = _extract_json(result)
        if parsed is None or not isinstance(parsed, dict):
            logger.error("Study card JSON failed. Raw: %.500s", result)
            return {**self._EMPTY_CARD, "summary": "Failed to parse AI output. Please regenerate."}

        # Guarantee all required keys exist with correct types
        card = {**self._EMPTY_CARD}
        card["summary"] = str(parsed.get("summary", ""))
        card["key_concepts"] = parsed.get("key_concepts", []) if isinstance(parsed.get("key_concepts"), list) else []
        card["formulas"] = parsed.get("formulas", []) if isinstance(parsed.get("formulas"), list) else []
        card["study_tips"] = parsed.get("study_tips", []) if isinstance(parsed.get("study_tips"), list) else []
        card["resources"] = parsed.get("resources", []) if isinstance(parsed.get("resources"), list) else []
        card["practice_problems"] = parsed.get("practice_problems", []) if isinstance(parsed.get("practice_problems"), list) else []

        return card

    # ──────────────────────────────────────────────────────
    # 3. PROBE QUESTIONS (Quick Knowledge Verification)
    # ──────────────────────────────────────────────────────

    async def generate_probe_questions(
        self, topic_name: str, num_questions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate short verification questions used after a study session.
        These test understanding, not memorization.
        """
        system = (
            "You are the NeuroPlan Knowledge Probe Engine.\n"
            "Generate short, conceptual verification questions that test whether "
            "a student truly understands a topic — not just memorized facts.\n\n"
            "RULES:\n"
            "1. Questions should require understanding, not just recall.\n"
            "2. Answers should be 1–3 sentences, clear and correct.\n"
            "3. Mix question types: 'why' questions, 'what happens if', comparisons.\n"
            "4. Respond ONLY with a valid JSON object."
        )

        prompt = f"""## TOPIC: {topic_name}

Generate exactly {num_questions} conceptual probe questions.

## REQUIRED JSON FORMAT
{{
  "questions": [
    {{
      "question": "A short question testing conceptual understanding",
      "answer": "Clear, correct answer in 1–3 sentences"
    }}
  ]
}}"""

        result = await self._call_ai(prompt, system, use_custom=True, temperature=0.5)
        if not result:
            return []

        parsed = _extract_json(result)
        if parsed is None:
            logger.error("Probe JSON failed. Raw: %.500s", result)
            return []

        if isinstance(parsed, dict):
            return parsed.get("questions", [])
        if isinstance(parsed, list):
            return parsed
        return []

    # ──────────────────────────────────────────────────────
    # 4. ASSESSMENT GENERATION (MCQ Tests)
    # ──────────────────────────────────────────────────────

    async def generate_assessment(
        self,
        topic_name: str,
        difficulty: str,
        mastery_score: Optional[float] = None,
        wrong_concepts: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Generate adaptive MCQ assessments.
        Difficulty auto-scales from DKT mastery prediction.
        Targets known weak concepts when available.
        """
        mastery = mastery_score or 0.5
        effective_diff = _difficulty_from_mastery(mastery) if mastery_score is not None else difficulty

        system = (
            "You are the NeuroPlan Assessment Engine.\n"
            "You generate high-quality multiple-choice questions for real exams.\n\n"
            "RULES:\n"
            "1. Each question must have exactly 4 options (A, B, C, D).\n"
            "2. Only ONE option is correct. Distractors should be plausible.\n"
            "3. Explanations must teach — explain WHY the answer is correct "
            "and WHY common wrong choices are wrong.\n"
            "4. Scale difficulty to the student's level.\n"
            "5. Respond ONLY with a valid JSON object."
        )

        level_guidance = ""
        if effective_diff == "easy":
            level_guidance = (
                "Student is at BEGINNER level. "
                "Ask definition, identification, and basic application questions."
            )
        elif effective_diff == "medium":
            level_guidance = (
                "Student is at INTERMEDIATE level. "
                "Ask analysis, comparison, and multi-step reasoning questions."
            )
        else:
            level_guidance = (
                "Student is at ADVANCED level. "
                "Ask synthesis, evaluation, and edge-case questions. "
                "Include tricky distractors."
            )

        prompt = f"""## TOPIC: {topic_name}
## DIFFICULTY: {effective_diff.upper()} (Mastery: {mastery*100:.0f}%)
## ADAPTATION: {level_guidance}"""

        if wrong_concepts:
            prompt += f"\n## WEAK AREAS TO TARGET: {wrong_concepts}"

        prompt += """

Generate 5 multiple-choice questions.

## REQUIRED JSON FORMAT
{
  "questions": [
    {
      "question": "Clear, specific question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "explanation": "Why this answer is correct and why others are wrong"
    }
  ]
}"""

        result = await self._call_ai(prompt, system, use_custom=True, temperature=0.4)
        if not result:
            return []

        parsed = _extract_json(result)
        if parsed is None:
            logger.error("Assessment JSON failed. Raw: %.500s", result)
            return []

        if isinstance(parsed, dict):
            return parsed.get("questions", [])
        if isinstance(parsed, list):
            return parsed
        return []

    # ──────────────────────────────────────────────────────
    # 5. ADAPTIVE COACHING RECOMMENDATION
    # ──────────────────────────────────────────────────────

    async def generate_adaptive_recommendation(
        self,
        profile: str,
        plan_status: str,
        struggles: str,
        mastery_snapshot: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Generate personalized coaching advice when a student
        is struggling or falling behind their study plan.
        """
        system = (
            "You are the NeuroPlan Performance Coach.\n"
            "You provide empathetic, actionable study advice to students "
            "who are struggling or falling behind.\n\n"
            "RULES:\n"
            "1. Be encouraging but honest about where they need to improve.\n"
            "2. Prioritize the weakest topics — give specific action items.\n"
            "3. Suggest realistic daily study hours (not more than their current plan allows).\n"
            "4. The motivational note should feel personal, not generic.\n"
            "5. Respond ONLY with a valid JSON object."
        )

        adaptive_ctx = self._build_adaptive_context(profile, mastery_snapshot)

        prompt = f"""{adaptive_ctx}

## CURRENT SITUATION
- **Plan Status:** {plan_status}
- **Recent Issue:** {struggles}

## REQUIRED JSON FORMAT
{{
  "message": "2–3 sentence personalized coaching message addressing their specific situation",
  "priority_topics": ["Topic they should focus on first", "Second priority"],
  "suggested_daily_hours": 2.0,
  "motivational_note": "A personal, encouraging message — not generic motivational quotes"
}}"""

        _FALLBACK = {
            "message": "Keep at it — consistency matters more than perfection.",
            "priority_topics": [],
            "suggested_daily_hours": None,
            "motivational_note": "Every expert was once a beginner. You're making progress.",
        }

        result = await self._call_ai(prompt, system, use_custom=True, temperature=0.6)
        if not result:
            return _FALLBACK

        parsed = _extract_json(result)
        if parsed is None or not isinstance(parsed, dict):
            logger.error("Recommendation JSON failed. Raw: %.500s", result)
            return _FALLBACK

        return {
            "message": parsed.get("message", _FALLBACK["message"]),
            "priority_topics": parsed.get("priority_topics", []),
            "suggested_daily_hours": parsed.get("suggested_daily_hours"),
            "motivational_note": parsed.get("motivational_note", _FALLBACK["motivational_note"]),
        }

    # ──────────────────────────────────────────────────────
    # 6. SCHEDULE OPTIMIZATION
    # ──────────────────────────────────────────────────────

    async def optimize_schedule(
        self, schedule_data: Dict[str, Any], context: str = ""
    ) -> str:
        """
        Review a generated study plan and provide optimization advice.
        Returns plain text (not JSON) — used for plan config metadata.
        """
        system = (
            "You are the NeuroPlan Schedule Optimizer.\n"
            "Review the student's generated study plan and provide a concise, "
            "actionable optimization summary.\n\n"
            "FOCUS ON:\n"
            "1. Topic ordering: are prerequisites respected?\n"
            "2. Cognitive load balance: are hard topics spread out?\n"
            "3. Review spacing: is there enough revision before the deadline?\n"
            "4. Practical advice for the student's specific situation.\n\n"
            "Keep your response to 3–5 sentences. Be specific, not generic."
        )

        prompt = f"""## STUDENT PROFILE
{context}

## STUDY PLAN (first 30 entries)
{json.dumps(schedule_data[:30] if isinstance(schedule_data, list) else schedule_data, indent=2)}

Provide your optimization summary."""

        result = await self._call_ai(prompt, system, use_custom=True, temperature=0.4, json_mode=False)
        return result or "Plan generated with standard neuro-scientific spacing."

    # ──────────────────────────────────────────────────────
    # 7. OPEN-ENDED INTERVIEW QUESTIONS
    # ──────────────────────────────────────────────────────

    async def generate_open_ended_questions(
        self,
        topic_name: str,
        difficulty: str,
        num_questions: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate qualitative interview questions."""
        system = (
            "You are the NeuroPlan Interview Simulator.\n"
            "Generate open-ended questions that require detailed verbal explanations.\n\n"
            "RULES:\n"
            "1. Focus on 'How' and 'Why' questions.\n"
            "2. Questions should be scenario-based where possible.\n"
            "3. Provide the 'Key Points' that must be included in a perfect answer.\n"
            "4. Respond ONLY with a valid JSON object."
        )

        prompt = f"""## TOPIC: {topic_name}
## DIFFICULTY: {difficulty.upper()}

Generate {num_questions} open-ended interview questions.

## REQUIRED JSON FORMAT
{{
  "questions": [
    {{
      "question": "The interview question text",
      "key_points": ["Point 1 that must be covered", "Point 2", "Point 3"],
      "difficulty": "{difficulty}"
    }}
  ]
}}"""

        result = await self._call_ai(prompt, system, use_custom=True, temperature=0.6)
        parsed = _extract_json(result)
        return parsed.get("questions", []) if parsed else []

    async def evaluate_answer(
        self,
        question: str,
        user_answer: str,
        key_points: List[str]
    ) -> Dict[str, Any]:
        """Critique a free-text answer based on key points and technical accuracy."""
        system = (
            "You are the NeuroPlan Technical Interviewer.\n"
            "Evaluate the user's verbal/textual response to an interview question.\n\n"
            "EVALUATION CRITERIA:\n"
            "1. Technical Accuracy (Did they get the facts right?)\n"
            "2. Completeness (Did they cover the required key points?)\n"
            "3. Communication (Is it structured? Is it concise?)\n"
            "4. Score (0.0 to 1.0)\n"
            "5. Feedback (What did they miss? How can they word it better?)\n"
            "6. Respond ONLY with a valid JSON object."
        )

        prompt = f"""## QUESTION
{question}

## REQUIRED KEY POINTS
{json.dumps(key_points)}

## USER'S RESPONSE
{user_answer}

## TASK
Evaluate the response and provide a score and actionable feedback."""

        result = await self._call_ai(prompt, system, use_custom=True, temperature=0.3)
        parsed = _extract_json(result)
        return parsed or {
            "score": 0.0,
            "feedback": "AI evaluation failed. Please retry.",
            "technical_accuracy": "unknown",
            "completeness": "unknown"
        }

