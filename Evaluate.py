import asyncio
import os
import sys
import time
from typing import Any, Dict, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MCP_SERVER_PYTHON = sys.executable
MCP_SERVER_SCRIPT = os.path.abspath("server.py")

TEST_CASES: List[Dict[str, Any]] = [
    # --- Semantic Accuracy Tests ---
    {
        "id": "TC-01",
        "description": "Authentication & OAuth2 Scopes",
        "query": "authentication oauth2 scopes",
        "top_k": 3,
        "expected_type": "success",
        "expected_keywords": ["auth", "token", "scope", "security"],
    },
    {
        "id": "TC-02",
        "description": "Background Tasks with Database Session",
        "query": "background tasks database session yield",
        "top_k": 3,
        "expected_type": "success",
        "expected_keywords": ["background", "task", "yield", "dependenc"],
    },
    {
        "id": "TC-03",
        "description": "OpenAPI Component Schemas & Responses",
        "query": "OpenAPI component schemas and response references",
        "top_k": 4,
        "expected_type": "success",
        "expected_keywords": ["response", "schema", "openapi", "status"],
    },
    {
        "id": "TC-04",
        "description": "Query Parameters & Path Validation",
        "query": "query parameter type validation q",
        "top_k": 3,
        "expected_type": "success",
        "expected_keywords": ["query", "parameter", "dependenc"],
    },
    {
        "id": "TC-05",
        "description": "Dependency Injection with Yield",
        "query": "dependency injection yield exception handling",
        "top_k": 3,
        "expected_type": "success",
        "expected_keywords": ["yield", "exception", "dependenc"],
    },
    {
        "id": "TC-06",
        "description": "HTTP Status Codes Modification",
        "query": "response change status code JSONResponse",
        "top_k": 3,
        "expected_type": "success",
        "expected_keywords": ["status", "response", "code"],
    },
    {
        "id": "TC-07",
        "description": "CORS & Middleware Setup",
        "query": "middleware CORS origins allow methods",
        "top_k": 3,
        "expected_type": "success",
        "expected_keywords": ["middleware", "cors", "response"],
    },
    # --- Boundary & Validation Handling ---
    {
        "id": "TC-08",
        "description": "Boundary: Empty String Query",
        "query": "",
        "top_k": 3,
        "expected_type": "error",
        "expected_keywords": ["cannot be blank"],
    },
    {
        "id": "TC-09",
        "description": "Boundary: Whitespace-Only Query",
        "query": "     ",
        "top_k": 3,
        "expected_type": "error",
        "expected_keywords": ["cannot be blank"],
    },
    {
        "id": "TC-10",
        "description": "Boundary: Out-of-Bounds top_k (top_k > 20)",
        "query": "FastAPI routers",
        "top_k": 25,
        "expected_type": "error",
        "expected_keywords": ["top_k must be between 1 and 20"],
    },
]


async def run_eval() -> None:
    server_params = StdioServerParameters(
        command=MCP_SERVER_PYTHON,
        args=[MCP_SERVER_SCRIPT],
        env=dict(os.environ),
    )

    print("=" * 80)
    print("  MCP SERVER AUTOMATED EVALUATION SUITE (`docs-retriever-mcp`)")
    print(f"  Target Script: {MCP_SERVER_SCRIPT}")
    print(f"  Interpreter:   {MCP_SERVER_PYTHON}")
    print("=" * 80)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("[INFO] MCP Session Initialized over stdio successfully.\n")

            results = []

            for tc in TEST_CASES:
                start_time = time.perf_counter()
                tool_result = await session.call_tool(
                    name="search_docs",
                    arguments={"query": tc["query"], "top_k": tc["top_k"]},
                )
                latency_ms = (time.perf_counter() - start_time) * 1000

                raw_output = tool_result.content[0].text if tool_result.content else ""
                output_lower = raw_output.lower()

                # Evaluation assertions
                passed = False
                reason = ""

                if tc["expected_type"] == "error":
                    if any(kw.lower() in output_lower for kw in tc["expected_keywords"]):
                        passed = True
                    else:
                        reason = f"Expected error warning not returned. Output: {raw_output[:120]}"
                else:
                    if raw_output.startswith("Error"):
                        reason = f"Unexpected tool execution error: {raw_output[:120]}"
                    else:
                        matched = [
                            kw for kw in tc["expected_keywords"] if kw.lower() in output_lower
                        ]
                        if len(matched) >= 1:
                            passed = True
                        else:
                            reason = f"Keywords {tc['expected_keywords']} absent from response."

                results.append(
                    {
                        "id": tc["id"],
                        "description": tc["description"],
                        "top_k": tc["top_k"],
                        "passed": passed,
                        "latency_ms": latency_ms,
                        "reason": reason,
                    }
                )

                status_icon = "✅ PASS" if passed else "❌ FAIL"
                print(
                    f"[{tc['id']}] {status_icon} | Latency: {latency_ms:6.1f}ms | {tc['description']}"
                )
                if not passed:
                    print(f"       └── Failure Reason: {reason}")

            # Summary metrics
            total = len(results)
            passed_count = sum(1 for r in results if r["passed"])
            avg_latency = sum(r["latency_ms"] for r in results) / total
            max_latency = max(r["latency_ms"] for r in results)
            min_latency = min(r["latency_ms"] for r in results)

            print("\n" + "=" * 80)
            print("  EVALUATION SUMMARY")
            print("=" * 80)
            print(f"  Tests Passed:       {passed_count}/{total} ({(passed_count/total)*100:.1f}%)")
            print(f"  Average Latency:    {avg_latency:.1f} ms")
            print(f"  Min / Max Latency:  {min_latency:.1f} ms / {max_latency:.1f} ms")
            print("=" * 80)

            if passed_count != total:
                sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_eval())