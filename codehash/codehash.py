from __future__ import annotations
import os
import shutil
import subprocess
import json
import uuid


class CodeHash:
    """
    - `codehash_path` requires path to CodeHash Jar file
    - [optional] `id_key` requires field name of id in codestruct (default: `_id`)
    """

    def __init__(self, codehash_path, id_key="_id"):
        self.CODEHASH_PATH = codehash_path
        self.ID_KEY = id_key
        self.codehash_cache = {}

    def compare(
            self,
            codes: list[str],
            metrics=None,  # str or list
            n: int = None) -> object:
        """Compares source code lists of type `str` with each other.

        - `metrics` requires `str` or `list of str`.
        """
        if os.path.exists("./tmp"):
            shutil.rmtree("./tmp")
        os.makedirs("tmp")

        files = []
        for c in codes:
            id_key = str(uuid.uuid4())
            fname = "tmp/" + id_key + ".py"
            with open(fname, "w") as f:
                f.write(c)
            files.append(fname)
        jsdata = self.compare_files(files, metrics, n)
        shutil.rmtree("./tmp")
        return jsdata

    def compare_with_id(
            self,
            code_structs: list[dict],
            # code_struct2: dict,
            metrics=None,  # str or list
            n: int = None) -> object:
        """Compares source code(with code's id) lists of type `str` with each other.

        - `codestruct` requires `_id` field and `code` field.
        - `metrics` requires `str` or `list of str`.
        """

        code_structs.sort(key=lambda x: x[self.ID_KEY])

        codehash_ids = []
        for cs in code_structs:
            codehash_ids.append(cs[self.ID_KEY])
        codehash_id = ":".join(codehash_ids)
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

        if os.path.exists("./tmp"):
            shutil.rmtree("./tmp")
        os.makedirs("tmp")
        files = []
        for c in code_structs:
            fname = "tmp/" + c[self.ID_KEY] + ".py"
            with open(fname, "w") as f:
                f.write(c["code"])
            files.append(fname)
        jsdata = self.compare_files(files, metrics, n)
        shutil.rmtree("./tmp")
        return jsdata

    def compare_files(
            self,
            files: list[str],
            metrics=None,
            n: int = None) -> object:
        """Compares source code file lists of type str with each other.

        - `files` requires filename's list.
        - `metrics` requires `str` or `list of str`.
        """
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
        cmd.extend(files)
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        sout = res.stdout.decode("utf8")
        jsdata = json.loads(sout)
        return jsdata

    def compare_directory(
        self,
        dirs: list[str],
        metrics=None,
        n: int = None,
    ) -> object:
        """Compares source code directory lists of type `str` with each other.

        - `files` requires filename's list.
        - `metrics` requires `str` or `list of str`.
        """
        cmd = [
            "java",
            "-classpath",
            self.CODEHASH_PATH,
            "jp.naist.se.codehash.comparison.DirectComparisonMain",
        ]
        for d in dirs:
            if d.endswith("/"):
                d = d[:-1]
            cmd.append(f"-dir{os.path.basename(d)}:{d}")
        cmd.append("-compare:crossgroup")
        if metrics is not None:
            if isinstance(metrics, list):
                cmd.append("-metrics:" + ",".join(metrics))
            elif isinstance(metrics, str):
                cmd.append("-metrics:" + metrics)
            else:
                raise Exception("unknown metrics")
        if n is not None:
            cmd.append("-n:" + str(n))

        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        sout = res.stdout.decode("utf8")
        return json.loads(sout)  # byte->str->json dict

    def make_cache_of_codedatas(
            self,
            code_structs,
            metrics=None,
            n: int = None) -> None:
        """
        Accelerate `codehash_with_id` when comparing multiple codes to each other.

        - `codestruct` requires `_id` field and `code` field.
        - `metrics` requires `str` or `list of str`.
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
