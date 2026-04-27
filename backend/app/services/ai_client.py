import json
import openai
from typing import List, Dict, Any, Optional, Type
import logging
import asyncio
from pydantic import BaseModel
from app.config import settings

logger = logging.getLogger("neuroplan.ai")

class AIClient:
    """
    NeuroPlan AI — Proprietary Model Client
    ========================================
    Routes ALL inference through our fine-tuned model served via Ollama.
    NO external API dependency. The model IS the product.
    
    Architecture:
    - Primary: Fine-tuned Llama-3.1-8B (local via Ollama)
    - Fallback: Groq/OpenAI ONLY if local model is unavailable and keys exist
    """
    def __init__(self):
        # ================================================================
        # PRIMARY: Our fine-tuned model via Ollama
        # ================================================================
        self.custom_url = settings.CUSTOM_AI_URL or "http://localhost:11434/v1"
        self.custom_model = settings.CUSTOM_AI_MODEL or "neuroplan"
        self.use_custom = settings.USE_CUSTOM_AI
        
        self.custom_client = openai.AsyncOpenAI(
            api_key="ollama",  # Ollama doesn't need a real key
            base_url=self.custom_url
        )
        
        # ================================================================
        # FALLBACK ONLY: External API (for development before model is trained)
        # ================================================================
        self.groq_key = settings.GROQ_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        
        if self.groq_key:
            self.fallback_client = openai.AsyncOpenAI(
                api_key=self.groq_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.fallback_model = "llama-3.3-70b-versatile"
        elif self.openai_key:
            self.fallback_client = openai.AsyncOpenAI(api_key=self.openai_key)
            self.fallback_model = "gpt-4o-mini"
        else:
            self.fallback_client = None
            self.fallback_model = None
        
        # Backward compatibility for generators
        if self.use_custom:
            self.client = self.custom_client
            self.model = self.custom_model
            logger.info(f"🧠 Using PROPRIETARY model: {self.custom_model} at {self.custom_url}")
        elif self.fallback_client:
            self.client = self.fallback_client
            self.model = self.fallback_model
            logger.info(f"⚠️  Using FALLBACK API: {self.fallback_model}")
        else:
            self.client = None
            self.model = None
            logger.warning("❌ No AI backend configured!")

    def _get_client_and_model(self, use_custom: bool = True):
        """Select the appropriate client based on configuration."""
        if use_custom and self.use_custom:
            return self.custom_client, self.custom_model
        elif self.fallback_client:
            return self.fallback_client, self.fallback_model
        elif self.use_custom:
            return self.custom_client, self.custom_model
        else:
            raise ValueError(
                "No AI backend configured. Either:\n"
                "  1. Start Ollama and set USE_CUSTOM_AI=true (recommended)\n"
                "  2. Set GROQ_API_KEY in .env (fallback only)"
            )

    async def _call_ai(
        self, 
        prompt: str, 
        system_msg: str = "You are a helpful study assistant.",
        use_custom: bool = True,
        response_model: Optional[Type[BaseModel]] = None
    ) -> Any:
        """Internal router with retry and schema enforcement."""
        client, model = self._get_client_and_model(use_custom)

        for attempt in range(settings.AI_MAX_RETRIES):
            try:
                # Ensure 'json' appears in prompt when using json_object format
                effective_system = system_msg
                if response_model:
                    effective_system += " You MUST respond with valid JSON."
                    
                messages = [
                    {"role": "system", "content": effective_system},
                    {"role": "user", "content": prompt}
                ]
                
                # Use response_format if supported
                extra_args = {}
                if response_model and settings.CUSTOM_AI_GUIDED_JSON:
                    extra_args["response_format"] = {"type": "json_object"}

                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                    **extra_args
                )
                
                content = response.choices[0].message.content
                
                if response_model:
                    try:
                        return response_model.model_validate_json(content)
                    except Exception as e:
                        logger.warning(f"JSON Validation failed on attempt {attempt+1}: {e}")
                        continue
                
                return content
            except Exception as e:
                logger.error(f"AI Call failed on attempt {attempt+1}: {e}")
                
                # If custom model failed, try fallback
                if use_custom and self.fallback_client and attempt == 0:
                    logger.info("Falling back to external API...")
                    client = self.fallback_client
                    model = self.fallback_model
                    continue
                    
                await asyncio.sleep(2 ** attempt)
        
        return None

    async def get_structured_completion(
        self, 
        prompt: str, 
        response_model: Type[BaseModel],
        system_prompt: str = "You are a specialized AI assistant."
    ) -> Any:
        """High-level method for Pydantic-guaranteed JSON output."""
        return await self._call_ai(
            prompt=prompt,
            system_msg=system_prompt,
            use_custom=self.use_custom,
            response_model=response_model
        )

    async def decompose_subject(self, subject_name: str, profile: str, mastery_scores: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Decompose subject using our fine-tuned curriculum engine with real mastery context."""
        system = "You are NeuroPlan AI Curriculum Engine. Break down subjects into personalized topics based on student profiles and real-time mastery scores."
        prompt = f"Subject: {subject_name}\nProfile: {profile}"
        if mastery_scores:
            prompt += f"\nRecent Mastery Analysis: {json.dumps(mastery_scores)}"
        
        result = await self._call_ai(prompt, system, use_custom=True)
        try:
            parsed = json.loads(result)
            return parsed.get("topics", []) if isinstance(parsed, dict) else parsed
        except:
            return []

    async def generate_study_card(self, topic_name: str, subject_name: str, profile: str, topic_mastery: Optional[float] = None) -> Dict[str, Any]:
        """Generate study cards with real-time mastery grounding."""
        system = "You are NeuroPlan AI Study Card Engine. Generate personalized learning content. Use mastery scores to adjust complexity."
        prompt = f"Topic: {topic_name}\nSubject: {subject_name}\nProfile: {profile}"
        if topic_mastery is not None:
            prompt += f"\nCurrent Mastery for this topic: {topic_mastery:.2f}"
        
        result = await self._call_ai(prompt, system, use_custom=True)
        try:
            return json.loads(result)
        except:
            return {"summary": "Generated content placeholder."}

    async def generate_assessment(self, topic_name: str, difficulty: str, mastery_score: Optional[float] = None, wrong_concepts: str = "") -> List[Dict[str, Any]]:
        """Generate adaptive assessments targeting predicted weak areas."""
        system = "You are NeuroPlan AI Assessment Engine. Generate high-quality MCQs. Target predicted knowledge gaps from DKT analysis."
        prompt = f"Topic: {topic_name}\nBase Difficulty: {difficulty}"
        if mastery_score is not None:
            prompt += f"\nPredicted Mastery: {mastery_score:.2f}"
        if wrong_concepts:
            prompt += f"\nFocus on weak concepts: {wrong_concepts}"
        
        result = await self._call_ai(prompt, system, use_custom=True)
        try:
            parsed = json.loads(result)
            return parsed.get("questions", []) if isinstance(parsed, dict) else parsed
        except:
            return []

    async def generate_adaptive_recommendation(self, profile: str, plan_status: str, struggles: str, mastery_snapshot: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Generate adjustments with full DKT snapshot context."""
        system = "You are NeuroPlan AI Adaptive Engine. Analyze student performance vectors and provide personalized plan adjustments."
        prompt = f"Profile: {profile}\nPlan Status: {plan_status}\nStruggles: {struggles}"
        if mastery_snapshot:
            prompt += f"\nMastery Snapshot: {json.dumps(mastery_snapshot)}"
        
        result = await self._call_ai(prompt, system, use_custom=True)
        try:
            return json.loads(result)
        except:
            return {"summary": "Unable to generate recommendation", "actions": []}

    async def optimize_schedule(self, schedule_data: Dict[str, Any], context: str = "") -> str:
        """Optimize study schedule using model intelligence."""
        system = "You are a Senior Study Coach. Optimize this study plan for continuity and balance."
        prompt = f"Data: {json.dumps(schedule_data)}\nContext: {context}"
        
        return await self._call_ai(prompt, system, use_custom=True)
