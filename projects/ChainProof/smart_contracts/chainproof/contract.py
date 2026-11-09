
from algopy import ARC4Contract, BoxMap, Bytes, Account, String, Txn
from algopy.arc4 import abimethod


class Chainproof(ARC4Contract):

    def __init__(self) -> None:
        # Stores the SHA-256 hash of each evidence file
        self.evidence_hashes = BoxMap(
            String, Bytes, key_prefix=b"hash_"
        )

        # Stores the current custodian of each evidence file
        self.custodians = BoxMap(
            String, Account, key_prefix=b"owner_"
        )

    @abimethod()
    def register_evidence(
        self,
        evidence_id: String,
        evidence_hash: Bytes
    ) -> String:

        assert evidence_id not in self.evidence_hashes, "Evidence already registered"
        assert evidence_hash.length == 32, "Invalid SHA-256 hash length"

        self.evidence_hashes[evidence_id] = evidence_hash
        self.custodians[evidence_id] = Txn.sender

        return String("Evidence registered successfully")

    @abimethod()
    def transfer_custody(
        self,
        evidence_id: String,
        new_custodian: Account
    ) -> String:

        assert evidence_id in self.evidence_hashes, "Evidence not found"
        assert self.custodians[evidence_id] == Txn.sender, "Unauthorized transfer"

        self.custodians[evidence_id] = new_custodian

        return String("Custody transferred successfully")

    @abimethod()
    def verify_evidence(
        self,
        evidence_id: String,
        submitted_hash: Bytes
    ) -> bool:

        assert evidence_id in self.evidence_hashes, "Evidence not found"

        return self.evidence_hashes[evidence_id] == submitted_hash

    @abimethod()
    def get_custodian(self, evidence_id: String) -> Account:

        assert evidence_id in self.custodians, "Evidence not found"

        return self.custodians[evidence_id]
