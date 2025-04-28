#!/usr/bin/env python3
"""
Simplified test script for protocol abort vulnerability in MPC protocols.
"""

import time
import random
import hashlib

class MPCProtocol:
    """A simplified MPC protocol implementation to demonstrate abort vulnerabilities."""
    
    def __init__(self):
        """Initialize the MPC protocol."""
        self.private_key = random.randint(1, 0xFFFFFFFF)
        self.state = "INITIALIZED"
        self.nonce = None
        self.message_hash = None
        self.partial_results = {}
    
    def start_protocol(self, message):
        """Start the protocol."""
        if self.state != "INITIALIZED":
            raise ValueError("Protocol already started")
        
        self.message_hash = hashlib.sha256(message.encode()).digest()
        self.nonce = random.randint(1, 0xFFFFFFFF)
        self.state = "STARTED"
        
        # VULNERABLE: Store sensitive information in the state
        self.partial_results["nonce"] = self.nonce
        
        print(f"Protocol started with message hash: {self.message_hash.hex()}")
        return True
    
    def phase1(self):
        """Execute phase 1 of the protocol."""
        if self.state != "STARTED":
            raise ValueError("Protocol not started")
        
        # VULNERABLE: Compute and store intermediate results
        self.partial_results["phase1_result"] = self.nonce * self.private_key
        self.state = "PHASE1_COMPLETED"
        
        print("Phase 1 completed")
        return True
    
    def phase2(self):
        """Execute phase 2 of the protocol."""
        if self.state != "PHASE1_COMPLETED":
            raise ValueError("Phase 1 not completed")
        
        # VULNERABLE: Compute and store more intermediate results
        self.partial_results["phase2_result"] = self.partial_results["phase1_result"] ^ int.from_bytes(self.message_hash[:4], byteorder='big')
        self.state = "PHASE2_COMPLETED"
        
        print("Phase 2 completed")
        return True
    
    def finalize(self):
        """Finalize the protocol and produce the result."""
        if self.state != "PHASE2_COMPLETED":
            raise ValueError("Phase 2 not completed")
        
        # Compute the final result
        result = self.partial_results["phase2_result"] % 0xFFFF
        self.state = "FINALIZED"
        
        print(f"Protocol finalized with result: {result}")
        return result
    
    def abort(self):
        """Abort the protocol."""
        old_state = self.state
        self.state = "ABORTED"
        
        # VULNERABLE: Don't clear sensitive information
        print(f"Protocol aborted from state: {old_state}")
        return self.partial_results

def test_normal_execution():
    """Test normal protocol execution."""
    print("\n=== Testing normal protocol execution ===")
    
    protocol = MPCProtocol()
    protocol.start_protocol("Test message")
    protocol.phase1()
    protocol.phase2()
    result = protocol.finalize()
    
    print(f"Normal execution result: {result}")
    return result

def test_abort_after_phase1():
    """Test aborting the protocol after phase 1."""
    print("\n=== Testing abort after phase 1 ===")
    
    protocol = MPCProtocol()
    protocol.start_protocol("Test message")
    protocol.phase1()
    
    # Abort after phase 1
    partial_results = protocol.abort()
    
    print("Partial results obtained from abort:")
    for key, value in partial_results.items():
        print(f"  {key}: {value}")
    
    # Check if sensitive information was leaked
    if "nonce" in partial_results:
        print("\nVULNERABILITY DETECTED: Nonce leaked through protocol abort!")
    if "phase1_result" in partial_results:
        print("VULNERABILITY DETECTED: Phase 1 intermediate result leaked through protocol abort!")
    
    return partial_results

def test_abort_after_phase2():
    """Test aborting the protocol after phase 2."""
    print("\n=== Testing abort after phase 2 ===")
    
    protocol = MPCProtocol()
    protocol.start_protocol("Test message")
    protocol.phase1()
    protocol.phase2()
    
    # Abort after phase 2
    partial_results = protocol.abort()
    
    print("Partial results obtained from abort:")
    for key, value in partial_results.items():
        print(f"  {key}: {value}")
    
    # Check if sensitive information was leaked
    if "nonce" in partial_results:
        print("\nVULNERABILITY DETECTED: Nonce leaked through protocol abort!")
    if "phase1_result" in partial_results:
        print("VULNERABILITY DETECTED: Phase 1 intermediate result leaked through protocol abort!")
    if "phase2_result" in partial_results:
        print("VULNERABILITY DETECTED: Phase 2 intermediate result leaked through protocol abort!")
    
    return partial_results

def main():
    print("Testing for protocol abort vulnerabilities...")
    
    # Test normal execution
    normal_result = test_normal_execution()
    
    # Test abort after phase 1
    abort_phase1_results = test_abort_after_phase1()
    
    # Test abort after phase 2
    abort_phase2_results = test_abort_after_phase2()
    
    # Summary
    print("\n=== Summary ===")
    print("Normal execution completed successfully.")
    
    vulnerabilities = []
    if "nonce" in abort_phase1_results or "nonce" in abort_phase2_results:
        vulnerabilities.append("Nonce leakage through protocol abort")
    if "phase1_result" in abort_phase1_results or "phase1_result" in abort_phase2_results:
        vulnerabilities.append("Phase 1 intermediate result leakage")
    if "phase2_result" in abort_phase2_results:
        vulnerabilities.append("Phase 2 intermediate result leakage")
    
    if vulnerabilities:
        print("\nVulnerabilities detected:")
        for vuln in vulnerabilities:
            print(f"- {vuln}")
    else:
        print("\nNo vulnerabilities detected.")
    
    return 0

if __name__ == "__main__":
    main()
