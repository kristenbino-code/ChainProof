
import pytest

from algopy import Bytes, String
from algopy_testing import algopy_testing_context

from smart_contracts.chainproof.contract import Chainproof


def test_register_evidence():
    with algopy_testing_context() as context:
        contract = Chainproof()

        evidence_id = String("CASE-001")
        evidence_hash = Bytes(b"a" * 32)

        contract.register_evidence(evidence_id, evidence_hash)

        assert contract.verify_evidence(evidence_id, evidence_hash) is True
        assert contract.get_custodian(evidence_id) == context.default_sender


def test_duplicate_evidence_rejected():
    with algopy_testing_context():
        contract = Chainproof()

        evidence_id = String("CASE-001")
        evidence_hash = Bytes(b"a" * 32)

        contract.register_evidence(evidence_id, evidence_hash)

        with pytest.raises(AssertionError):
            contract.register_evidence(evidence_id, evidence_hash)


def test_modified_evidence_detected():
    with algopy_testing_context():
        contract = Chainproof()

        evidence_id = String("CASE-002")
        original_hash = Bytes(b"a" * 32)
        modified_hash = Bytes(b"b" * 32)

        contract.register_evidence(evidence_id, original_hash)

        assert contract.verify_evidence(evidence_id, original_hash) is True
        assert contract.verify_evidence(evidence_id, modified_hash) is False


def test_authorized_custody_transfer():
    with algopy_testing_context() as context:
        contract = Chainproof()

        evidence_id = String("CASE-003")
        evidence_hash = Bytes(b"c" * 32)
        new_custodian = context.any.account()

        contract.register_evidence(evidence_id, evidence_hash)
        contract.transfer_custody(evidence_id, new_custodian)

        assert contract.get_custodian(evidence_id) == new_custodian


def test_unauthorized_custody_transfer_rejected():
    with algopy_testing_context() as context:
        contract = Chainproof()

        evidence_id = String("CASE-004")
        evidence_hash = Bytes(b"d" * 32)
        attacker = context.any.account()
        new_custodian = context.any.account()

        contract.register_evidence(evidence_id, evidence_hash)

        with context.txn.create_group(
            active_txn_overrides={"sender": attacker}
        ):
            with pytest.raises(AssertionError):
                contract.transfer_custody(evidence_id, new_custodian)

        assert contract.get_custodian(evidence_id) == context.default_sender
