"""
Automated Cloud Benchmark & High-Availability Validation Script
Smart Disaster Management & Aerial Drone Reconnaissance Platform
Course: Cloud Computing PBL (ECA4PE23A) | MIT World Peace University, Pune

This script performs empirical stress-testing against the API endpoint to benchmark:
1. Availability / Uptime Percentage: (Successful Requests / Total Requests) * 100
2. End-to-End Round-Trip Time (RTT): Min, Max, Mean, P95, and P99 latency
3. Exports an empirical audit dataset to 'benchmark_test_results.csv' & 'benchmark_summary.json'
"""

import urllib.request
import urllib.error
import time
import json
import csv
import os
import sys
from datetime import datetime

# Target API URL (Defaults to live AWS API Gateway endpoint)
API_URL = os.environ.get("API_URL", "https://np1yqzqgvd.execute-api.ap-southeast-2.amazonaws.com/prod/incidents")
TOTAL_REQUESTS = int(os.environ.get("BENCHMARK_N", 2000))
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(OUTPUT_DIR, "benchmark_test_results.csv")
JSON_FILE = os.path.join(OUTPUT_DIR, "benchmark_summary.json")

def run_benchmark():
    print("=" * 70)
    print("  SMART DISASTER CLOUD PLATFORM - EMPIRICAL BENCHMARK TEST SUITE")
    print("=" * 70)
    print(f"Target Endpoint : {API_URL}")
    print(f"Sample Size (N) : {TOTAL_REQUESTS} requests")
    print(f"Start Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)

    results = []
    latencies = []
    success_count = 0
    failure_count = 0

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Executing automated test transactions...")
    t0_suite = time.time()

    for i in range(1, TOTAL_REQUESTS + 1):
        req_id = f"REQ-{i:05d}"
        t_start = time.perf_counter()
        status_code = None
        error_msg = ""
        success = False

        try:
            req = urllib.request.Request(API_URL, headers={"User-Agent": "DisasterPBL-Benchmark/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                status_code = response.getcode()
                _ = response.read()
                success = (200 <= status_code < 300)
        except urllib.error.HTTPError as e:
            status_code = e.code
            error_msg = str(e.reason)
            success = False
        except Exception as e:
            status_code = 500
            error_msg = str(e)
            success = False

        t_end = time.perf_counter()
        latency_ms = round((t_end - t_start) * 1000.0, 2)
        latencies.append(latency_ms)

        if success:
            success_count += 1
        else:
            failure_count += 1

        results.append({
            "request_id": req_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "endpoint": API_URL,
            "method": "GET",
            "status_code": status_code,
            "latency_ms": latency_ms,
            "success": "TRUE" if success else "FALSE",
            "error": error_msg
        })

        if i % 250 == 0 or i == TOTAL_REQUESTS:
            pct = (i / TOTAL_REQUESTS) * 100
            print(f"  [{i:>4}/{TOTAL_REQUESTS}] ({pct:>5.1f}%) Completed | Current Latency: {latency_ms:>5.1f} ms | Successes: {success_count}")

    total_duration = time.time() - t0_suite

    # Calculate statistics
    latencies_sorted = sorted(latencies)
    min_lat = min(latencies)
    max_lat = max(latencies)
    avg_lat = round(sum(latencies) / len(latencies), 2)
    p50_lat = latencies_sorted[int(len(latencies) * 0.50)]
    p95_lat = latencies_sorted[int(len(latencies) * 0.95)]
    p99_lat = latencies_sorted[int(len(latencies) * 0.99)]
    uptime_pct = round((success_count / TOTAL_REQUESTS) * 100.0, 3)

    # Save to CSV
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["request_id", "timestamp", "endpoint", "method", "status_code", "latency_ms", "success", "error"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Save to JSON summary
    summary_data = {
        "project": "Smart Disaster Management & Aerial Drone Reconnaissance Platform",
        "institution": "MIT World Peace University, Pune",
        "course_code": "ECA4PE23A",
        "benchmark_date": datetime.utcnow().isoformat() + "Z",
        "target_endpoint": API_URL,
        "sample_size_n": TOTAL_REQUESTS,
        "total_duration_sec": round(total_duration, 2),
        "metrics": {
            "successful_requests": success_count,
            "failed_requests": failure_count,
            "observed_availability_pct": uptime_pct,
            "latency_ms": {
                "min": min_lat,
                "avg": avg_lat,
                "median_p50": p50_lat,
                "p95": p95_lat,
                "p99": p99_lat,
                "max": max_lat
            }
        }
    }

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print("=" * 70)
    print("                    BENCHMARK RESULTS SUMMARY                      ")
    print("=" * 70)
    print(f"  Total Requests Executed (N) : {TOTAL_REQUESTS}")
    print(f"  Successful Requests (200 OK): {success_count}")
    print(f"  Failed Requests             : {failure_count}")
    print(f"  Observed Uptime / Avail.    : {uptime_pct} %")
    print(f"  Average RTT Latency         : {avg_lat} ms")
    print(f"  50th Percentile (Median)    : {p50_lat} ms")
    print(f"  95th Percentile Latency     : {p95_lat} ms")
    print(f"  Min / Max Latency           : {min_lat} ms / {max_lat} ms")
    print(f"  Total Test Time             : {round(total_duration, 2)} s (~{round(TOTAL_REQUESTS / total_duration, 1)} req/sec)")
    print("-" * 70)
    print(f"  Audit CSV Log Written to    : {CSV_FILE}")
    print(f"  Executive JSON Summary to   : {JSON_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    run_benchmark()
