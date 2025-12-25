from typing import List, Optional
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from database import DatabaseManager
from langdetect import detect

load_dotenv()

class Document(BaseModel):
    id: str
    content: str
    metadata: dict
    created_at: str

class RAGService:
    def __init__(self):
        # Initialize Cohere client
        cohere_api_key = os.getenv("COHERE_API_KEY")
        if cohere_api_key:
            try:
                self.cohere_client = cohere.Client(cohere_api_key)
                print("Cohere client initialized successfully")
            except Exception as e:
                print(f"WARNING: Failed to initialize Cohere client: {e}")
                print("Some features will be disabled.")
                self.cohere_client = None
        else:
            print("WARNING: COHERE_API_KEY not set. Some features will be disabled.")
            self.cohere_client = None

        # Initialize Qdrant client
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        # Only try to connect to cloud if we have both URL and API key and the URL is not a placeholder
        if qdrant_url and qdrant_api_key and "your_" not in qdrant_url and "example" not in qdrant_url:
            try:
                self.qdrant_client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                    prefer_grpc=True
                )
                print("Connected to Qdrant Cloud successfully")
            except Exception as e:
                print(f"Failed to connect to Qdrant Cloud: {e}")
                print("Using in-memory storage for testing")
                # Use in-memory Qdrant client
                self.qdrant_client = QdrantClient(":memory:")
        else:
            print("QDRANT_URL or QDRANT_API_KEY not set or using placeholder values. Using in-memory storage for testing")
            # Initialize in-memory Qdrant client
            self.qdrant_client = QdrantClient(":memory:")

        # Initialize database manager
        self.db_manager = DatabaseManager()

        # Ensure the collection exists (this will create it if needed)
        self._ensure_collection_exists()

        # Verify that the client has the required methods
        if not hasattr(self.qdrant_client, 'search'):
            print("WARNING: Qdrant client doesn't have 'search' method. This may indicate an issue with the client initialization.")

    def _ensure_collection_exists(self):
        """Ensure the Qdrant collection exists"""
        try:
            # Check if the collection exists
            self.qdrant_client.get_collection("physical_ai_docs")
        except Exception as e:
            print(f"Collection doesn't exist, creating it: {e}")
            try:
                # Create the collection with proper vector configuration
                self.qdrant_client.create_collection(
                    collection_name="physical_ai_docs",
                    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),  # Updated to match Cohere's embedding size
                )
                print("Collection 'physical_ai_docs' created successfully")
            except Exception as create_error:
                print(f"Failed to create collection: {create_error}")

    async def connect_to_neon_db(self):
        """Establish connection to Neon Postgres database"""
        await self.db_manager.connect()

    async def embed_text(self, text: str, input_type: str = "search_document") -> List[float]:
        """Generate embeddings for text using Cohere"""
        if not self.cohere_client:
            # Return a simple fallback embedding if Cohere is not available
            # This is a basic fallback - in production, you might want to use a different embedding service
            import hashlib
            # Create a deterministic vector based on the text content
            text_hash = hashlib.md5(text.encode()).hexdigest()
            # Convert hash to a list of floats (simplified approach)
            vector = [float(ord(c) % 1000) / 1000.0 for c in text_hash]
            # Pad or truncate to expected size (384 as per collection config)
            while len(vector) < 384:
                vector.append(0.0)
            return vector[:384]

        try:
            response = self.cohere_client.embed(
                texts=[text],
                model="embed-english-light-v3.0",  # Using a lighter model that may be more accessible
                input_type=input_type
            )
            return response.embeddings[0]
        except Exception as e:
            print(f"Error generating embeddings with Cohere: {e}")
            # Return a fallback embedding if Cohere fails
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()
            vector = [float(ord(c) % 1000) / 1000.0 for c in text_hash]
            while len(vector) < 384:
                vector.append(0.0)
            return vector[:384]

    async def store_document(self, content: str, metadata: dict = None) -> str:
        """Store a document in Qdrant with embeddings"""
        if metadata is None:
            metadata = {}

        doc_id = str(uuid.uuid4())
        vector = await self.embed_text(content)

        self.qdrant_client.upsert(
            collection_name="physical_ai_docs",
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload={
                        "content": content,
                        "metadata": metadata,
                        "created_at": datetime.now().isoformat()
                    }
                )
            ]
        )

        # Store in Neon Postgres as well if available
        if self.db_manager.has_pool:
            # Convert metadata to JSON string for database storage
            import json
            json_metadata = json.dumps(metadata) if isinstance(metadata, dict) else metadata
            await self.db_manager.store_document(doc_id, content, json_metadata)

        return doc_id

    async def search_documents(self, query: str, limit: int = 5) -> List[dict]:
        """Search for relevant documents in Qdrant"""
        query_vector = await self.embed_text(query, input_type="search_query")

        print(f"Qdrant client type: {type(self.qdrant_client)}")
        print(f"Qdrant client has search method: {hasattr(self.qdrant_client, 'search')}")

        # Check if the collection exists before searching
        try:
            self.qdrant_client.get_collection("physical_ai_docs")
            print("Collection 'physical_ai_docs' exists")
        except Exception as e:
            print(f"Collection 'physical_ai_docs' does not exist: {e}")
            # Try to create it again
            try:
                from qdrant_client.http import models
                self.qdrant_client.create_collection(
                    collection_name="physical_ai_docs",
                    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),  # Updated to match Cohere's embedding size
                )
                print("Collection 'physical_ai_docs' created successfully")
            except Exception as create_error:
                print(f"Failed to create collection: {create_error}")
                return []

        # Check if the qdrant_client has the search method
        if not hasattr(self.qdrant_client, 'search'):
            print("Qdrant client doesn't have search method - likely using in-memory mode without proper initialization")
            # Return empty results if search method is not available
            return []

        try:
            search_results = self.qdrant_client.search(
                collection_name="physical_ai_docs",
                query_vector=query_vector,
                limit=limit,
                with_payload=True
            )
        except Exception as e:
            print(f"Qdrant search error: {e}")
            import traceback
            traceback.print_exc()
            # Return empty results if search fails
            return []

        results = []
        for result in search_results:
            if result.payload:
                results.append({
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score
                })

        print(f"Found {len(results)} search results")
        return results

    async def generate_response(self, query: str, context: str = "") -> str:
        """Generate a response using Cohere based on query and context"""
        if not self.cohere_client:
            # Provide a more helpful fallback response instead of just an error
            # This could be expanded to use a local model or simple rule-based responses
            detected_lang = self.detect_language(query)
            print(f"Detected language: {detected_lang}")

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

        try:
            # Detect the language of the query to provide appropriate response
            # Use the same robust language detection as in main.py
            detected_lang = self.detect_language(query)
            print(f"Detected language: {detected_lang}")

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
            # Using more commonly available models
            models_to_try = ["command", "command-light", "command-r", "command-r-plus", "command-nightly", "base", "base-light"]
            response = None

            for model in models_to_try:
                try:
                    # Generate response using Cohere Chat API
                    response = self.cohere_client.chat(
                        model=model,
                        message=message,
                        max_tokens=500,
                        temperature=0.7
                    )
                    print(f"Successfully used model: {model}")
                    break
                except Exception as model_error:
                    print(f"Model {model} not available: {model_error}")
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
            print(f"Error generating response: {e}")
            return "Sorry, I encountered an error while processing your request."

    async def generate_paper(self, topic: str, length: int = 3000) -> str:
        """Generate a research paper on a given topic"""
        if not self.cohere_client:
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
            # Using more commonly available models
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
                    print(f"Successfully used model for paper: {model}")
                    break
                except Exception as model_error:
                    print(f"Model {model} not available for paper generation: {model_error}")
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
            print(f"Error generating paper: {e}")
            return "Sorry, I encountered an error while generating the paper."

    async def load_documents_from_db(self):
        """Load documents from Neon Postgres if available"""
        if not self.db_manager.has_pool:
            return []

        try:
            return await self.db_manager.search_documents("", limit=100)  # Get all documents
        except Exception as e:
            print(f"Error loading documents from database: {e}")
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
            from langdetect import detect
            return detect(text)
        except ImportError:
            # If langdetect is not available, default to English
            return "en"
        except:
            # If detection fails for any reason, default to English
            return "en"  # Default to English if detection fails