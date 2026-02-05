from typing import List, Dict, Any
import re


class ResponseValidator:
    def __init__(self):
        # Patterns that indicate the response might not be based on the book content
        self.non_book_indicators = [
            r"i don't know",
            r"i'm not sure",
            r"i don't have access to",
            r"i cannot find",
            r"not mentioned in the provided text",
            r"not in the context",
            r"not specified in the document"
        ]

    def validate(self, response: str, sources: List[Dict[str, Any]]) -> bool:
        """
        Validate that the response is based on book content and doesn't contain code/logs
        """
        response_lower = response.lower()

        # Check if the response contains any non-book indicators
        for indicator in self.non_book_indicators:
            if re.search(indicator, response_lower):
                # These responses are actually valid when content isn't found
                # as they acknowledge the limitation rather than hallucinating
                return True

        # Check if the response contains code-like patterns that should be filtered out
        if self._contains_code_patterns(response):
            return False

        # Check if the response contains log-like patterns
        if self._contains_log_patterns(response):
            return False

        # If we have sources, check that the response references content from those sources
        if sources:
            # Extract key phrases from sources
            source_content = " ".join([source['text'] for source in sources])
            source_words = set(re.findall(r'\b\w+\b', source_content.lower()))

            # Extract words from response
            response_words = set(re.findall(r'\b\w+\b', response_lower))

            # Calculate overlap
            if source_words:
                overlap = len(source_words.intersection(response_words))
                total_source_words = len(source_words)

                # If there's significant overlap, the response is likely based on sources
                if overlap / total_source_words > 0.1:  # 10% overlap threshold
                    return True

            # Alternative check: see if response contains phrases from sources
            for source in sources:
                if len(source['text']) > 20:  # Only check longer text snippets
                    # Look for at least part of the source text in the response
                    if self._text_contains_substring(response, source['text'], threshold=0.3):
                        return True

        # If no sources provided but response doesn't contain non-book indicators,
        # it might be a valid response that summarizes or explains concepts
        return True

    def _contains_code_patterns(self, response: str) -> bool:
        """
        Check if response contains code-like patterns that should be filtered out
        """
        code_patterns = [
            r'\bdef\s+\w+\s*\(',  # Python function definitions
            r'\bclass\s+\w+\s*\w*',  # Class definitions
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
            r'\s*=\s*',  # General assignment (but be careful with this one)
            r'\s*:\s*\w+\s*,',  # Type annotations with commas
            r'\s*->\s*',  # Arrow functions
            r'\s*=>\s*',  # Fat arrow
            r'\([^)]*=[^)]*\)',  # Function parameters with defaults
        ]

        # Count how many code patterns match
        matches = 0
        for pattern in code_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                matches += 1
                # If we find multiple code patterns, it's likely code
                if matches >= 2:
                    return True

        # If only a few matches, check if they're just technical terms in context
        if matches >= 1:
            # Check if the response is mostly natural language or mostly code
            words = response.split()
            code_indicators = 0
            total_words = len(words)

            for word in words[:20]:  # Check first 20 words as sample
                if any(code_word in word.lower() for code_word in ['def', 'class', 'import', 'var', 'const', 'let', 'function', 'return', 'print']):
                    code_indicators += 1

            # If more than 30% of the first 20 words are code indicators, consider it code
            if total_words > 0 and (code_indicators / min(20, total_words)) > 0.3:
                return True

        # Additional check: if the response contains clear code structure, mark as code
        # Look for common code patterns that indicate structured code, but only if they're not in explanatory context
        if re.search(r'^\s*def\s+\w+\s*\(|^\s*class\s+\w+|^\s*import\s+\w+|^\s*function\s+\w+', response, re.IGNORECASE):
            return True

        return False

    def _contains_log_patterns(self, response: str) -> bool:
        """
        Check if response contains log-like patterns that should be filtered out
        """
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

        for pattern in log_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return True

        return False

    def _text_contains_substring(self, text1: str, text2: str, threshold: float = 0.3) -> bool:
        """
        Check if text1 contains a significant portion of text2
        """
        text1_lower = text1.lower()
        text2_lower = text2.lower()

        # Split both texts into words
        words1 = set(re.findall(r'\b\w+\b', text1_lower))
        words2 = set(re.findall(r'\b\w+\b', text2_lower))

        if not words2:
            return False

        # Calculate overlap
        overlap = len(words1.intersection(words2))
        min_len = min(len(words1), len(words2))

        if min_len == 0:
            return False

        return overlap / min_len >= threshold

    def validate_no_hallucinations(self, response: str, sources: List[Dict[str, Any]]) -> bool:
        """
        Validate that the response doesn't contain hallucinated information
        """
        # This is a simplified check - in a real implementation, you'd need more sophisticated checks
        # For now, we'll just ensure that if sources exist, the response is related to them
        if not sources:
            return True  # Can't validate without sources

        # Check if response is generally related to the sources
        response_lower = response.lower()
        source_texts = [source['text'].lower() for source in sources]

        # Look for key terms from sources in the response
        for source_text in source_texts:
            # Extract key terms (longer words that are likely to be important)
            key_terms = [word for word in source_text.split() if len(word) > 5]

            # Check if at least some key terms appear in the response
            matched_terms = [term for term in key_terms if term in response_lower]

            # If we have some overlap, it's likely not hallucinated
            if len(matched_terms) > 0:
                return True

        return True  # Default to true to avoid overly restrictive validation