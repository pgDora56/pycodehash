from unittest import TestCase
from codehash.codehash import CodeHash


class TestCodeHash(TestCase):
    def test_normal_code_hash(self):
        ch = CodeHash("../CodeHash/target/CodeHash-0.1.0.jar")
        c1 = "print('Hello')"
        c2 = "print('Hell')"
        c3 = "print('Hell'+'o')"
        print(ch.codehash(c1, c1))
        print(ch.codehash(c1, c2, "jaccard"))
        print(ch.codehash(c1, c3, ["jaccard", "overlap-similarity"], n=3))

    def test_codehash_with_id(self):
        ch = CodeHash("../CodeHash/target/CodeHash-0.1.0.jar")
        c1 = {
            "_id": "1",
            "code": "print('Hello')",
        }
        c2 = {
            "_id": "2",
            "code": "print('Hell')"
        }
        c3 = {
            "_id": "3",
            "code": "print('Hell'+'o')"
        }
        print(ch.codehash_with_id(c1, c1))
        print(ch.codehash_with_id(c1, c2, "jaccard"))
        print(
            ch.codehash_with_id(
                c1, c3, "overlap-similarity", n=3))

    def test_codehash_with_cache(self):
        ch = CodeHash("../CodeHash/target/CodeHash-0.1.0.jar")
        c1 = {
            "_id": "1",
            "code": "print('Hello')",
        }
        c2 = {
            "_id": "2",
            "code": "print('Hell')"
        }
        c3 = {
            "_id": "3",
            "code": "print('Hell'+'o')"
        }
        ch.codehash_cache_get([c1, c2, c3])
        print(ch.codehash_with_id(c1, c2))
        print(ch.codehash_with_id(c1, c2, "jaccard"))
        print(
            ch.codehash_with_id(
                c1, c3, ["jaccard", "exact-jaccard"], n=3))
