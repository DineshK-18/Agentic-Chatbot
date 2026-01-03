# tools/document_tool.py
import os
import re
import PyPDF2
import requests
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import aiofiles

class DocumentTool:
    """Document Understanding + Web Intelligence Agent"""
    
    def __init__(self):
        self.documents = {}
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    async def process_document_async(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process uploaded document asynchronously"""
        try:
            # Save file
            file_path = self.upload_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            # Extract text
            text = self._extract_text(file_path, filename)
            
            # Store document
            doc_id = len(self.documents) + 1
            self.documents[doc_id] = {
                "id": doc_id,
                "filename": filename,
                "file_path": str(file_path),
                "text": text,
                "uploaded_at": datetime.now().isoformat(),
                "word_count": len(text.split())
            }
            
            return {
                "status": "success",
                "document_id": doc_id,
                "filename": filename,
                "word_count": len(text.split()),
                "message": f"Document '{filename}' processed successfully"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process uploaded document synchronously"""
        try:
            # Extract text
            text = self._extract_text(file_path, filename)
            
            # Store document
            doc_id = len(self.documents) + 1
            self.documents[doc_id] = {
                "id": doc_id,
                "filename": filename,
                "file_path": file_path,
                "text": text,
                "uploaded_at": datetime.now().isoformat(),
                "word_count": len(text.split())
            }
            
            return {
                "status": "success",
                "document_id": doc_id,
                "filename": filename,
                "word_count": len(text.split()),
                "preview": text[:200] + "..." if len(text) > 200 else text
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from different file types"""
        if filename.lower().endswith('.pdf'):
            return self._extract_from_pdf(file_path)
        elif filename.lower().endswith('.txt'):
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"PDF extraction error: {str(e)}")
        return text.strip()
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                raise Exception(f"TXT read error: {str(e)}")
    
    def query_document(self, question: str, document_id: Optional[int] = None) -> Dict[str, Any]:
        """Query documents with a question"""
        if not self.documents:
            return {
                "source": "error",
                "answer": "No documents uploaded yet. Please upload a document first.",
                "confidence": 0
            }
        
        # If no specific document_id, search all documents
        if document_id is None:
            documents_to_search = list(self.documents.values())
        elif document_id in self.documents:
            documents_to_search = [self.documents[document_id]]
        else:
            return {
                "source": "error",
                "answer": f"Document ID {document_id} not found.",
                "confidence": 0
            }
        
        best_match = None
        best_score = 0
        
        # Simple keyword matching (in production, use vector search/embeddings)
        question_lower = question.lower()
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        
        for doc in documents_to_search:
            text = doc["text"].lower()
            doc_words = set(re.findall(r'\b\w+\b', text))
            
            # Calculate overlap
            overlap = len(question_words.intersection(doc_words))
            if len(question_words) > 0:
                score = overlap / len(question_words)
            else:
                score = 0
            
            # Find sentences containing question words
            sentences = re.split(r'[.!?]+', text)
            relevant_sentences = []
            
            for sentence in sentences:
                if any(word in sentence for word in question_words):
                    relevant_sentences.append(sentence.strip())
            
            if score > best_score:
                best_score = score
                best_match = {
                    "document_id": doc["id"],
                    "filename": doc["filename"],
                    "relevant_sentences": relevant_sentences[:3],  # Top 3 sentences
                    "score": score
                }
        
        if best_match and best_score > 0.3:
            answer = " ".join(best_match["relevant_sentences"])
            if not answer:
                answer = "The document contains relevant information but no specific answer was found."
            
            return {
                "source": "document",
                "answer": answer,
                "confidence": min(best_score * 100, 95),
                "document_info": {
                    "id": best_match["document_id"],
                    "filename": best_match["filename"]
                }
            }
        else:
            # Fallback to web search
            return self.search_web(question)
    
    def search_web(self, query: str) -> Dict[str, Any]:
        """Search the web for information"""
        try:
            # Using DuckDuckGo Instant Answer API (no API key required)
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('AbstractText'):
                return {
                    "source": "web_search",
                    "answer": data['AbstractText'],
                    "confidence": 70,
                    "url": data.get('AbstractURL', ''),
                    "search_query": query
                }
            elif data.get('RelatedTopics'):
                for topic in data['RelatedTopics'][:3]:  # First 3 results
                    if isinstance(topic, dict) and 'Text' in topic:
                        return {
                            "source": "web_search",
                            "answer": topic['Text'],
                            "confidence": 60,
                            "url": topic.get('FirstURL', ''),
                            "search_query": query
                        }
            
            return {
                "source": "web_search",
                "answer": "No specific information found online for your query.",
                "confidence": 20,
                "suggestion": "Try rephrasing your question or be more specific.",
                "search_query": query
            }
            
        except Exception as e:
            return {
                "source": "error",
                "answer": f"Web search error: {str(e)}",
                "confidence": 0,
                "search_query": query
            }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents"""
        return list(self.documents.values())