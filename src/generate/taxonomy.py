"""taxonomy.yaml 로더. 코드 어디에서도 카테고리를 하드코딩하지 않는다."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "taxonomy" / "taxonomy.yaml"

NUMERIC_ID = {
    "rrn", "foreigner_reg_no", "passport_no", "driver_license_no", "phone_no", "business_reg_no",
    "corp_reg_no", "bank_account_no", "securities_account_no", "card_no", "contract_no", "customer_id",
    "access_credential",
}
TEXT_ID = {"person_name", "address", "email", "online_handle"}


@dataclass
class Category:
    id: str
    tier: str
    kind: str
    span_policy: str
    deid_default: str
    format: dict
    subtypes: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)

    @property
    def checksum(self) -> bool:
        return bool(self.format.get("checksum"))


@dataclass
class VariationOp:
    id: str
    level: str
    applies_to: list[str]
    raw: dict

    def applies(self, category: Category) -> bool:
        for sel in self.applies_to:
            if sel == "all":
                return True
            if sel == "numeric_id" and category.id in NUMERIC_ID:
                return True
            if sel == "text_id" and category.id in TEXT_ID:
                return True
            if sel == "attribute" and category.kind == "attribute":
                return True
            if sel == category.id or sel.split(".")[0] == category.id:
                return True
        return False


class Taxonomy:
    def __init__(self, path: Path = DEFAULT_PATH):
        self.raw: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        self.version = str(self.raw["version"])
        self.categories: dict[str, Category] = {}
        for c in self.raw["categories"]:
            self.categories[c["id"]] = Category(
                id=c["id"], tier=c["tier"], kind=c["kind"], span_policy=c["span_policy"],
                deid_default=c["deid_default"], format=c.get("format") or {},
                subtypes=c.get("subtypes") or [], raw=c,
            )
        v = self.raw["variation"]
        self.levels: list[str] = list(v["levels"].keys())          # ['T0','T1','T2','T3']
        self.ops: dict[str, VariationOp] = {
            o["id"]: VariationOp(o["id"], o["level"], _as_list(o["applies_to"]), o) for o in v["ops"]
        }
        self.hard_negative_types = [t["id"] for t in v["hard_negatives"]["types"]]
        self.stt_profile = v.get("stt_profile", {})
        self.generation_policy = v.get("generation_policy", {})
        self.document_types = {d["id"]: d for d in self.raw["document_types"]}

    def __getitem__(self, cid: str) -> Category:
        return self.categories[cid]

    def ids(self, tier: str | None = None, kind: str | None = None) -> list[str]:
        return [c.id for c in self.categories.values()
                if (tier is None or c.tier == tier) and (kind is None or c.kind == kind)]

    def ops_for(self, category: Category, max_level: str) -> list[VariationOp]:
        li = self.levels.index(max_level)
        return [o for o in self.ops.values() if self.levels.index(o.level) <= li and o.applies(category)]


def _as_list(x) -> list[str]:
    return x if isinstance(x, list) else [x]
