from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
from src.utils.config import get_settings
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class LLMService:
    """
    Service class for interacting with OpenAI's language models
    """
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_model = "gpt-4-turbo"  # Default model for chat completions
        self.fallback_model = "gpt-3.5-turbo"

    async def generate_response(self, context: str, question: str, language: str = "en") -> Optional[str]:
        """
        Generate a response based on the provided context and question.

        Args:
            context: Context to use for generating the response
            question: Question from the user
            language: Language for the response ('en' or 'ur')

        Returns:
            Generated response or None if failed
        """
        try:
            # Create the prompt following the template from the requirements
            system_message = self._create_system_message(language)
            user_message = self._create_user_message(context, question)

            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=1000,
                timeout=30
            )

            answer = response.choices[0].message.content.strip()
            logger.debug(f"Generated response with {len(answer)} characters")
            return answer
        except Exception as e:
            logger.error(f"Error generating response with primary model: {e}")

            # Try with fallback model
            try:
                response = await self.client.chat.completions.create(
                    model=self.fallback_model,
                    messages=[
                        {"role": "system", "content": self._create_system_message(language)},
                        {"role": "user", "content": self._create_user_message(context, question)}
                    ],
                    temperature=0.3,
                    max_tokens=1000,
                    timeout=30
                )

                answer = response.choices[0].message.content.strip()
                logger.debug(f"Generated response with fallback model: {len(answer)} characters")
                return answer
            except Exception as fallback_error:
                logger.error(f"Error generating response with fallback model: {fallback_error}")
                return None

    def _create_system_message(self, language: str) -> str:
        """
        Create the system message based on the language.

        Args:
            language: Target language for the response

        Returns:
            System message string
        """
        if language == "ur":
            return (
                "آپ ایک کتاب کے اسسٹنٹ ہیں۔ صرف فراہم کردہ سیاق و سباق سے جواب دیں۔\n"
                "اگر جواب غائب ہے، تو کہیں کہ یہ کتاب میں دستیاب نہیں ہے۔\n"
                "جوابات مختصر اور جامع ہونی چاہئیں۔"
            )
        else:
            return (
                "You are a book assistant. Answer ONLY from the provided context.\n"
                "If answer is missing, say it is not available in the book.\n"
                "Keep answers concise and to the point."
            )

    def _create_user_message(self, context: str, question: str) -> str:
        """
        Create the user message with context and question.

        Args:
            context: Context to include in the message
            question: User's question

        Returns:
            Formatted user message string
        """
        return f"CONTEXT:\n{context}\n\nUSER:\n{question}"

    async def generate_response_with_sources(self, context: str, question: str,
                                           sources: List[str], language: str = "en") -> Optional[Dict[str, Any]]:
        """
        Generate a response and include source information.

        Args:
            context: Context to use for generating the response
            question: Question from the user
            sources: List of sources used to generate the response
            language: Language for the response ('en' or 'ur')

        Returns:
            Dictionary containing response and sources, or None if failed
        """
        response_text = await self.generate_response(context, question, language)
        if response_text is None:
            return None

        return {
            "answer": response_text,
            "sources": sources,
            "language": language,
            "timestamp": datetime.utcnow()
        }

    async def validate_context_relevance(self, context: str, question: str, response: str) -> bool:
        """
        Validate that the response is relevant to the context and question.

        Args:
            context: Context used for the response
            question: Original question
            response: Generated response

        Returns:
            True if response is contextually relevant, False otherwise
        """
        try:
            # Create a validation prompt to check if the response is based on the context
            validation_prompt = (
                "You are a validator checking if a response is based on the provided context.\n"
                "Context: {context}\n\n"
                "Question: {question}\n\n"
                "Response: {response}\n\n"
                "Is the response based on the provided context? Answer with only 'yes' or 'no'."
            ).format(context=context[:1000], question=question, response=response[:1000])

            validation_response = await self.client.chat.completions.create(
                model=self.fallback_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that validates responses."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )

            validation_result = validation_response.choices[0].message.content.strip().lower()
            is_relevant = "yes" in validation_result or "true" in validation_result

            logger.debug(f"Context relevance validation result: {is_relevant}")
            return is_relevant
        except Exception as e:
            logger.error(f"Error validating context relevance: {e}")
            # If validation fails, assume it's relevant to avoid blocking
            return True

    async def enforce_context_only_response(self, context: str, question: str,
                                          language: str = "en") -> Optional[str]:
        """
        Generate a response that strictly follows the context-only rule.

        Args:
            context: Context to use for generating the response
            question: Question from the user
            language: Language for the response ('en' or 'ur')

        Returns:
            Context-based response or fallback message if no context available
        """
        # If context is empty or just whitespace, return the fallback response
        if not context or not context.strip():
            if language == "ur":
                return "Is sawal ka jawab kitab ke matn mein mojood nahi hai."
            else:
                return "Is sawal ka jawab kitab ke matn mein mojood nahi hai."

        response = await self.generate_response(context, question, language)

        # Validate that the response is based on the context
        if response and await self.validate_context_relevance(context, question, response):
            return response
        else:
            # If the response doesn't seem to be based on context, return fallback
            if language == "ur":
                return "Is sawal ka jawab kitab ke matn mein mojood nahi hai."
            else:
                return "Is sawal ka jawab kitab ke matn mein mojood nahi hai."

    async def detect_hallucination(self, context: str, response: str) -> bool:
        """
        Detect if the response contains hallucinated information not in the context.

        Args:
            context: Context that was provided to the model
            response: Response generated by the model

        Returns:
            True if hallucination detected, False otherwise
        """
        try:
            # Create a prompt to check for hallucinations
            hallucination_prompt = (
                "You are checking if the response contains information not present in the context.\n\n"
                "CONTEXT:\n{context}\n\n"
                "RESPONSE:\n{response}\n\n"
                "Does the response contain specific information not found in the context? "
                "Answer with only 'yes' or 'no'."
            ).format(context=context[:1500], response=response[:1000])

            hallucination_response = await self.client.chat.completions.create(
                model=self.fallback_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that detects hallucinations."},
                    {"role": "user", "content": hallucination_prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )

            result = hallucination_response.choices[0].message.content.strip().lower()
            has_hallucination = "yes" in result

            logger.debug(f"Hallucination detection result: {has_hallucination}")
            return has_hallucination
        except Exception as e:
            logger.error(f"Error detecting hallucination: {e}")
            # If detection fails, assume no hallucination to avoid blocking
            return False


# Global instance for use throughout the application
llm_service = LLMService()