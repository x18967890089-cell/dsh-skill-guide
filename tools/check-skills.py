#!/usr/bin/env python3
"""Validate the example skills and the links in this repo's Markdown.

Checks, in order:
  1. every examples/*/SKILL.md starts with a YAML frontmatter block
  2. the frontmatter parses as YAML (no PyYAML: a tiny key: value reader)
  3. it has `name` and `description`, both non-empty
  4. `name` equals the directory name (that is how DSH loads a skill)
  5. every relative link/image target in *.md exists on disk
Exit code 0 = all good, 1 = a check failed.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
checked = 0


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def frontmatter(text):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end < 0:
        return None, text
    return text[3:end], text[end + 4:]


def simple_yaml(block):
    data = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip().strip('"\'')
    return data


def check_skill(skill_dir, name):
    global checked
    path = os.path.join(skill_dir, "SKILL.md")
    rel = os.path.relpath(path, ROOT)
    if not os.path.isfile(path):
        errors.append("%s: missing SKILL.md" % rel)
        return
    block, _ = frontmatter(read(path))
    if block is None:
        errors.append("%s: no --- frontmatter block" % rel)
        return
    meta = simple_yaml(block)
    for key in ("name", "description"):
        if not meta.get(key):
            errors.append("%s: frontmatter is missing a non-empty %r" % (rel, key))
    if meta.get("name") and meta["name"] != name:
        errors.append("%s: name %r must equal the directory name %r"
                      % (rel, meta["name"], name))
    if meta.get("description") and len(meta["description"]) < 20:
        errors.append("%s: description is too short to tell the model when to load it"
                      % rel)
    checked += 1


def check_links():
    pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for base, _dirs, files in os.walk(ROOT):
        if os.sep + ".git" in base:
            continue
        for f in files:
            if not f.endswith(".md"):
                continue
            path = os.path.join(base, f)
            rel = os.path.relpath(path, ROOT)
            for target in pattern.findall(read(path)):
                target = target.split("#")[0].strip()
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = os.path.normpath(os.path.join(base, target))
                if not os.path.exists(resolved):
                    errors.append("%s: link target does not exist: %s" % (rel, target))


def main():
    examples = os.path.join(ROOT, "examples")
    if os.path.isdir(examples):
        for name in sorted(os.listdir(examples)):
            skill_dir = os.path.join(examples, name)
            if os.path.isdir(skill_dir):
                check_skill(skill_dir, name)
    check_links()
    if errors:
        for e in errors:
            print("FAIL " + e)
        print("%d problem(s)" % len(errors))
        return 1
    print("ok: %d skill(s), every link resolves" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())