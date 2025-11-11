#!/usr/bin/env python3
"""
ChatOllama Performance Benchmark Script

Tests response time and token generation speed for the configured model
using LangChain's ChatOllama interface.
"""

import time
from typing import Dict
from agents.llm_model import LLM

# Test questions
WARMUP_PROMPT = "Hello, how are you today?"

Q3_PROMPT = """List 5 advantages and 5 disadvantages of using microservices architecture. 
Format each as a brief point."""

Q4_PROMPT = """Write a Python function that takes a list of dictionaries representing database records 
and returns the top 3 records with the highest 'score' field. Include error handling for 
missing keys and empty lists. Add docstring and type hints."""

TEST_QUESTIONS = {
    "warmup": WARMUP_PROMPT,
    "q3": Q3_PROMPT,
    "q4": Q4_PROMPT,
}


def test_model(prompt: str) -> Dict:
    """
    Test the configured model with a prompt and return performance metrics.
    
    Args:
        prompt: The prompt to send to the model
        
    Returns:
        Dict with metrics: time, tokens, response, etc.
    """
    start_time = time.time()
    response = LLM.invoke(prompt)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    content = response.content
    token_count = len(content.split())  # Approximate token count
    tokens_per_sec = token_count / elapsed_time if elapsed_time > 0 else 0
    
    return {
        "time": elapsed_time,
        "tokens": token_count,
        "tokens_per_sec": tokens_per_sec,
        "response": content,
    }


def run_benchmark():
    """Run the complete benchmark for the configured model."""
    print("=" * 60)
    print("ChatOllama Performance Benchmark")
    print(f"Testing Model: {LLM.model}")
    print("=" * 60)
    print()
    
    results = {}
    
    # Warmup
    print("  [WARMUP] Loading model...")
    try:
        warmup_result = test_model(TEST_QUESTIONS["warmup"])
        print(f"    Time: {warmup_result['time']:.2f}s | "
              f"Tokens: {warmup_result['tokens']} | "
              f"Speed: {warmup_result['tokens_per_sec']:.1f} tok/s")
        results["warmup"] = warmup_result
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return
    
    print()
    
    # Q3: Structured List (3 runs)
    print("  [Q3: Structured List]")
    q3_results = []
    for i in range(1, 4):
        try:
            result = test_model(TEST_QUESTIONS["q3"])
            print(f"    Run {i}: {result['tokens']} tokens | "
                  f"{result['time']:.2f}s | "
                  f"{result['tokens_per_sec']:.1f} tok/s")
            q3_results.append(result)
        except Exception as e:
            print(f"    Run {i}: ❌ Error: {e}")
    
    results["q3"] = q3_results
    print()
    
    # Q4: Python Code (3 runs)
    print("  [Q4: Python Code Generation]")
    q4_results = []
    for i in range(1, 4):
        try:
            result = test_model(TEST_QUESTIONS["q4"])
            print(f"    Run {i}: {result['tokens']} tokens | "
                  f"{result['time']:.2f}s | "
                  f"{result['tokens_per_sec']:.1f} tok/s")
            q4_results.append(result)
        except Exception as e:
            print(f"    Run {i}: ❌ Error: {e}")
    
    results["q4"] = q4_results
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    
    # Calculate averages for Q3
    if results.get("q3") and len(results["q3"]) > 0:
        q3_avg_time = sum(r["time"] for r in results["q3"]) / len(results["q3"])
        q3_avg_tokens = sum(r["tokens"] for r in results["q3"]) / len(results["q3"])
        q3_avg_speed = sum(r["tokens_per_sec"] for r in results["q3"]) / len(results["q3"])
        
        print(f"Q3 Average: {q3_avg_time:.2f}s | "
              f"{q3_avg_tokens:.0f} tokens | "
              f"{q3_avg_speed:.1f} tok/s")
    
    # Calculate averages for Q4
    if results.get("q4") and len(results["q4"]) > 0:
        q4_avg_time = sum(r["time"] for r in results["q4"]) / len(results["q4"])
        q4_avg_tokens = sum(r["tokens"] for r in results["q4"]) / len(results["q4"])
        q4_avg_speed = sum(r["tokens_per_sec"] for r in results["q4"]) / len(results["q4"])
        
        print(f"Q4 Average: {q4_avg_time:.2f}s | "
              f"{q4_avg_tokens:.0f} tokens | "
              f"{q4_avg_speed:.1f} tok/s")
    
    # Overall average
    if results.get("q3") and results.get("q4") and len(results["q3"]) > 0 and len(results["q4"]) > 0:
        overall_avg_time = (q3_avg_time + q4_avg_time) / 2
        overall_avg_tokens = (q3_avg_tokens + q4_avg_tokens) / 2
        overall_avg_speed = (q3_avg_speed + q4_avg_speed) / 2
        
        print(f"\nOverall Average: {overall_avg_time:.2f}s | "
              f"{overall_avg_tokens:.0f} tokens | "
              f"{overall_avg_speed:.1f} tok/s")
    
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_benchmark()
