"""GPT-based answer generation service"""
import logging
from typing import Optional
from openai import OpenAI
from app.config import get_settings

logger = logging.getLogger(__name__)


class GPTService:
    """Service for generating answers using GPT"""

    def __init__(self):
        """Initialize GPT service"""
        self.settings = get_settings()
        try:
            self.client = OpenAI(api_key=self.settings.openai_api_key)
            logger.info(f"GPT service initialized with model: {self.settings.openai_model}")
        except Exception as e:
            logger.error(f"Failed to initialize GPT service: {e}")
            raise

    def generate_answer(
        self,
        question: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate answer based on question and context

        Args:
            question: User question
            context: Context retrieved from documents
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response

        Returns:
            Generated answer
        """
        try:
            if not question or not context:
                raise ValueError("Question and context cannot be empty")

            system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
            Answer questions accurately and concisely using only the information provided in the context. 
            If the context doesn't contain enough information to answer the question, say so clearly.
            Format your response in a clear and organized manner."""

            user_prompt = f"""Context:
{context}

Question:
{question}

Please provide a detailed answer based on the context provided."""

            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            answer = response.choices[0].message.content
            logger.info(f"Generated answer for question (tokens: {response.usage.total_tokens})")
            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def generate_summary(
        self,
        text: str,
        max_tokens: int = 300,
    ) -> str:
        """
        Generate summary of text

        Args:
            text: Text to summarize
            max_tokens: Maximum tokens in summary

        Returns:
            Generated summary
        """
        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please provide a concise summary of the following text:\n\n{text}",
                    }
                ],
                max_tokens=max_tokens,
            )

            summary = response.choices[0].message.content
            logger.info("Generated text summary")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise

    def stream_answer(
        self,
        question: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        """
        Stream answer response

        Args:
            question: User question
            context: Context retrieved from documents
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Yields:
            Generated text chunks
        """
        try:
            system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
            Answer questions accurately and concisely using only the information provided in the context."""

            user_prompt = f"""Context:
{context}

Question:
{question}

Please provide a detailed answer based on the context provided."""

            with self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            ) as response:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error streaming answer: {e}")
            raise
