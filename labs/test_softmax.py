import cocotb
from cocotb.triggers import Timer
import numpy as np

def golden_softmax_approx(in_vec):
    max_v = max(in_vec)
    deltas = [v - max_v for v in in_vec]
    lut = {
        0: 255, 1: 155, 2: 94, 3: 57, 4: 35,
        5: 21, 6: 13, 7: 8, 8: 5, 9: 3, 10: 2, 11: 1
    }
    exp_vals = [lut.get(-d, 0) for d in deltas]
    sum_e = sum(exp_vals)
    probs = [(e * 255) // sum_e for e in exp_vals]
    return probs

@cocotb.test()
async def test_softmax_equal_inputs(dut):
    """When all inputs are equal, all probabilities must be equal (~63/255 each for 4 elements)"""
    for val in [-50, 0, 10, 100]:
        for i in range(4):
            dut.in_vec[i].value = val
        await Timer(1, unit="ns")
        
        probs = [int(dut.out_prob[i].value) for i in range(4)]
        # 255 / 4 = 63.75 -> each should be 63
        for p in probs:
            assert abs(p - 63) <= 1, f"Expected equal probabilities ~63, got {probs}"
        assert sum(probs) >= 250, f"Sum of probabilities should be close to 255, got {sum(probs)}"

@cocotb.test()
async def test_softmax_dominant_winner(dut):
    """When one input is much larger, its probability should dominate (~255)"""
    dut.in_vec[0].value = 50
    dut.in_vec[1].value = 0
    dut.in_vec[2].value = 0
    dut.in_vec[3].value = 0
    await Timer(1, unit="ns")
    
    probs = [int(dut.out_prob[i].value) for i in range(4)]
    assert probs[0] == 255, f"Dominant element should have max prob 255, got {probs[0]}"
    assert probs[1] == 0 and probs[2] == 0 and probs[3] == 0

@cocotb.test()
async def test_softmax_various_vectors(dut):
    """Test various input vectors and compare against golden fixed-point reference"""
    test_vectors = [
        [10, 8, 6, 4],
        [0, -2, -4, -6],
        [100, 99, 98, 97],
        [-10, -11, -12, -15],
        [5, 5, 0, 0],
    ]
    
    for vec in test_vectors:
        for i in range(4):
            dut.in_vec[i].value = vec[i]
        await Timer(1, unit="ns")
        
        expected_probs = golden_softmax_approx(vec)
        actual_probs = [int(dut.out_prob[i].value) for i in range(4)]
        
        for i in range(4):
            assert actual_probs[i] == expected_probs[i], (
                f"Mismatch for vector {vec} at index {i}: got {actual_probs[i]}, expected {expected_probs[i]}"
            )
        # Sum should approximate total probability 255 (allowing small truncation differences)
        assert 245 <= sum(actual_probs) <= 255
