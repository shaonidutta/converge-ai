"""
Integration tests for guardrails system.

This module tests the complete guardrails flow including:
- Input guardrails (validation, PII detection, toxic content, rate limiting)
- Output guardrails (PII leakage, toxic content)
- GuardrailManager orchestration
- Integration with ChatService
"""

import pytest
import asyncio
from src.guardrails.core.guardrail_factory import create_guardrail_manager
from src.guardrails.core.guardrail_result import Action


@pytest.mark.asyncio
async def test_input_validation_pass():
    """Test that valid input passes all guardrails"""
    manager = create_guardrail_manager()
    
    text = "I need help with plumbing services"
    report = await manager.check_input(text, user_id=1, context={})
    
    assert not report.is_blocked
    assert report.final_action == Action.ALLOW
    print(f"✓ Input validation passed (latency: {report.total_latency_ms:.2f}ms)")


@pytest.mark.asyncio
async def test_input_validation_too_long():
    """Test that too-long input is blocked"""
    manager = create_guardrail_manager()
    
    text = "x" * 15000  # Exceeds max_length of 10000
    report = await manager.check_input(text, user_id=1, context={})
    
    assert report.is_blocked
    assert report.final_action == Action.BLOCK
    print(f"✓ Too-long input blocked (latency: {report.total_latency_ms:.2f}ms)")


@pytest.mark.asyncio
async def test_pii_detection_and_masking():
    """Test that PII is detected and masked"""
    manager = create_guardrail_manager()
    
    text = "My email is john@example.com and phone is 123-456-7890"
    report = await manager.check_input(text, user_id=1, context={})
    
    assert not report.is_blocked  # Should sanitize, not block
    assert report.final_action == Action.SANITIZE
    assert report.final_text is not None
    assert "john@example.com" not in report.final_text
    assert "123-456-7890" not in report.final_text
    print(f"✓ PII detected and masked (latency: {report.total_latency_ms:.2f}ms)")
    print(f"  Original: {text}")
    print(f"  Sanitized: {report.final_text}")


@pytest.mark.asyncio
async def test_toxic_content_detection():
    """Test that toxic content is blocked"""
    manager = create_guardrail_manager()
    
    text = "This is fucking terrible service"
    report = await manager.check_input(text, user_id=1, context={})
    
    assert report.is_blocked
    assert report.final_action == Action.BLOCK
    print(f"✓ Toxic content blocked (latency: {report.total_latency_ms:.2f}ms)")


@pytest.mark.asyncio
async def test_rate_limiting():
    """Test that rate limiting works"""
    manager = create_guardrail_manager()
    
    # Send 25 requests (exceeds limit of 20 per minute)
    blocked_count = 0
    for i in range(25):
        text = f"Request {i}"
        report = await manager.check_input(text, user_id=999, context={})
        if report.is_blocked:
            blocked_count += 1
    
    assert blocked_count > 0  # At least some requests should be blocked
    print(f"✓ Rate limiting working (blocked {blocked_count}/25 requests)")


@pytest.mark.asyncio
async def test_output_pii_leakage():
    """Test that PII leakage in output is detected"""
    manager = create_guardrail_manager()
    
    text = "Your booking is confirmed. Contact us at support@converge.com or 555-1234"
    report = await manager.check_output(text, user_id=1, context={})
    
    assert not report.is_blocked  # Should sanitize, not block
    assert report.final_action == Action.SANITIZE
    assert report.final_text is not None
    print(f"✓ Output PII leakage detected and masked (latency: {report.total_latency_ms:.2f}ms)")
    print(f"  Original: {text}")
    print(f"  Sanitized: {report.final_text}")


@pytest.mark.asyncio
async def test_output_toxic_content():
    """Test that toxic content in output is blocked"""
    manager = create_guardrail_manager()
    
    text = "I hate this damn service"
    report = await manager.check_output(text, user_id=1, context={})
    
    assert report.is_blocked
    assert report.final_action == Action.BLOCK
    print(f"✓ Toxic output blocked (latency: {report.total_latency_ms:.2f}ms)")


@pytest.mark.asyncio
async def test_parallel_execution_performance():
    """Test that guardrails run in parallel for better performance"""
    manager = create_guardrail_manager()
    
    text = "I need plumbing help at my address 123 Main St"
    report = await manager.check_input(text, user_id=1, context={})
    
    # Total latency should be less than sum of individual latencies
    # (because they run in parallel)
    individual_latencies = [r.latency_ms for r in report.results]
    sum_latencies = sum(individual_latencies)
    
    print(f"✓ Parallel execution test:")
    print(f"  Individual latencies: {individual_latencies}")
    print(f"  Sum of latencies: {sum_latencies:.2f}ms")
    print(f"  Actual total (parallel): {report.total_latency_ms:.2f}ms")
    if report.total_latency_ms > 0:
        print(f"  Speedup: {sum_latencies / report.total_latency_ms:.2f}x")
    else:
        print(f"  Speedup: N/A (latency too small to measure)")

    # Parallel execution should be faster than sequential (or equal if very fast)
    assert report.total_latency_ms <= sum_latencies


@pytest.mark.asyncio
async def test_complete_flow():
    """Test complete flow with multiple guardrails"""
    manager = create_guardrail_manager()
    
    # Test 1: Clean input and output
    input_text = "I need AC repair service"
    output_text = "Sure! I can help you book an AC repair service."
    
    input_report = await manager.check_input(input_text, user_id=1, context={})
    output_report = await manager.check_output(output_text, user_id=1, context={})
    
    assert not input_report.is_blocked
    assert not output_report.is_blocked
    print(f"✓ Clean flow passed")
    print(f"  Input latency: {input_report.total_latency_ms:.2f}ms")
    print(f"  Output latency: {output_report.total_latency_ms:.2f}ms")
    print(f"  Total overhead: {input_report.total_latency_ms + output_report.total_latency_ms:.2f}ms")


if __name__ == "__main__":
    print("Running guardrails integration tests...\n")
    
    asyncio.run(test_input_validation_pass())
    asyncio.run(test_input_validation_too_long())
    asyncio.run(test_pii_detection_and_masking())
    asyncio.run(test_toxic_content_detection())
    asyncio.run(test_rate_limiting())
    asyncio.run(test_output_pii_leakage())
    asyncio.run(test_output_toxic_content())
    asyncio.run(test_parallel_execution_performance())
    asyncio.run(test_complete_flow())
    
    print("\n✅ All tests passed!")

