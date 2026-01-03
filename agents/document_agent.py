# agents/document_agent.py - Document Understanding + Web Intelligence Agent
import PyPDF2
import requests
from typing import Dict, Any, Optional
import os
from io import BytesIO
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

class DocumentAgent:
    def __init__(self):
        self.document_text = ""
        self.document_name = ""
        self.vector_store = None
        self.qa_chain = None
        
        # Initialize embeddings and LLM
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize a simple LLM pipeline (using a small model for demo)
        self.llm_pipeline = pipeline(
            "text-generation",
            model="gpt2",
            max_length=200,
            temperature=0.7
        )
        
        self.llm = HuggingFacePipeline(pipeline=self.llm_pipeline)
    
    def process_document(self, file_content: bytes, filename: str):
        """Process uploaded document"""
        self.document_name = filename
        
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            self.document_text = self._extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.txt'):
            self.document_text = file_content.decode('utf-8')
        else:
            raise ValueError("Unsupported file format. Please upload PDF or TXT.")
        
        # Create vector store for document
        self._create_vector_store()
    
    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        text = ""
        pdf_file = BytesIO(file_content)
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return text
    
    def _create_vector_store(self):
        """Create vector store from document text"""
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        
        chunks = text_splitter.split_text(self.document_text)
        
        # Create vector store
        self.vector_store = FAISS.from_texts(chunks, self.embeddings)
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3})
        )
    
    def query_document(self, question: str) -> Dict[str, Any]:
        """Query the document with a question"""
        if not self.document_text:
            return {
                "source": "error",
                "answer": "No document uploaded. Please upload a document first.",
                "confidence": 0.0
            }
        
        try:
            # Use the QA chain to get answer
            result = self.qa_chain({"query": question})
            answer = result.get('result', '').strip()
            
            # Calculate confidence (simplified)
            confidence = self._calculate_confidence(question, answer)
            
            if confidence > 0.3:
                return {
                    "source": "document",
                    "answer": answer,
                    "confidence": confidence,
                    "document": self.document_name
                }
            else:
                return {
                    "source": "document",
                    "answer": "This information is not clearly mentioned in the document.",
                    "confidence": confidence,
                    "suggestion": "Would you like me to search the web for this information?"
                }
                
        except Exception as e:
            return {
                "source": "error",
                "answer": f"Error processing document query: {str(e)}",
                "confidence": 0.0
            }
    
    def search_web(self, query: str) -> Dict[str, Any]:
        """Search the web for information"""
        try:
            # Using DuckDuckGo instant answer API as fallback
            # In production, you would use Google Search API with proper API key
            ddg_url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(ddg_url, params=params)
            data = response.json()
            
            if data.get('AbstractText'):
                return {
                    "source": "web_search",
                    "answer": data['AbstractText'],
                    "confidence": 0.7,
                    "url": data.get('AbstractURL', '')
                }
            elif data.get('RelatedTopics') and len(data['RelatedTopics']) > 0:
                first_result = data['RelatedTopics'][0]
                if isinstance(first_result, dict) and 'Text' in first_result:
                    return {
                        "source": "web_search",
                        "answer": first_result['Text'],
                        "confidence": 0.6,
                        "url": first_result.get('FirstURL', '')
                    }
            
            return {
                "source": "web_search",
                "answer": "I couldn't find specific information online. Please try rephrasing your question.",
                "confidence": 0.2
            }
            
        except Exception as e:
            return {
                "source": "error",
                "answer": f"Web search error: {str(e)}",
                "confidence": 0.0
            }
    
    def _calculate_confidence(self, question: str, answer: str) -> float:
        """Calculate confidence score for answer"""
        # Simple confidence calculation
        # In production, use more sophisticated methods
        
        if not answer or len(answer) < 10:
            return 0.1
        
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        
        # Calculate word overlap
        overlap = len(question_words.intersection(answer_words))
        total_question_words = len(question_words)
        
        if total_question_words == 0:
            return 0.3
        
        confidence = min(overlap / total_question_words * 2, 0.9)
        
        # Adjust based on answer length and content
        if "not sure" in answer.lower() or "not mentioned" in answer.lower():
            confidence *= 0.5
        
        return confidence