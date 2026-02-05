from typing import List, Dict, Any, Optional
import re


class ResponseGenerator:
    """
    Generate natural language responses based on retrieved content
    """

    def __init__(self):
        # Define a prompt template to guide the response generation
        self.response_template = """Based on the book content, here is what I found about '{query}':

{retrieved_content}

Please provide a clear, natural language explanation based on this information. Your response should:
1. Use plain English to explain concepts
2. Avoid showing any code, technical syntax, or implementation details
3. Focus on the conceptual understanding and practical applications
4. Explain the "why" and "how" in natural language
5. Use complete sentences and proper paragraph structure
6. If technical terms are necessary, explain them in context"""

    def generate_response(self, query: str, search_results: List[Dict[str, Any]],
                         conversation_context: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate a natural language response based on search results
        """
        if not search_results:
            return "I cannot find relevant information in the book for your query."

        # Sanitize and format the retrieved content
        formatted_content = self._format_retrieved_content(search_results)

        # If sanitization removed all content, try a different approach
        if not formatted_content.strip():
            # Extract conceptual information from original results even if they contain code
            conceptual_content = self._extract_conceptual_content(search_results)
            if conceptual_content.strip():
                formatted_content = conceptual_content
            else:
                return "I cannot find relevant conceptual information in the book for your query."

        # Generate the response by formatting the retrieved content into natural language
        response = self._create_natural_language_response(query, formatted_content, conversation_context)

        # Additional check to ensure the response doesn't contain code or logs
        if self._contains_unwanted_patterns(response):
            # Try to reformat the response to remove code elements
            cleaned_response = self._remove_code_elements_from_response(response)
            if cleaned_response.strip() and not self._contains_unwanted_patterns(cleaned_response):
                return cleaned_response
            else:
                # If we still can't get a clean response, try to summarize the conceptual content
                conceptual_content = self._extract_conceptual_content(search_results)
                if conceptual_content.strip():
                    return f"Regarding your query about '{query}': Based on the book content, the main concept is: {conceptual_content}"
                else:
                    return "I found information related to your query in the book, but I cannot extract the conceptual information without technical details."

        return response

    def _contains_unwanted_patterns(self, text: str) -> bool:
        """
        Check if text contains unwanted patterns like code or logs
        """
        code_patterns = [
            r'\bdef\s+\w+\s*\(',  # Python function definitions
            r'\bclass\s+\w+',  # Class definitions
            r'\bimport\s+\w+',  # Import statements
            r'\bfrom\s+\w+\s+import',  # From import statements
            r'\bconsole\.\w+\s*\(',  # Console logging
            r'\bfunction\s+\w+\s*\(',  # JavaScript function definitions
            r'\bvar\s+\w+\s*=',  # Variable declarations
            r'\bconst\s+\w+\s*=',  # Constant declarations
            r'\blet\s+\w+\s*=',  # Let declarations
            r'\bif\s*\([^)]+\)\s*{',  # If statements with braces
            r'\bfor\s*\([^)]+\)\s*{',  # For loops with braces
            r'\bwhile\s*\([^)]+\)\s*{',  # While loops with braces
            r'\bdo\s*{[^}]+}\s*while',  # Do-while loops
            r'\btry\s*{',  # Try blocks
            r'\bcatch\s*\([^)]*\)\s*{',  # Catch blocks
            r'\bfinally\s*{',  # Finally blocks
            r'\basync\s+def',  # Async function definitions
            r'\bawait\s+\w+',  # Await statements
            r'\bprint\s*\(',  # Print statements
            r'\bstd::\w+',  # C++ standard library usage
            r'\b#include\s*<',  # C++ include statements
            r'\busing\s+namespace',  # C++ using namespace
            r'\bpublic\s+.*?\s+\w+\s*\(',  # Public method definitions
            r'\bprivate\s+.*?\s+\w+\s*\(',  # Private method definitions
            r'\bprotected\s+.*?\s+\w+\s*\(',  # Protected method definitions
            r'\breturn\s+.*?;',  # Return statements
            r'\bif\s*\([^)]+\):',  # Python-style if statements
            r'\bfor\s*.*?:',  # Python-style for loops
            r'\bwhile\s*.*?:',  # Python-style while loops
            r'\btry:',  # Python try statement
            r'\bexcept:',  # Python except statement
            r'\bfinally:',  # Python finally statement
            r'\bwith\s+.*?:',  # Python with statement
            r'\bwith\s*\(',  # With statements
            r'\b\w+\s*=\s*lambda',  # Lambda functions
            r'\bfn\s+\w+\s*<',  # Rust function definitions
            r'\bimpl\s+\w+',  # Rust implementations
            r'\bpackage\s+\w+',  # Package declarations
            r'\bmodule\s+\w+',  # Module declarations
        ]

        log_patterns = [
            r'\bDEBUG\b',
            r'\bINFO\b',
            r'\bWARNING\b',
            r'\bWARN\b',
            r'\bERROR\b',
            r'\bFATAL\b',
            r'\bTRACE\b',
            r'\[\d{4}-\d{2}-\d{2}',  # Date patterns like [2023-01-01
            r'\[\d{2}:\d{2}:\d{2}',  # Time patterns like [12:34:56
            r'LOG:\s*',
            r'log\.\w+\s*\(',
            r'\blogger\.\w+\s*\(',
            r'console\.(log|error|warn|debug)\s*\(',
            r'\[.*?\]\s*\[.*?\]\s*',  # Multiple bracket groups like [INFO][MAIN]
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # Full timestamp patterns
        ]

        combined_patterns = code_patterns + log_patterns

        for pattern in combined_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _format_retrieved_content(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format and sanitize retrieved content to remove code and technical formatting
        """
        formatted_parts = []

        for result in search_results:
            text = result['text']
            # Sanitize the text to remove code blocks and technical formatting
            sanitized_text = self._sanitize_content(text)

            if sanitized_text.strip():
                formatted_parts.append(sanitized_text)

        return "\n\n".join(formatted_parts)


    def _sanitize_content(self, content: str) -> str:
        """
        Sanitize content to remove code blocks, raw code, or other non-text elements
        """
        import re

        # Remove code blocks (```...``` or indented code)
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

        # Remove single-line code blocks (`code`)
        content = re.sub(r'`[^`]+`', '', content)

        # Remove potential Python-style indented code blocks (4+ spaces at start of lines)
        lines = content.split('\n')
        filtered_lines = []
        for line in lines:
            stripped_line = line.strip()

            # Skip lines that are clearly code-related
            if (re.match(r'^\s*def\s+', stripped_line) or
                re.match(r'^\s*class\s+', stripped_line) or
                re.match(r'^\s*import\s+', stripped_line) or
                re.match(r'^\s*from\s+', stripped_line) or
                re.match(r'^\s*console\.', stripped_line) or
                re.match(r'^\s*function\s+', stripped_line) or
                re.match(r'^\s*if\s*\(', stripped_line) or
                re.match(r'^\s*for\s*\(', stripped_line) or
                re.match(r'^\s*while\s*\(', stripped_line) or
                re.match(r'^\s*try\s*:', stripped_line) or
                re.match(r'^\s*except\s*:', stripped_line) or
                re.match(r'^\s*with\s+', stripped_line) or
                re.match(r'^\s*return\s+', stripped_line) or
                re.match(r'^\s*\w+\s*=\s*', stripped_line) or  # Variable assignments
                re.match(r'^\s*print\s*\(', stripped_line) or
                re.match(r'^\s*#.*', stripped_line) or  # Comments
                re.match(r'^\s*//.*', stripped_line) or  # JavaScript comments
                re.match(r'^\s*\*.*', stripped_line) or  # C-style comments continuation
                re.match(r'^\s*""".*"""', stripped_line) or  # Python docstrings
                re.match(r'^\s*\{.*\}', stripped_line) or  # Simple object literals
                re.match(r'^\s*\[.*\]', stripped_line)): # Simple array literals
                continue  # Skip this line

            # Remove inline code elements from the line
            line = re.sub(r'\b\w+\s*=\s*["\'][^"\']*["\']', '', line)  # Remove variable assignments
            line = re.sub(r'\b\w+\s*=\s*\d+', '', line)  # Remove variable assignments to numbers
            line = re.sub(r'\b\w+\s*\([^)]*\)', '', line)  # Remove function calls
            line = re.sub(r'\b\w+\s*\[\s*\]', '', line)  # Remove array declarations
            line = re.sub(r'\b(?:int|str|float|bool|list|dict|var|let|const|function|async|await)\b', '', line)  # Remove type keywords

            # Only add the line if it still has meaningful content after cleaning
            cleaned_line = line.strip()
            if cleaned_line and not re.match(r'^[\s\(\)\[\]\{\}\<\>\.,;:+=\-*\/%&|^!~]+$|^[\s\(\)\[\]\{\}\<\>\.,;:+=\-*\/%&|^!~=]+$|^$', cleaned_line):
                filtered_lines.append(cleaned_line)

        content = '\n'.join(filtered_lines)

        # Remove potential command-line prompts
        content = re.sub(r'^[>$]\s.*$', '', content, flags=re.MULTILINE)

        # Clean up excessive whitespace and normalize
        content = re.sub(r'\n\s*\n', '\n\n', content)  # Replace multiple newlines with double newline
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        content = content.strip()

        return content

    def _create_natural_language_response(self, query: str, formatted_content: str,
                                         conversation_context: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Create a natural language response from the formatted content
        """
        response_parts = []

        # Add context if there's conversation history
        if conversation_context:
            recent_context = conversation_context[-3:] if len(conversation_context) > 3 else conversation_context
            bot_responses = [item["text"] for item in recent_context if item["sender"] == "bot"]

            if bot_responses:
                response_parts.append(f"Referring back to our conversation:")
                response_parts.append(f"Previously, I mentioned: {bot_responses[-1][:200]}...")

        # Add the main response
        response_parts.append(f"Regarding your query about '{query}':")
        response_parts.append(f"Based on the book content:")
        response_parts.append(formatted_content)

        # Join all parts to form the final response
        final_response = " ".join(response_parts)

        # Ensure the response is properly formatted and doesn't contain raw code
        return self._post_process_response(final_response)

    def _post_process_response(self, response: str) -> str:
        """
        Perform final processing on the response to ensure it's in natural language
        """
        # Remove any remaining code-like patterns
        response = re.sub(r'\b\w+\s*=\s*["\'][^"\']*["\']', '', response)  # Remove variable assignments
        response = re.sub(r'\b\w+\s*=\s*\d+', '', response)  # Remove variable assignments to numbers
        response = re.sub(r'\b\w+\s*\(\s*\)', '', response)  # Remove function calls
        response = re.sub(r'\b\w+\s*\[\s*\]', '', response)  # Remove array declarations

        # Clean up any empty sections
        response = re.sub(r'\n\s*\n', '\n\n', response)
        response = re.sub(r'\s+', ' ', response)  # Normalize whitespace

        # Ensure proper sentence structure
        response = response.strip()

        return response

    def _extract_conceptual_content(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Extract conceptual information from search results, even if they contain code
        """
        conceptual_parts = []

        for result in search_results:
            text = result['text']
            # Split into sentences/paragraphs
            paragraphs = text.split('\n\n')

            for paragraph in paragraphs:
                # Look for sentences that are more conceptual rather than code
                sentences = paragraph.split('. ')

                for sentence in sentences:
                    sentence = sentence.strip()
                    # Skip if it looks like code
                    if (re.search(r'\bdef\s', sentence) or
                        re.search(r'\bclass\s', sentence) or
                        re.search(r'\bimport\s', sentence) or
                        re.search(r'\s*=\s*', sentence) or  # assignment
                        re.search(r'\([^)]*=[^)]*\)', sentence) or  # function with assignment
                        sentence.strip().endswith(':') or  # Python block start
                        sentence.strip().startswith('#') or  # comment
                        sentence.strip().startswith('//')):  # JS comment
                        continue

                    # Only keep sentences that look like natural language
                    if len(sentence) > 10 and sentence.count(' ') > 2:  # At least 3 words
                        conceptual_parts.append(sentence + '.')

        return ' '.join(conceptual_parts)

    def _remove_code_elements_from_response(self, response: str) -> str:
        """
        Remove code elements from an existing response while preserving natural language
        """
        import re

        # Remove code assignment patterns
        response = re.sub(r'\b\w+\s*=\s*["\'][^"\']*["\']', '', response)
        response = re.sub(r'\b\w+\s*=\s*\d+', '', response)
        response = re.sub(r'\b\w+\s*=\s*\[.*?\]', '', response)
        response = re.sub(r'\b\w+\s*=\s*{.*?}', '', response)

        # Remove function calls
        response = re.sub(r'\b\w+\s*\([^)]*\)', '', response)

        # Remove type annotations and declarations
        response = re.sub(r'\s*:\s*\w+', '', response)  # Type annotations
        response = re.sub(r'\b(?:int|str|float|bool|list|dict|var|let|const|function|async|await)\s+', '', response)

        # Remove code-specific punctuation patterns
        response = re.sub(r'\s*->\s*', ' ', response)  # Arrow functions
        response = re.sub(r'\s*=>\s*', ' ', response)  # Fat arrow
        response = re.sub(r'\s*==\s*', ' equals ', response)
        response = re.sub(r'\s*!=\s*', ' not equals ', response)

        # Clean up excessive whitespace
        response = re.sub(r'\s+', ' ', response)
        response = re.sub(r'\.+\.', '.', response)  # Multiple dots
        response = response.strip()

        return response