"""
Import scholarship opportunities from official public sources.

The command intentionally keeps imported records conservative: it stores a
source link and summary, then sends students back to the official page to
verify deadlines, amounts, and application rules.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from urllib.parse import urljoin

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.scholarships.models import Scholarship, ScholarshipSyncRun


KEYWORDS = (
    "borsa",
    "borse",
    "scholarship",
    "contribut",
    "diritto allo studio",
    "disco",
    "laziodisco",
    "alloggio",
    "study grant",
)


@dataclass(frozen=True)
class SourceConfig:
    name: str
    url: str
    provider: str
    is_disco_lazio: bool = False
    region: str = "lazio"
    level: str = "all"
    static_title: str = ""
    static_summary: str = ""


SOURCES = [
    SourceConfig(
        name="LazioDiSCo",
        provider="LazioDiSCo",
        url="https://laziodisco.it/bandi/bando-diritto-allo-studio-25-26/",
        is_disco_lazio=True,
        static_title="Bando Diritto allo Studio LazioDiSCo 2025/2026",
        static_summary=(
            "Regional right-to-study call for Lazio students, including scholarships, "
            "housing, canteen support, international mobility contributions, and graduation prizes."
        ),
    ),
    SourceConfig(
        name="LazioDiSCo Scholarships",
        provider="LazioDiSCo",
        url="https://laziodisco.it/servizi/scholarships/?lang=en",
        is_disco_lazio=True,
        static_title="LazioDiSCo Scholarships and Benefits",
        static_summary=(
            "Official LazioDiSCo scholarship information for students enrolled in Lazio institutions."
        ),
    ),
    SourceConfig(
        name="Regione Lazio",
        provider="Regione Lazio / DiSCo Lazio",
        url="https://regione.lazio.it/notizie/Universita-online-bando-DiSCo-Lazio-2025-2026-diritto-allo-studio",
        is_disco_lazio=True,
        static_title="Regione Lazio announcement: DiSCo right-to-study call 2025/2026",
        static_summary=(
            "Regional announcement for the 2025/2026 DiSCo Lazio right-to-study call, "
            "covering scholarships, housing services, and economic contributions."
        ),
    ),
    SourceConfig(
        name="Sapienza",
        provider="Sapienza Universita di Roma",
        url="https://www.uniroma1.it/node/23974",
        static_title="Sapienza scholarships and student benefits",
        static_summary=(
            "Sapienza scholarship page listing regional DiSCo Lazio support, housing, collaboration grants, "
            "study abroad support, and other student contributions."
        ),
    ),
    SourceConfig(
        name="Tor Vergata Economics",
        provider="Universita degli Studi di Roma Tor Vergata",
        url="https://economia.uniroma2.it/borse-di-studio/",
        static_title="Tor Vergata scholarship information",
        static_summary=(
            "Tor Vergata scholarship information page, including institutional and external scholarship channels."
        ),
    ),
    SourceConfig(
        name="UNINT",
        provider="Universita degli Studi Internazionali di Roma - UNINT",
        url="https://www.unint.eu/entra-in-unint/borse-di-studio-e-agevolazioni-a-a-2025-2026/",
        static_title="UNINT scholarships and fee reductions 2025/2026",
        static_summary=(
            "UNINT scholarship and fee-reduction information for the 2025/2026 academic year, "
            "including access to DiSCo Lazio right-to-study benefits."
        ),
    ),
]


class ScholarshipHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._tag_stack = []
        self._capture_link = None
        self._current_link_text = []
        self.text_blocks = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self._tag_stack.append(tag)
        if tag == "a" and attrs.get("href"):
            self._capture_link = attrs["href"]
            self._current_link_text = []

    def handle_endtag(self, tag):
        if tag == "a" and self._capture_link:
            text = _clean_text(" ".join(self._current_link_text))
            if text:
                self.links.append((text, self._capture_link))
            self._capture_link = None
            self._current_link_text = []
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data):
        text = _clean_text(data)
        if not text:
            return
        if self._capture_link:
            self._current_link_text.append(text)
        if self._tag_stack and self._tag_stack[-1] in {"h1", "h2", "h3", "h4", "p", "li"}:
            self.text_blocks.append(text)


def _clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _looks_like_scholarship(text):
    lowered = text.lower()
    return any(keyword in lowered for keyword in KEYWORDS)


def _find_deadline(text):
    patterns = [
        r"(\d{1,2})[\/\.-](\d{1,2})[\/\.-](20\d{2})",
        r"(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(20\d{2})",
    ]
    months = {
        "gennaio": 1,
        "febbraio": 2,
        "marzo": 3,
        "aprile": 4,
        "maggio": 5,
        "giugno": 6,
        "luglio": 7,
        "agosto": 8,
        "settembre": 9,
        "ottobre": 10,
        "novembre": 11,
        "dicembre": 12,
    }
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        try:
            day = int(match.group(1))
            month = months.get(match.group(2).lower(), int(match.group(2)) if match.group(2).isdigit() else None)
            year = int(match.group(3))
            if month:
                return date(year, month, day)
        except ValueError:
            continue
    return None


class Command(BaseCommand):
    help = "Sync scholarship opportunities from official public sources."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Fetch and parse without saving changes.")
        parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds.")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        timeout = options["timeout"]
        created = 0
        updated = 0
        skipped = 0
        errors = []
        sync_run = ScholarshipSyncRun.objects.create(
            status="dry_run" if dry_run else "running",
            dry_run=dry_run,
            source_count=len(SOURCES),
        )

        for source in SOURCES:
            try:
                payload = self._build_payload(source, timeout)
            except Exception as exc:
                skipped += 1
                message = f"Skipped {source.name}: {exc}"
                errors.append(message)
                self.stderr.write(self.style.WARNING(message))
                continue

            if dry_run:
                self.stdout.write(f"Would sync: {payload['title']} ({source.url})")
                continue

            obj, was_created = self._upsert(payload)
            created += int(was_created)
            updated += int(not was_created)
            verb = "Created" if was_created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb}: {obj.title}"))

        if dry_run:
            self.stdout.write(self.style.SUCCESS("Dry run complete."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Sync complete: {created} created, {updated} updated, {skipped} skipped."))

        sync_run.created_count = created
        sync_run.updated_count = updated
        sync_run.skipped_count = skipped
        sync_run.error_log = "\n".join(errors)
        sync_run.finished_at = timezone.now()
        if dry_run:
            sync_run.status = "dry_run"
        elif skipped and (created or updated):
            sync_run.status = "partial"
        elif skipped and not (created or updated):
            sync_run.status = "failed"
        else:
            sync_run.status = "success"
        sync_run.save(update_fields=[
            "created_count",
            "updated_count",
            "skipped_count",
            "error_log",
            "finished_at",
            "status",
        ])

    def _build_payload(self, source, timeout):
        response = requests.get(
            source.url,
            timeout=timeout,
            headers={"User-Agent": "ASCAI Lazio scholarship sync (+https://ascai.org)"},
        )
        response.raise_for_status()
        parser = ScholarshipHTMLParser()
        parser.feed(response.text)

        text = " ".join(parser.text_blocks)
        scholarship_blocks = [block for block in parser.text_blocks if _looks_like_scholarship(block)]
        scholarship_links = [
            (title, urljoin(source.url, href))
            for title, href in parser.links
            if _looks_like_scholarship(title) or "bando" in href.lower()
        ]

        title = source.static_title or (scholarship_blocks[0] if scholarship_blocks else source.name)
        summary_parts = scholarship_blocks[:4] or parser.text_blocks[:4]
        summary = source.static_summary
        if summary_parts:
            summary = f"{summary} {' '.join(summary_parts)}" if summary else " ".join(summary_parts)
        summary = _clean_text(summary)[:1400]

        application_url = scholarship_links[0][1] if scholarship_links else source.url
        deadline = _find_deadline(text)
        source_hash = hashlib.sha256(_clean_text(text[:8000]).encode("utf-8", errors="ignore")).hexdigest()
        now = timezone.now()

        return {
            "title": title[:200],
            "provider": source.provider,
            "description": summary or source.static_summary or title,
            "eligibility_criteria": self._eligibility_copy(source),
            "application_deadline": deadline,
            "application_url": application_url,
            "level": source.level,
            "region": source.region,
            "is_disco_lazio": source.is_disco_lazio,
            "status": "active",
            "source_name": source.name,
            "source_url": source.url,
            "source_excerpt": summary,
            "source_last_seen_at": now,
            "source_imported_at": now,
            "source_hash": source_hash,
        }

    def _eligibility_copy(self, source):
        if source.is_disco_lazio:
            return (
                "Eligibility is defined by the official LazioDiSCo annual call and may include ISEE/ISEEUP, "
                "merit, enrollment, residency, housing, and documentation requirements. Students should verify "
                "all requirements on the official LazioDiSCo page before applying."
            )
        return (
            "Eligibility depends on the official source page and may vary by degree level, citizenship, merit, "
            "income, enrollment status, or university-specific rules. Students should verify details on the source page."
        )

    def _upsert(self, payload):
        source_url = payload["source_url"]
        slug = slugify(payload["title"])[:200] or "scholarship"
        obj = Scholarship.objects.filter(source_url=source_url).first()
        if not obj:
            obj = Scholarship.objects.filter(slug=slug).first()

        if obj:
            imported_at = obj.source_imported_at or payload["source_imported_at"]
            for key, value in payload.items():
                if key == "source_imported_at":
                    value = imported_at
                setattr(obj, key, value)
            obj.save()
            return obj, False

        obj = Scholarship.objects.create(slug=slug, **payload)
        return obj, True
