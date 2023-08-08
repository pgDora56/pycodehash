import os
import shutil
import subprocess
import json
import uuid


class CodeHash:
    def __init__(self, codehash_path, id_key="_id"):
        self.CODEHASH_PATH = codehash_path
        self.codehash_cache = {}
        self.ID_KEY = id_key

    def codehash(
            self,
            code1: str,
            code2: str,
            metrics=None,  # str or list
            n: int = None):
        cmd = [
            "java",
            "-classpath",
            self.CODEHASH_PATH,
            "jp.naist.se.codehash.comparison.DirectComparisonMain",
        ]
        if metrics is not None:
            if isinstance(metrics, list):
                cmd.append("-metrics:" + ",".join(metrics))
            elif isinstance(metrics, str):
                cmd.append("-metrics:" + metrics)
            else:
                raise Exception("unknown metrics")
        if n is not None:
            cmd.append("-n:" + str(n))

        if os.path.exists("./tmp"):
            shutil.rmtree("./tmp")
        os.makedirs("tmp")
        cs = [
            {
                self.ID_KEY: str(uuid.uuid4()),
                "code": code1,
            },
            {
                self.ID_KEY: str(uuid.uuid4()),
                "code": code2,
            },
        ]
        for submit in cs:
            fname = "tmp/" + submit[self.ID_KEY] + ".py"
            with open(fname, "w") as f:
                f.write(submit["code"])
            cmd.append(fname)
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        sout = res.stdout.decode("utf8")
        jsdata = json.loads(sout)
        shutil.rmtree("./tmp")
        return jsdata["Pairs"][0]

    def codehash_with_id(
            self,
            code_struct1: dict,
            code_struct2: dict,
            metrics=None,  # str or list
            n: int = None):
        """
        `codestruct` required `_id` field and `code` field.
        """
        if code_struct1[self.ID_KEY] > code_struct2[self.ID_KEY]:  # swap
            code_struct1, code_struct2 = code_struct2, code_struct1

        codehash_id = code_struct1[self.ID_KEY] + \
            ":" + code_struct2[self.ID_KEY]
        if metrics is not None:
            if isinstance(metrics, list):
                metrics.sort()
                codehash_id += "-" + ",".join(metrics)
            elif isinstance(metrics, str):
                codehash_id += "-" + metrics
            else:
                raise Exception("unknown metrics")
        if n is not None:
            codehash_id += "-" + str(n)

        if codehash_id in self.codehash_cache:
            return self.codehash_cache[codehash_id]

        result = self.codehash(
            code_struct1["code"],
            code_struct2["code"],
            metrics,
            n)
        self.codehash_cache[codehash_id] = result
        return result

    # TODO: Directoryごとに比較するやつが実装されているのでそれを使用するように修正
    def codehash_cache_get(
            self,
            code_structs,
            metrics: str = None,
            n: int = None):
        """
        Accelerate `codehash_with_id` when comparing multiple codes to each other.
        `codestruct` required `_id` field and `code` field.
        """
        if os.path.exists("./tmp"):
            shutil.rmtree("./tmp")
        os.makedirs("tmp")
        cmd = [
            "java",
            "-classpath",
            self.CODEHASH_PATH,
            "jp.naist.se.codehash.comparison.DirectComparisonMain",
        ]
        if metrics is not None:
            if isinstance(metrics, list):
                cmd.append("-metrics:" + ",".join(metrics))
            elif isinstance(metrics, str):
                cmd.append("-metrics:" + metrics)
            else:
                raise Exception("unknown metrics")
        if n is not None:
            cmd.append("-n:" + str(n))

        codeids = []
        idx = 0
        code_structs.sort(key=lambda x: x[self.ID_KEY])
        for submit in code_structs:
            fname = "tmp/" + submit[self.ID_KEY] + ".py"
            codeids.append(submit[self.ID_KEY])
            idx += 1
            with open(fname, "w") as f:
                f.write(submit["code"])
            cmd.append(fname)

        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        sout = res.stdout.decode("utf8")
        jsdata = json.loads(sout)  # byte->str->json dict
        shutil.rmtree("./tmp")

        for pair in jsdata["Pairs"]:
            idx1 = pair["index1"]
            idx2 = pair["index2"]
            cacheid = codeids[idx1] + ":" + codeids[idx2]
            if metrics is not None:
                cacheid += "-" + metrics
            if n is not None:
                cacheid += "-" + str(n)
            self.codehash_cache[cacheid] = pair

    def isValidCode(self, code, ipt="", output_result=False):
        if not os.path.exists("./tmp"):
            os.makedirs("tmp")
        fname = "tmp/tmp.py"

        if os.path.exists(fname):
            os.remove(fname)
        with open(fname, "w") as f:
            f.write(code)

        cmd = ["timeout", "5", "python3", fname]
        res = subprocess.run(
            cmd,
            input=ipt.encode("utf8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        if output_result:
            print("Stdout:", res.stdout.decode("utf8"))
            print("Stderr:", res.stderr.decode("utf8"))
        if res.returncode != 0:
            return False
        return True


if __name__ == "__main__":
    ch = CodeHash()
    print(ch.isValidCode("print(input())", "1", "Hello", True))
