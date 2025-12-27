from typing import List, Optional
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from database import DatabaseManager
import logging
import hashlib
from collections import defaultdict

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import cohere with fallbacks
try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Failed to import cohere: {e}")
    COHERE_AVAILABLE = False

from pydantic import BaseModel

class Document(BaseModel):
    id: str
    content: str
    metadata: dict
    created_at: str

class RAGService:
    def __init__(self):
        # Initialize Cohere client if available
        if COHERE_AVAILABLE:
            cohere_api_key = os.getenv("COHERE_API_KEY")
            if cohere_api_key:
                try:
                    self.cohere_client = cohere.Client(cohere_api_key)
                    logger.info("Cohere client initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize Cohere client: {e}")
                    logger.info("Some features will be disabled.")
                    self.cohere_client = None
            else:
                logger.warning("COHERE_API_KEY not set. Some features will be disabled.")
                self.cohere_client = None
        else:
            logger.warning("Cohere package not available. Some features will be disabled.")
            self.cohere_client = None

        # Initialize in-memory document storage instead of Qdrant
        self.documents = {}  # Store documents by ID
        self.inverted_index = defaultdict(list)  # Simple text-based search index

        # Initialize database manager
        self.db_manager = DatabaseManager()

        logger.info("RAGService initialized with in-memory search (no Qdrant dependency)")

    def _simple_tokenize(self, text):
        """Simple tokenization for building search index"""
        import re
        # Simple word tokenization, convert to lowercase
        tokens = re.findall(r'\b\w+\b', text.lower())
        return set(tokens)  # Use set to get unique tokens

    def _calculate_similarity(self, query_tokens, doc_tokens):
        """Calculate simple Jaccard similarity between query and document"""
        query_set = set(query_tokens)
        doc_set = set(doc_tokens)

        if len(query_set) == 0 or len(doc_set) == 0:
            return 0.0

        intersection = query_set.intersection(doc_set)
        union = query_set.union(doc_set)

        return len(intersection) / len(union) if len(union) > 0 else 0.0

    async def load_documents_from_db(self):
        """Load documents from Neon Postgres into memory for searching"""
        if hasattr(self.db_manager, 'has_pool') and self.db_manager.has_pool:
            try:
                # Get all documents from the database - use a direct approach to get all documents
                # Instead of using search_documents with empty query, let's try to get all documents
                # First, let's get the count to understand what we're working with
                async with self.db_manager.pool.acquire() as conn:
                    count = await conn.fetchval("SELECT COUNT(*) FROM documents")
                    logger.info(f"Total documents in database: {count}")

                # Now get all documents using the search method with empty query
                # The database method should return all documents when query is empty
                db_docs = await self.db_manager.search_documents("", limit=1000)  # Get all documents
                logger.info(f"Retrieved {len(db_docs)} documents from database search")

                for doc in db_docs:
                    doc_id = doc.get('id') or doc.get('doc_id', str(uuid.uuid4()))
                    content = doc.get('content', '')
                    metadata = doc.get('metadata', {})

                    # Store the document in memory
                    self.documents[doc_id] = {
                        "id": doc_id,
                        "content": content,
                        "metadata": metadata,
                        "created_at": doc.get('created_at', datetime.now().isoformat()),
                        "tokens": self._simple_tokenize(content)  # For search indexing
                    }

                    # Update the inverted index for search
                    content_tokens = self._simple_tokenize(content)
                    for token in content_tokens:
                        if doc_id not in self.inverted_index[token]:
                            self.inverted_index[token].append(doc_id)

                logger.info(f"Successfully loaded {len(db_docs)} documents into in-memory search index")
                return len(db_docs)
            except Exception as e:
                logger.error(f"Error loading documents from database: {e}")
                import traceback
                traceback.print_exc()
                return 0
        else:
            logger.warning("Database manager not available or not connected")
            return 0

    async def connect_to_neon_db(self):
        """Establish connection to Neon Postgres database"""
        await self.db_manager.connect()
        # After connecting, load documents from the database into memory
        await self.load_documents_from_db()

    async def embed_text(self, text: str, input_type: str = "search_document") -> List[float]:
        """Generate embeddings for text using Cohere or fallback method"""
        if COHERE_AVAILABLE and self.cohere_client:
            try:
                response = self.cohere_client.embed(
                    texts=[text],
                    model="embed-english-light-v3.0",
                    input_type=input_type
                )
                return response.embeddings[0]
            except Exception as e:
                logger.error(f"Error generating embeddings with Cohere: {e}")

        # Fallback: Return a simple deterministic vector based on the text content
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        vector = [float(ord(c) % 1000) / 1000.0 for c in text_hash]
        # Pad or truncate to expected size (384)
        while len(vector) < 384:
            vector.append(0.0)
        return vector[:384]

    async def store_document(self, content: str, metadata: dict = None) -> str:
        """Store a document in in-memory storage with text indexing"""
        if metadata is None:
            metadata = {}

        doc_id = str(uuid.uuid4())

        # Store the document in memory
        self.documents[doc_id] = {
            "id": doc_id,
            "content": content,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "tokens": self._simple_tokenize(content)  # For search indexing
        }

        # Update the inverted index for search
        content_tokens = self._simple_tokenize(content)
        for token in content_tokens:
            if doc_id not in self.inverted_index[token]:
                self.inverted_index[token].append(doc_id)

        # Store in Neon Postgres as well if available
        if hasattr(self.db_manager, 'has_pool') and self.db_manager.has_pool:
            # Convert metadata to JSON string for database storage
            import json
            json_metadata = json.dumps(metadata) if isinstance(metadata, dict) else metadata
            try:
                await self.db_manager.store_document(doc_id, content, json_metadata)
            except Exception as e:
                logger.error(f"Error storing document in database: {e}")

        return doc_id

    async def search_documents(self, query: str, limit: int = 5) -> List[dict]:
        """Search for relevant documents using in-memory text-based search"""
        try:
            logger.info(f"Performing in-memory search for query: {query}")

            # Tokenize the query
            query_tokens = self._simple_tokenize(query)

            if not query_tokens:
                logger.info("No tokens found in query, returning empty results")
                return []

            # Find documents that contain query tokens
            candidate_doc_ids = set()

            # Get documents that contain any of the query tokens
            for token in query_tokens:
                if token in self.inverted_index:
                    candidate_doc_ids.update(self.inverted_index[token])

            if not candidate_doc_ids:
                logger.info("No matching documents found in index")
                return []

            # Calculate similarity scores for each candidate document
            scored_docs = []
            for doc_id in candidate_doc_ids:
                if doc_id in self.documents:
                    doc_tokens = self.documents[doc_id]["tokens"]
                    similarity_score = self._calculate_similarity(query_tokens, doc_tokens)

                    if similarity_score > 0:  # Only include documents with some similarity
                        scored_docs.append({
                            "doc": self.documents[doc_id],
                            "score": similarity_score
                        })

            # Sort by similarity score (highest first)
            scored_docs.sort(key=lambda x: x["score"], reverse=True)

            # Format results to match the expected structure
            results = []
            for item in scored_docs[:limit]:  # Limit to requested number
                doc = item["doc"]
                results.append({
                    "id": doc["id"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "score": item["score"]
                })

            logger.info(f"Found {len(results)} search results")
            return results
        except Exception as e:
            logger.error(f"Error in search_documents: {e}")
            import traceback
            traceback.print_exc()
            # Return empty results if search fails
            return []

    async def generate_response(self, query: str, context: str = "") -> str:
        """Generate a response using Cohere based on query and context"""
        if COHERE_AVAILABLE and self.cohere_client:
            try:
                # Detect the language of the query to provide appropriate response
                detected_lang = self.detect_language(query)
                logger.info(f"Detected language: {detected_lang}")

                # Prepare the message content
                full_context = f"Context: {context}\n\n" if context else ""

                # Customize message based on detected language
                if detected_lang == 'ur':  # Urdu
                    message = f"""
                    {full_context}
                    سوال: {query}

                    براہ کرم فزیکل ای آئی اور روبوٹکس کے درسی منصوبے کے مواد کی بنیاد پر جامع جواب فراہم کریں۔
                    اگر آپ کے پاس کافی معلومات نہیں ہیں تو واضح طور پر کہیں۔
                    جواب اردو میں ہونا چاہیے۔
                    """
                else:  # Default to English
                    message = f"""
                    {full_context}
                    Question: {query}

                    Please provide a comprehensive answer based on the Physical AI & Robotics textbook content.
                    If you don't have enough information, say so clearly.
                    """

                # Try different models in order of preference
                models_to_try = ["command", "command-light", "command-r", "command-r-plus", "command-nightly", "base", "base-light"]
                response = None

                for model in models_to_try:
                    try:
                        response = self.cohere_client.chat(
                            model=model,
                            message=message,
                            max_tokens=500,
                            temperature=0.7
                        )
                        logger.info(f"Successfully used model: {model}")
                        break
                    except Exception as model_error:
                        logger.warning(f"Model {model} not available: {model_error}")
                        continue

                if response is not None:
                    return response.text.strip()
                else:
                    # If no models are available, return a helpful message
                    if detected_lang == 'ur':
                        return """AI سروس کا استعمال کرنے کے لیے ماڈل کی رسائی کی پابندیوں کی وجہ سے دستیاب نہیں ہے۔
                        یہ اس وجہ سے ہو سکتا ہے:
                        1. آپ کے کوہیر API کلید کے پاس درکار ماڈلز تک رسائی نہیں ہے
                        2. ماڈلز کو ختم کر دیا گیا ہے یا نام تبدیل کر دیا گیا ہے
                        3. آپ کا اکاؤنٹ ٹیئر ان ماڈلز کی حمایت نہیں کرتا

                        براہ کرم اپنی API کلید اور ماڈل تک رسائی چیک کریں، یا معاونت کے لیے رابطہ کریں۔"""
                    else:
                        return """AI service is not currently available due to model access restrictions.
                        This may be because:
                        1. Your Cohere API key doesn't have access to the required models
                        2. The models have been deprecated or renamed
                        3. Your account tier doesn't support these models

                        Please check your API key and model access, or contact support for assistance."""

            except Exception as e:
                logger.error(f"Error generating response: {e}")
                return "Sorry, I encountered an error while processing your request."
        else:
            # Provide a more helpful fallback response instead of just an error
            detected_lang = self.detect_language(query)
            logger.info(f"Detected language: {detected_lang}")

            if detected_lang == 'ur':  # Urdu
                return """میں فزیکل ای آئی اور روبوٹکس کے بارے میں معلومات فراہم کر سکتا ہوں۔

                روبوٹکس ایک انجینئرنگ کی شاخ ہے جس میں روبوٹس کے ڈیزائن، تعمیر، اور استعمال کا مطالعہ کیا جاتا ہے۔
                یہ میکانکی انجینئرنگ، الیکٹرانک انجینئرنگ، اور کمپیوٹر سائنس کا ایک مجموعہ ہے۔

                اگر آپ کو کوہیر API کلید سیٹ کرنا ہے تو، یہ کام کرے گا۔"""
            else:  # Default to English
                # For "what is robotics" query specifically, provide a helpful response
                if "robotics" in query.lower():
                    return """Robotics is an interdisciplinary branch of engineering and science that includes mechanical engineering, electrical engineering, computer science, and others. It deals with the design, construction, operation, and use of robots, as well as computer systems for their control, sensory feedback, and information processing.

                    These technologies are used to develop machines that can substitute for humans. Robots can be used in any situation and condition designed for, including situations that are dangerous for humans or access to small spaces.

                    To get full AI functionality, please set the COHERE_API_KEY environment variable."""
                else:
                    return """I can provide information about Physical AI and Robotics.

                    To get full AI functionality with advanced responses, please set the COHERE_API_KEY environment variable with a valid API key from Cohere (https://dashboard.cohere.com/).

                    In the meantime, I'm using a basic response system. For a query about "what is robotics", I can tell you that robotics is an interdisciplinary branch of engineering that deals with the design, construction, and operation of robots."""

    async def generate_paper(self, topic: str, length: int = 3000) -> str:
        """Generate a research paper on a given topic"""
        if COHERE_AVAILABLE and self.cohere_client:
            try:
                message = f"""
                Write a comprehensive research paper about {topic}.
                The paper should be approximately {length} words long.
                Include the following sections:
                1. Introduction
                2. Literature Review
                3. Methodology (if applicable)
                4. Discussion
                5. Conclusion
                6. References

                Make sure the paper is well-structured, academic in tone, and includes relevant information about Physical AI and Robotics.
                """

                # Try different models in order of preference
                models_to_try = ["command", "command-light", "command-r", "command-r-plus", "command-nightly", "base", "base-light"]
                response = None

                for model in models_to_try:
                    try:
                        response = self.cohere_client.chat(
                            model=model,
                            message=message,
                            max_tokens=length,
                            temperature=0.7
                        )
                        logger.info(f"Successfully used model for paper: {model}")
                        break
                    except Exception as model_error:
                        logger.warning(f"Model {model} not available for paper generation: {model_error}")
                        continue

                if response is not None:
                    paper_content = response.text.strip()

                    # Store the generated paper in the database
                    await self.store_document(
                        content=paper_content,
                        metadata={
                            "type": "generated_paper",
                            "topic": topic,
                            "length": length
                        }
                    )

                    return paper_content
                else:
                    # If no models are available, return a helpful message
                    return """AI service is not currently available for paper generation due to model access restrictions.
                    This may be because:
                    1. Your Cohere API key doesn't have access to the required models
                    2. The models have been deprecated or renamed
                    3. Your account tier doesn't support these models

                    Please check your API key and model access, or contact support for assistance."""

            except Exception as e:
                logger.error(f"Error generating paper: {e}")
                return "Sorry, I encountered an error while generating the paper."
        else:
            # Provide a helpful fallback when no AI service is configured
            if "robotics" in topic.lower() or "physical ai" in topic.lower():
                return f"""# Research Paper on {topic}

## Abstract
This paper explores the fundamental concepts of {topic}, examining its applications, technologies, and future potential in various fields.

## Introduction
{topic} represents a significant advancement in the field of artificial intelligence and engineering. This interdisciplinary field combines mechanical engineering, electrical engineering, computer science, and other disciplines to create autonomous systems and machines.

## Literature Review
The field of {topic} has evolved significantly over the past decades. Early developments focused on simple mechanical automation, while modern approaches incorporate sophisticated AI algorithms, sensor systems, and adaptive learning capabilities.

## Discussion
Modern {topic} applications span numerous industries including manufacturing, healthcare, space exploration, and domestic applications. The integration of AI has enabled robots to perform increasingly complex tasks with greater autonomy.

## Conclusion
The future of {topic} holds tremendous potential as technologies continue to advance. Key areas of development include improved autonomy, human-robot interaction, and specialized applications in challenging environments.

## References
1. Modern Robotics Textbooks and Journals
2. IEEE Robotics and Automation Society Publications
3. International Conference on Robotics and Automation Proceedings

Note: This is a basic template. To generate full AI-powered research papers, please set the COHERE_API_KEY environment variable."""
            else:
                return f"""# Research Paper on {topic}

This is a basic template for a research paper on {topic}.

The full AI-powered paper generation requires a Cohere API key to generate comprehensive, detailed research content. To enable this feature, please set the COHERE_API_KEY environment variable with a valid API key from Cohere (https://dashboard.cohere.com/).

In the meantime, you can structure your research paper with the following sections:
1. Abstract
2. Introduction
3. Literature Review
4. Methodology
5. Discussion
6. Conclusion
7. References

For {topic}, consider exploring relevant academic databases, journals, and publications in the field."""

    async def load_documents_from_db(self):
        """Load documents from Neon Postgres if available"""
        if hasattr(self.db_manager, 'has_pool') and self.db_manager.has_pool:
            try:
                return await self.db_manager.search_documents("", limit=100)  # Get all documents
            except Exception as e:
                logger.error(f"Error loading documents from database: {e}")
                return []
        else:
            logger.warning("Database manager not available or not connected")
            return []

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text
        Uses Unicode range detection for Urdu as a fallback to avoid import issues
        """
        # First check for Urdu characters using Unicode range
        # Urdu characters are in the Arabic block (0x0600-0x06FF) and Arabic Supplement block (0x0750-0x077F)
        # Also check for Arabic Presentation Forms (0xFB50-0xFDFF, 0xFE70-0xFEFF)
        for char in text:
            if '\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F' or '\uFB50' <= char <= '\uFDFF' or '\uFE70' <= char <= '\uFEFF':
                return "ur"

        # If no Urdu characters found, try langdetect as fallback
        try:
            import langdetect
            return langdetect.detect(text)
        except ImportError:
            logger.warning("langdetect package not available, defaulting to English")
            # If langdetect is not available, default to English
            return "en"
        except:
            # If detection fails for any reason, default to English
            return "en"  # Default to English if detection fails