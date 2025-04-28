#!/usr/bin/env python3
"""
Simplified test script for side-channel vulnerability in cryptographic operations.
"""

import time
import random
import hashlib

def non_constant_time_operation(input_value):
    """
    A deliberately non-constant time operation to demonstrate side-channel vulnerability.
    The execution time depends on the number of bits in the input value.
    """
    start_time = time.time()
    
    # Simulate a non-constant time operation
    # The more bits set to 1 in the input, the longer it takes
    count = 0
    for i in range(32):
        if (input_value >> i) & 1:
            # Simulate more work for each bit set to 1
            time.sleep(0.001)
            count += 1
    
    end_time = time.time()
    return count, end_time - start_time

def collect_timing_data(num_samples=100):
    """Collect timing data for the non-constant time operation."""
    timing_data = {}
    
    for i in range(num_samples):
        # Generate a random input
        input_value = random.randint(0, 0xFFFFFFFF)
        
        # Perform the operation and measure the time
        bit_count, time_taken = non_constant_time_operation(input_value)
        
        # Store the timing data
        timing_data[input_value] = (bit_count, time_taken)
        
        # Print progress
        if (i + 1) % 10 == 0:
            print(f"Collected {i + 1}/{num_samples} samples")
    
    return timing_data

def analyze_timing_data(timing_data):
    """Analyze the timing data to detect side-channel vulnerabilities."""
    # Group timing data by bit count
    grouped_data = {}
    
    for input_value, (bit_count, time_taken) in timing_data.items():
        if bit_count not in grouped_data:
            grouped_data[bit_count] = []
        grouped_data[bit_count].append(time_taken)
    
    # Calculate average time for each bit count
    avg_times = {}
    for bit_count, times in grouped_data.items():
        avg_times[bit_count] = sum(times) / len(times)
    
    # Print results
    print("\nTiming Analysis:")
    print(f"Number of samples: {len(timing_data)}")
    
    print("\nAverage time by bit count:")
    for bit_count in sorted(avg_times.keys()):
        print(f"Bit count {bit_count}: {avg_times[bit_count]:.6f} seconds")
    
    # Check for correlation between bit count and timing
    bit_counts = list(avg_times.keys())
    times = [avg_times[bc] for bc in bit_counts]
    
    if len(bit_counts) > 1:
        # Simple check: does time increase with bit count?
        is_increasing = all(times[i] <= times[i+1] for i in range(len(times)-1))
        
        if is_increasing:
            print("\nVULNERABILITY DETECTED: Execution time increases with bit count!")
            print("This indicates a side-channel vulnerability that leaks information about the input value.")
        else:
            print("\nNo clear correlation between bit count and execution time.")
    else:
        print("\nNot enough data to analyze correlation.")

def main():
    print("Testing for side-channel vulnerability...")
    print("Collecting timing data for 50 samples...")
    
    timing_data = collect_timing_data(50)
    analyze_timing_data(timing_data)
    
    return 0

if __name__ == "__main__":
    main()
