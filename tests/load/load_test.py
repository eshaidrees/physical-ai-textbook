import asyncio
import aiohttp
import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import defaultdict
import statistics


@dataclass
class LoadTestResult:
    """
    Data class to store load test results
    """
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    errors_by_type: Dict[str, int]
    status_codes: Dict[int, int]


class LoadTester:
    """
    Load testing framework for the RAG Chatbot API
    """
    def __init__(self, base_url: str = "http://localhost:8000", concurrency: int = 10):
        self.base_url = base_url
        self.concurrency = concurrency
        self.session = None
        self.results_lock = threading.Lock()
        self.response_times = []
        self.status_codes = defaultdict(int)
        self.errors = defaultdict(int)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def make_request(self, endpoint: str, method: str = "POST", payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a single API request
        """
        start_time = time.time()

        try:
            url = f"{self.base_url}{endpoint}"
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    result = await response.json()
            else:
                async with self.session.post(url, json=payload) as response:
                    result = await response.json()

            response_time = time.time() - start_time

            with self.results_lock:
                self.response_times.append(response_time)
                self.status_codes[response.status] += 1

            return {
                "status": response.status,
                "response_time": response_time,
                "success": 200 <= response.status < 300,
                "data": result
            }

        except Exception as e:
            response_time = time.time() - start_time

            with self.results_lock:
                self.response_times.append(response_time)
                self.errors[type(e).__name__] += 1

            return {
                "status": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }

    async def run_single_test(self, endpoint: str, method: str = "POST", payload: Dict[str, Any] = None):
        """
        Run a single test request
        """
        return await self.make_request(endpoint, method, payload)

    async def run_concurrent_tests(self, endpoint: str, method: str = "POST",
                                  payload: Dict[str, Any] = None, num_requests: int = 100):
        """
        Run multiple concurrent test requests
        """
        tasks = []
        for _ in range(num_requests):
            task = asyncio.create_task(self.make_request(endpoint, method, payload))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    def calculate_statistics(self) -> LoadTestResult:
        """
        Calculate load test statistics
        """
        if not self.response_times:
            return LoadTestResult(
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                requests_per_second=0,
                errors_by_type=dict(self.errors),
                status_codes=dict(self.status_codes)
            )

        sorted_times = sorted(self.response_times)
        total_requests = len(self.response_times)
        successful_requests = sum(1 for code, count in self.status_codes.items() if 200 <= code < 300 for _ in range(count))
        failed_requests = total_requests - successful_requests

        return LoadTestResult(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=statistics.mean(self.response_times),
            min_response_time=min(self.response_times),
            max_response_time=max(self.response_times),
            p95_response_time=sorted_times[int(0.95 * len(sorted_times))] if sorted_times else 0,
            p99_response_time=sorted_times[int(0.99 * len(sorted_times))] if sorted_times else 0,
            requests_per_second=total_requests / sum(self.response_times) if sum(self.response_times) > 0 else 0,
            errors_by_type=dict(self.errors),
            status_codes=dict(self.status_codes)
        )

    def reset_results(self):
        """
        Reset collected results for a new test
        """
        with self.results_lock:
            self.response_times.clear()
            self.status_codes.clear()
            self.errors.clear()


async def run_chat_endpoint_load_test(num_requests: int = 100, concurrency: int = 10):
    """
    Run load test specifically for the chat endpoint
    """
    print(f"Running load test on chat endpoint with {num_requests} requests and {concurrency} concurrency...")

    async with LoadTester(concurrency=concurrency) as tester:
        # Prepare a typical chat request
        payload = {
            "message": "What is artificial intelligence?",
            "conversation_id": "load_test_conversation"
        }

        start_time = time.time()
        results = await tester.run_concurrent_tests(
            "/api/v1/chat",
            method="POST",
            payload=payload,
            num_requests=num_requests
        )
        end_time = time.time()

        total_time = end_time - start_time
        stats = tester.calculate_statistics()

        print(f"\nLoad Test Results for Chat Endpoint:")
        print(f"Total Requests: {stats.total_requests}")
        print(f"Successful Requests: {stats.successful_requests}")
        print(f"Failed Requests: {stats.failed_requests}")
        print(f"Success Rate: {(stats.successful_requests / stats.total_requests * 100):.2f}%")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Requests Per Second: {stats.requests_per_second:.2f}")
        print(f"Average Response Time: {stats.avg_response_time:.4f}s")
        print(f"Min Response Time: {stats.min_response_time:.4f}s")
        print(f"Max Response Time: {stats.max_response_time:.4f}s")
        print(f"95th Percentile Response Time: {stats.p95_response_time:.4f}s")
        print(f"99th Percentile Response Time: {stats.p99_response_time:.4f}s")

        if stats.status_codes:
            print(f"Status Codes: {stats.status_codes}")
        if stats.errors_by_type:
            print(f"Errors: {stats.errors_by_type}")

        return stats


async def run_search_endpoint_load_test(num_requests: int = 100, concurrency: int = 10):
    """
    Run load test specifically for the search endpoint
    """
    print(f"\nRunning load test on search endpoint with {num_requests} requests and {concurrency} concurrency...")

    async with LoadTester(concurrency=concurrency) as tester:
        # Prepare a typical search request
        payload = {
            "query": "neural networks",
            "k": 4
        }

        start_time = time.time()
        results = await tester.run_concurrent_tests(
            "/api/v1/search",
            method="POST",
            payload=payload,
            num_requests=num_requests
        )
        end_time = time.time()

        total_time = end_time - start_time
        stats = tester.calculate_statistics()

        print(f"\nLoad Test Results for Search Endpoint:")
        print(f"Total Requests: {stats.total_requests}")
        print(f"Successful Requests: {stats.successful_requests}")
        print(f"Failed Requests: {stats.failed_requests}")
        print(f"Success Rate: {(stats.successful_requests / stats.total_requests * 100):.2f}%")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Requests Per Second: {stats.requests_per_second:.2f}")
        print(f"Average Response Time: {stats.avg_response_time:.4f}s")
        print(f"Min Response Time: {stats.min_response_time:.4f}s")
        print(f"Max Response Time: {stats.max_response_time:.4f}s")
        print(f"95th Percentile Response Time: {stats.p95_response_time:.4f}s")
        print(f"99th Percentile Response Time: {stats.p99_response_time:.4f}s")

        if stats.status_codes:
            print(f"Status Codes: {stats.status_codes}")
        if stats.errors_by_type:
            print(f"Errors: {stats.errors_by_type}")

        return stats


async def run_health_endpoint_load_test(num_requests: int = 100, concurrency: int = 10):
    """
    Run load test specifically for the health endpoint
    """
    print(f"\nRunning load test on health endpoint with {num_requests} requests and {concurrency} concurrency...")

    async with LoadTester(concurrency=concurrency) as tester:
        start_time = time.time()
        results = await tester.run_concurrent_tests(
            "/api/v1/health",
            method="GET",
            num_requests=num_requests
        )
        end_time = time.time()

        total_time = end_time - start_time
        stats = tester.calculate_statistics()

        print(f"\nLoad Test Results for Health Endpoint:")
        print(f"Total Requests: {stats.total_requests}")
        print(f"Successful Requests: {stats.successful_requests}")
        print(f"Failed Requests: {stats.failed_requests}")
        print(f"Success Rate: {(stats.successful_requests / stats.total_requests * 100):.2f}%")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Requests Per Second: {stats.requests_per_second:.2f}")
        print(f"Average Response Time: {stats.avg_response_time:.4f}s")
        print(f"Min Response Time: {stats.min_response_time:.4f}s")
        print(f"Max Response Time: {stats.max_response_time:.4f}s")
        print(f"95th Percentile Response Time: {stats.p95_response_time:.4f}s")
        print(f"99th Percentile Response Time: {stats.p99_response_time:.4f}s")

        if stats.status_codes:
            print(f"Status Codes: {stats.status_codes}")
        if stats.errors_by_type:
            print(f"Errors: {stats.errors_by_type}")

        return stats


async def run_comprehensive_load_test():
    """
    Run comprehensive load tests on all major endpoints
    """
    print("Starting comprehensive load test for RAG Chatbot API...")
    print("=" * 60)

    # Test with 100 requests at 10 concurrent connections (simulating 100 users scenario)
    await run_health_endpoint_load_test(num_requests=100, concurrency=10)
    await run_search_endpoint_load_test(num_requests=100, concurrency=10)
    await run_chat_endpoint_load_test(num_requests=100, concurrency=10)

    print("\n" + "=" * 60)
    print("Comprehensive load test completed.")


def run_stress_test():
    """
    Run a stress test with increasing load to find breaking points
    """
    print("Starting stress test...")

    # Test different load levels
    load_levels = [50, 100, 200, 500]
    concurrency_levels = [10, 20, 50]

    results = []

    for concurrency in concurrency_levels:
        for num_requests in load_levels:
            print(f"\nTesting with {num_requests} requests at {concurrency} concurrency...")

            # Create a new event loop for each test to avoid issues
            import threading
            loop = asyncio.new_event_loop()
            threading.Thread(target=lambda: loop.run_until_complete(
                run_single_stress_test(num_requests, concurrency)
            )).start()
            loop.close()


async def run_single_stress_test(num_requests: int, concurrency: int):
    """
    Run a single stress test scenario
    """
    async with LoadTester(concurrency=concurrency) as tester:
        payload = {
            "message": "What is artificial intelligence?",
            "conversation_id": f"stress_test_{num_requests}_{concurrency}"
        }

        start_time = time.time()
        results = await tester.run_concurrent_tests(
            "/api/v1/chat",
            method="POST",
            payload=payload,
            num_requests=num_requests
        )
        end_time = time.time()

        total_time = end_time - start_time
        stats = tester.calculate_statistics()

        print(f"  Requests: {num_requests}, Concurrency: {concurrency}")
        print(f"  Success Rate: {(stats.successful_requests / stats.total_requests * 100):.2f}%")
        print(f"  Avg Response Time: {stats.avg_response_time:.4f}s")
        print(f"  RPS: {stats.requests_per_second:.2f}")

        return stats


if __name__ == "__main__":
    print("RAG Chatbot API Load Testing Framework")
    print("This framework tests the API's ability to handle multiple concurrent users.")

    # Run the comprehensive load test
    asyncio.run(run_comprehensive_load_test())