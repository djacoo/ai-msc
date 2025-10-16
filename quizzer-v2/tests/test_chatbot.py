#!/usr/bin/env python3
"""
Test Chatbot Integration
Quick test to verify chatbot works with course notes
"""

import sys
from pathlib import Path

# Add parent to sys.path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_chatbot():
    """Test chatbot functionality."""
    print("🧪 Testing Chatbot Integration\n")
    print("=" * 60)
    
    # Find repo root
    repo_root = Path(__file__).parent.parent.parent
    
    # Initialize AI
    print("\n1️⃣ Initializing AI engine...")
    try:
        from src.utils.local_ai import LocalAI
        ai = LocalAI("llama3.2:3b")
        print("   ✓ AI engine ready")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Initialize grounding
    print("\n2️⃣ Initializing PDF grounding...")
    try:
        from src.utils.pdf_grounding import PDFGroundingEngine
        grounding = PDFGroundingEngine(str(repo_root))
        print("   ✓ PDF grounding ready")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Initialize chatbot
    print("\n3️⃣ Initializing chatbot...")
    try:
        from src.engines.chatbot_engine import ChatbotEngine
        chatbot = ChatbotEngine(str(repo_root), ai, grounding)
        print("   ✓ Chatbot engine ready")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Set course
    print("\n4️⃣ Setting course (NLP)...")
    try:
        note_files = ["courses/natural-language-processing/notes/NLP Appunti.pdf"]
        chatbot.set_course("nlp", note_files)
        print("   ✓ Course configured")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test search
    print("\n5️⃣ Testing note search...")
    try:
        results = chatbot.get_relevant_context("tokenization", max_pages=2)
        if results:
            print(f"   ✓ Found {len(results)} relevant pages")
            for i, result in enumerate(results, 1):
                print(f"     - Page {result['page']}: Score {result['score']}")
        else:
            print("   ⚠️  No results found (this might be OK if the topic isn't in notes)")
    except Exception as e:
        print(f"   ✗ Search failed: {e}")
        return False
    
    # Test question answering
    print("\n6️⃣ Testing question answering...")
    try:
        question = "What is tokenization?"
        print(f"   Question: '{question}'")
        result = chatbot.answer_question(question)
        
        if result.get("found_info"):
            print(f"   ✓ Answer generated ({len(result['answer'])} chars)")
            print(f"   ✓ Sources: {len(result.get('sources', []))} citations")
            print(f"\n   Preview: {result['answer'][:150]}...")
        else:
            print(f"   ⚠️  No information found: {result['answer']}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All chatbot tests passed!\n")
    return True


if __name__ == "__main__":
    success = test_chatbot()
    sys.exit(0 if success else 1)
