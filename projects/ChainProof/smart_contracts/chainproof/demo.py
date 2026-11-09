
import hashlib
from pathlib import Path

import algokit_utils
from smart_contracts.artifacts.chainproof.chainproof_client import ChainproofClient


def main():
    print("\n========== CHAINPROOF ==========")

    # Connect to LocalNet
    algorand = algokit_utils.AlgorandClient.from_environment()
    deployer = algorand.account.from_environment("DEPLOYER")

    # Connect to smart contract
    client = ChainproofClient(
        algorand=algorand,
        app_id=1002,
        default_sender=deployer.address,
    )

    # Select evidence file
    file_name = input("Enter evidence file path: ").strip().strip('"')
    file_path = Path(file_name)

    if not file_path.is_file():
        print("File not found!")
        return

    # Calculate SHA-256 hash
    original_data = file_path.read_bytes()
    original_hash = hashlib.sha256(original_data).digest()

    print("\nSHA-256:", original_hash.hex())

    # Register evidence
    evidence_id = input("Enter a unique evidence ID: ").strip()

    if not evidence_id:
        print("Evidence ID cannot be empty!")
        return

    print("\nRegistering evidence...")
    registration = client.send.register_evidence(
        args=(evidence_id, original_hash)
    )

    print("Registration:", registration.abi_return)
    print("Transaction ID:", registration.tx_id)

    # Verify original evidence
    print("\nVerifying original file...")
    verification = client.send.verify_evidence(
        args=(evidence_id, original_hash)
    )

    print("Original file authentic:", verification.abi_return)

    # Simulate modified evidence
    modified_data = original_data + b"\nTAMPERED"
    modified_hash = hashlib.sha256(modified_data).digest()

    print("\nChecking modified file...")
    tampered_check = client.send.verify_evidence(
        args=(evidence_id, modified_hash)
    )

    print("Modified file authentic:", tampered_check.abi_return)

    # Create another Algorand account
    print("\nCreating a new custodian...")
    new_custodian = algorand.account.random()

    print("New custodian address:", new_custodian.address)

    # Transfer custody
    print("\nTransferring custody...")
    transfer = client.send.transfer_custody(
        args=(evidence_id, new_custodian.address)
    )

    print("Transfer:", transfer.abi_return)
    print("Transaction ID:", transfer.tx_id)

    # Retrieve current custodian
    print("\nChecking current custodian...")
    custodian = client.send.get_custodian(args=(evidence_id,))

    print("Current custodian:", custodian.abi_return)

    print("\n========== DEMO COMPLETE ==========")


if __name__ == "__main__":
    main()
