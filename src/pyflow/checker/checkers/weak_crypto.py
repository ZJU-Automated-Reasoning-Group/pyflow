# Check for weak cryptographic practices
import ast

from ..core import issue
from ..core import test_properties as test


def weak_crypto_issue():
    """Create a weak crypto issue"""
    return issue.Issue(
        severity="MEDIUM",
        confidence="HIGH",
        cwe=issue.Cwe.BROKEN_CRYPTO,
        text="Use of weak cryptographic primitive.",
    )


@test.checks("Call")
@test.with_id("B303")
def weak_cryptographic_key(context):
    """Check for weak cryptographic key sizes"""
    if context.call_function_name_qual in ["Crypto.Cipher.AES.new", "AES.new"]:
        # Check for weak key sizes
        key_size = context.get_call_arg_value("key_size")
        if key_size and int(key_size) < 128:
            return weak_crypto_issue()


@test.checks("Call")
@test.with_id("B304")
def weak_hash_functions(context):
    """Check for weak hash functions"""
    if context.call_function_name_qual in ["hashlib.md5", "hashlib.sha1"]:
        return issue.Issue(
            severity="MEDIUM",
            confidence="HIGH",
            cwe=issue.Cwe.BROKEN_CRYPTO,
            text="Use of insecure MD4, MD5, or SHA1 hash function.",
        )
