import os
import shutil
import subprocess
import json


class CodeHash:
    def __init__(self, codehash_path):
        self.CODEHASH_PATH = codehash_path
        self.codehash_cache = {}
    
    def codehash(self, code1:str, code2:str, metrics:str=None, n:int=None):
        cmd = [
            "java", 
            "-classpath", 
            self.CODEHASH_PATH,
            "jp.naist.se.codehash.comparison.DirectComparisonMain",
        ]
        if metrics is not None:
            cmd.append("-metrics:"+metrics)
        if n is not None:
            cmd.append("-n:" + str(n))

        if os.path.exists("./tmp"):
            shutil.rmtree("./tmp")
        os.makedirs("tmp")
        for submit in [code1, code2]:
            fname = "tmp/" + submit["_id"] + ".py"
            with open(fname, "w") as f:
                f.write(submit["code"])
            cmd.append(fname)

        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        sout = res.stdout.decode("utf8")
        jsdata = json.loads(sout)
        return jsdata["Pairs"][0]

    def codehash_with_id(self, code_struct1:dict, code_struct2:dict, metrics:str=None, n:int=None):
        """ 
        `codestruct` required `_id` field and `code` field. 
        """
        if code_struct1["_id"] > code_struct2["_id"]:  # swap
            code_struct1, code_struct2 = code_struct2, code_struct1

        codehash_id = code_struct1["_id"] + ":" + code_struct2["_id"]
        if metrics is not None:
            codehash_id += "-" + metrics
        if n is not None:
            codehash_id += "-" + str(n)

        if codehash_id in self.codehash_cache:
            return self.codehash_cache[codehash_id]

        result = self.codehash(code_struct1["code"], code_struct2["code"], metrics, n)
        self.codehash_cache[codehash_id] = result
        return result

    def codehash_cache_get(self, code_structs, metrics:str=None, n:int=None):
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
            codehash_id += "-" + metrics
        if n is not None:
            cmd.append("-n:" + str(n))

        codeids = []
        idx = 0
        code_structs.sort(key=lambda x: x["_id"])
        for submit in code_structs:
            fname = "tmp/" + submit["_id"] + ".py"
            codeids.append(submit["_id"])
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

        for pair in jsdata["Pairs"]:
            idx1 = pair["index1"]
            idx2 = pair["index2"]
            cacheid = codeids[idx1] + ":" + codeids[idx2]
            if metrics is not None:
                cacheid += "-" + metrics
            if n is not None:
                cacheid += "-" + str(n)
            self.codehash_cache[cacheid] = pair

    def isValidCode(self, code, taskid, ipt="", output_result=False):
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