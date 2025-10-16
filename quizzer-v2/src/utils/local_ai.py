#!/usr/bin/env python3
"""
Local AI using Ollama
No API key needed, runs completely offline
"""

import json
import subprocess
import sys

class LocalAI:
    def __init__(self, model="llama3.2:3b"):
        """Initialize local AI with specified model."""
        self.model = model
        self.check_ollama_installed()
        self.check_model_available()  # Auto-pull model if not present
    
    def check_ollama_installed(self):
        """Check if Ollama is installed."""
        try:
            subprocess.run(['ollama', '--version'], 
                          capture_output=True, 
                          check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n❌ Ollama is not installed!")
            print("\nTo install Ollama:")
            print("1. Visit: https://ollama.com/download")
            print("2. Or run: brew install ollama")
            print("\nThen pull a model:")
            print(f"   ollama pull {self.model}")
            sys.exit(1)
    
    def check_model_available(self):
        """Check if the model is pulled."""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                   capture_output=True, 
                                   text=True, 
                                   check=True)
            if self.model.split(':')[0] not in result.stdout:
                print(f"\n📥 Pulling {self.model} model... (this may take a few minutes)")
                subprocess.run(['ollama', 'pull', self.model], check=True)
                print(f"✅ Model {self.model} ready!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error checking model: {e}")
            sys.exit(1)
    
    def generate(self, prompt, system_prompt="You are a helpful assistant.", temperature=0.7, max_tokens=500):
        """Generate response using local Ollama model."""
        try:
            # Build the full prompt
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Call ollama
            result = subprocess.run(
                ['ollama', 'run', self.model, full_prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
        except subprocess.TimeoutExpired:
            print("⚠️ Model took too long to respond")
            return None
        except Exception as e:
            print(f"⚠️ Error generating response: {e}")
            return None
    
    def generate_json(self, prompt, system_prompt="You are a helpful assistant. Always respond with valid JSON.", temperature=0.3, max_tokens=500):
        """Generate JSON response using local model."""
        # Add JSON instruction to prompt
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond with ONLY valid JSON in this EXACT format with simple string values, no nested objects:\n{{\n  \"level\": \"...\",\n  \"explanation\": \"your explanation as a simple string\"\n}}\nDo NOT use nested objects or arrays in your response."
        
        response = self.generate(json_prompt, system_prompt, temperature, max_tokens)
        
        if response:
            # Try to extract JSON from response
            try:
                # Sometimes models add explanation before/after JSON
                # Try to find JSON object
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    parsed = json.loads(json_str)
                    
                    # Fix nested explanation if present
                    if isinstance(parsed.get('explanation'), dict):
                        # Flatten nested explanation into a string
                        exp_dict = parsed['explanation']
                        exp_parts = []
                        for key, value in exp_dict.items():
                            if isinstance(value, bool):
                                exp_parts.append(f"{key}: {str(value)}")
                            else:
                                exp_parts.append(f"{key}: {value}")
                        parsed['explanation'] = '. '.join(exp_parts)
                    
                    return parsed
                else:
                    # Try parsing whole response
                    parsed = json.loads(response)
                    
                    # Fix nested explanation if present
                    if isinstance(parsed.get('explanation'), dict):
                        exp_dict = parsed['explanation']
                        exp_parts = []
                        for key, value in exp_dict.items():
                            if isinstance(value, bool):
                                exp_parts.append(f"{key}: {str(value)}")
                            else:
                                exp_parts.append(f"{key}: {value}")
                        parsed['explanation'] = '. '.join(exp_parts)
                    
                    return parsed
            except json.JSONDecodeError as e:
                # If JSON parsing fails, return a default structure
                return {"error": f"Could not parse JSON: {str(e)}", "raw_response": response[:300]}
            except Exception as e:
                # Catch any other errors during parsing
                return {"error": f"Error processing response: {type(e).__name__}: {str(e)}", "raw_response": response[:300] if response else "No response"}
        
        return None


def test_local_ai():
    """Test the local AI setup."""
    print("🧪 Testing Local AI with Ollama...")
    
    ai = LocalAI()
    ai.check_model_available()
    
    # Test simple generation
    print("\n📝 Test 1: Simple question")
    response = ai.generate("What is 2+2?", "You are a math tutor.", temperature=0.1, max_tokens=50)
    print(f"Response: {response}")
    
    # Test JSON generation
    print("\n📝 Test 2: JSON response")
    response = ai.generate_json(
        'Generate a quiz question about Python. Format: {"question": "...", "difficulty": "easy/medium/hard"}',
        "You are a quiz generator.",
        temperature=0.7,
        max_tokens=150
    )
    print(f"Response: {json.dumps(response, indent=2)}")
    
    print("\n✅ Local AI is working!")


if __name__ == "__main__":
    test_local_ai()
