"""ask 스킬의 학습 기록: 요청마다 빠뜨린 항목을 JSONL 로 쌓고 통계를 낸다.

사용법
  add   표준입력으로 JSON 한 개를 받아 기록한다. score(0~5)는 선택이다.
        {"original": "원래 입력", "missing": ["CONTEXT"], "big": false, "score": 3}
  stats 최근 기록에서 자주 빠뜨리는 항목을 센다. (--last N, 기본 20)

기록 위치: ~/.claude/ask-log.jsonl (환경변수 ASK_LOG_PATH 로 바꿀 수 있다)
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

LOG = Path(os.environ.get("ASK_LOG_PATH") or Path.home() / ".claude" / "ask-log.jsonl")
ITEMS = ("GOAL", "CONSTRAINTS", "CONTEXT")
MAX_LEN = 200  # 긴 로그·코드를 통째로 쌓지 않는다
SECRET = re.compile(
    r"sk-[A-Za-z0-9_\-]{8,}"
    r"|[A-Za-z0-9_\-]{32,}"
    r"|[\w.+-]+@[\w-]+\.[\w.]+"
    r"|(?i:(?:password|passwd|token|secret|api[_-]?key)\s*[=:]\s*\S+)"
)


def mask(text):
    return SECRET.sub("***", text)


def add():
    data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    missing = [m for m in data.get("missing", []) if m in ITEMS]
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "original": mask(str(data.get("original", "")).replace("\n", " "))[:MAX_LEN],
        "missing": missing,
        "big": bool(data.get("big", False)),
    }
    score = data.get("score")
    if isinstance(score, int) and not isinstance(score, bool) and 0 <= score <= 5:
        entry["score"] = score
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    total = sum(1 for _ in LOG.open(encoding="utf-8"))
    print("기록됨 (총 {}건)".format(total))


def load():
    if not LOG.exists():
        return []
    rows = []
    for line in LOG.open(encoding="utf-8"):
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue  # 손상된 줄은 건너뛴다
    return rows


def stats(last):
    rows = load()[-last:]
    if not rows:
        print("기록이 없습니다.")
        return
    n = len(rows)
    count = Counter(m for r in rows for m in r.get("missing", []))
    big = sum(1 for r in rows if r.get("big"))
    print("최근 {}건 기준".format(n))
    for item in ITEMS:
        c = count.get(item, 0)
        print("- {} 빠뜨림: {}건 ({}%)".format(item, c, round(c * 100 / n)))
    print("- 큰 요청: {}건".format(big))
    scores = [r["score"] for r in rows if isinstance(r.get("score"), int)]
    if scores:
        print("- 평균 전달력: {:.1f}/5 ({}건)".format(sum(scores) / len(scores), len(scores)))
    if len(scores) >= 6:
        half = len(scores) // 2
        old, new = scores[:half], scores[half:]
        print("  이전 절반 {:.1f} -> 최근 절반 {:.1f}".format(sum(old) / len(old), sum(new) / len(new)))
    if n < 5:
        print("기록이 5건 미만이라 경향을 판단하기는 이릅니다.")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("add")
    s = sub.add_parser("stats")
    s.add_argument("--last", type=int, default=20)
    args = p.parse_args()
    if args.cmd == "add":
        add()
    else:
        stats(args.last)


if __name__ == "__main__":
    main()
