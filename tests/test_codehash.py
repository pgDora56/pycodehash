from unittest import TestCase
from codehash.codehash import CodeHash


class TestCodeHash(TestCase):
    def test_normal_code_hash(self):
        print("##### START test_normal_code_hash")
        ch = CodeHash("../CodeHash/target/CodeHash-0.1.0.jar")
        c1 = "print('Hello')"
        c2 = "print('Hell')"
        c3 = "print('Hell'+'o')"
        print(ch.compare([c1, c1]))
        print(ch.compare([c1, c2], "jaccard"))
        print(ch.compare([c1, c3], ["jaccard", "overlap-similarity"], n=3))
        print("##### END test_normal_code_hash")

    def test_codehash_with_id(self):
        print("##### START test_codehash_with_id")
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
        print(ch.compare_with_id([c1, c2, c3]))
        print(ch.compare_with_id([c1, c2], "jaccard"))
        print(
            ch.compare_with_id(
                [c1, c3], "overlap-similarity", n=3))
        print("##### END test_codehash_with_id")

    def test_codehash_with_cache(self):
        print("##### START test_codehash_with_cache")
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
        ch.make_cache_of_codedatas([c1, c2, c3])
        print(ch.compare_with_id([c1, c2]))
        print(ch.compare_with_id([c1, c2], "jaccard"))
        print(
            ch.compare_with_id(
                [c1, c3], ["jaccard", "exact-jaccard"], n=3))
        print("##### END test_codehash_with_cache")

    def test_compare_directory(self):
        print("##### START test_compare_directory")
        ch = CodeHash("../CodeHash/target/CodeHash-0.1.0.jar")
        print(ch.compare_directory(
            ["sample_files/a", "sample_files/b/", "sample_files/c"]))
        print("##### END test_compare_directory")
