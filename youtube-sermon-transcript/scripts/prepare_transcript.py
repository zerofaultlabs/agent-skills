#!/usr/bin/env python3
"""Prepare timestamp-linked caption artifacts for semantic sermon extraction."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse


TIMING = re.compile(
    r"^((?:(\d{2}):)?(\d{2}):(\d{2})\.\d{3})\s+-->\s+"
    r"((?:(\d{2}):)?(\d{2}):(\d{2})\.\d{3})(?:\s+.*)?$"
)
INLINE_TIMESTAMP = re.compile(r"<(?:\d{2}:)?\d{2}:\d{2}\.\d{3}>")
TAG = re.compile(r"<[^>]+>")
SPACE = re.compile(r"\s+")
CAPTION_CHEVRON = re.compile(r"(?<!\S)>{1,2}(?=\s|[A-Za-z])\s*")
SENTENCE_END = re.compile(r"[.!?](?:[\"'”’)]*)$")
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


@dataclass
class Cue:
    start_seconds: float
    end_seconds: float
    lines: list[str]


def timestamp_ms(value: str) -> int:
    parts = value.split(":")
    seconds, milliseconds = parts[-1].split(".")
    minutes = int(parts[-2])
    hours = int(parts[0]) if len(parts) == 3 else 0
    if minutes >= 60 or int(seconds) >= 60:
        raise ValueError(f"Invalid VTT timestamp: {value}")
    return ((hours * 60 + minutes) * 60 + int(seconds)) * 1000 + int(milliseconds)


def format_time(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    whole, fraction = divmod(milliseconds, 1000)
    hours, remainder = divmod(whole, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{fraction:03d}"


def clean_line(line: str) -> str:
    line = INLINE_TIMESTAMP.sub("", line)
    line = TAG.sub("", line)
    # YouTube uses > or >> as speaker-change cues. If retained at the start of
    # a Markdown paragraph, they accidentally render the transcript as a quote.
    line = CAPTION_CHEVRON.sub("", html.unescape(line))
    return SPACE.sub(" ", line).strip()


def parse_vtt(path: Path) -> list[Cue]:
    cues: list[Cue] = []
    content = path.read_text(encoding="utf-8-sig")
    if not content.startswith("WEBVTT"):
        raise ValueError("Expected a WEBVTT header")
    blocks = re.split(r"\n\s*\n", content)
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if lines and (lines[0] in {"STYLE", "REGION"} or re.match(r"^NOTE(?:\s|$)", lines[0])):
            continue
        timing_index = next((i for i, line in enumerate(lines) if TIMING.match(line)), None)
        if timing_index is None:
            if any("-->" in line for line in lines):
                raise ValueError("Malformed VTT cue timing")
            continue
        match = TIMING.match(lines[timing_index])
        assert match is not None
        start = timestamp_ms(match.group(1)) / 1000
        end = timestamp_ms(match.group(5)) / 1000
        if end <= start or (cues and start < cues[-1].start_seconds):
            raise ValueError("VTT cues must have positive duration and ordered start times")
        payload = [clean_line(line) for line in lines[timing_index + 1 :]]
        payload = [line for line in payload if line]
        if payload:
            cues.append(Cue(start, end, payload))
    return cues


WORD = re.compile(r"\w+(?:[’']\w+)*", re.UNICODE)


def rolling_overlap(previous: Cue, current: Cue) -> int:
    """Return prefix words supported by overlapping display times and >=2 words.

    A single repeated word is ambiguous, even with overlapping display times.
    Never compare against the accumulated transcript or deduplicate within a cue.
    """
    if not previous.start_seconds <= current.start_seconds < previous.end_seconds:
        return 0
    left = [m.group().casefold().replace("’", "'") for m in WORD.finditer(" ".join(previous.lines))]
    right = [m.group().casefold().replace("’", "'") for m in WORD.finditer(" ".join(current.lines))]
    for size in range(min(len(left), len(right)), 1, -1):
        if left[-size:] == right[:size]:
            return size
    return 0


def build_segments(cues: list[Cue]) -> list[dict[str, object]]:
    segments: list[dict[str, object]] = []
    for index, cue in enumerate(cues):
        text = " ".join(cue.lines)
        overlap = rolling_overlap(cues[index - 1], cue) if index else 0
        if overlap:
            words = list(WORD.finditer(text))
            text = text[words[overlap].start():] if overlap < len(words) else ""
        if text:
            segments.append({
                "start": format_time(cue.start_seconds),
                "start_seconds": cue.start_seconds,
                "start_ms": round(cue.start_seconds * 1000),
                "end": format_time(cue.end_seconds),
                "end_seconds": cue.end_seconds,
                "end_ms": round(cue.end_seconds * 1000),
                "text": text,
                "source_cue_ids": [index + 1],
                "overlap_words_removed": overlap,
                "overlap_source_cue_id": index if overlap else None,
            })
    return segments


def paragraph_markdown(segments: list[dict[str, object]], sentence_limit: int) -> str:
    paragraphs: list[str] = []
    text_parts: list[str] = []
    timestamp = "00:00:00"
    sentence_count = 0
    for segment in segments:
        if not text_parts:
            timestamp = str(segment["start"])
        part = str(segment["text"])
        text_parts.append(part)
        sentence_count += len(re.findall(r"[.!?](?:[\"'”’)]*)(?=\s|$)", part))
        if sentence_count >= sentence_limit and SENTENCE_END.search(part):
            paragraphs.append(f"[{timestamp}]\n\n{' '.join(text_parts)}")
            text_parts = []
            sentence_count = 0
    if text_parts:
        paragraphs.append(f"[{timestamp}]\n\n{' '.join(text_parts)}")
    return "\n\n".join(paragraphs).strip() + "\n"


def youtube_id(source: str) -> str | None:
    try:
        parsed = urlparse(source)
        if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password or parsed.port:
            return None
        if parsed.hostname in {"youtu.be", "www.youtu.be"}:
            candidate = parsed.path.removeprefix("/")
        elif parsed.hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
            if parsed.path == "/watch":
                values = parse_qs(parsed.query, keep_blank_values=True).get("v", [])
                candidate = values[0] if len(values) == 1 else ""
            else:
                match = re.fullmatch(r"/(?:live|shorts)/([A-Za-z0-9_-]{11})", parsed.path)
                candidate = match.group(1) if match else ""
        else:
            return None
        return candidate if VIDEO_ID.fullmatch(candidate) else None
    except ValueError:
        return None


def select_caption_track(info: dict) -> tuple[str, str]:
    # Human captions before automatic; exact en, en-orig, then lexical en-*.
    for kind, field in (("manual", "subtitles"), ("automatic", "automatic_captions")):
        tracks = info.get(field) or {}
        languages = sorted(tracks, key=lambda lang: (lang != "en", lang != "en-orig", lang))
        for language in languages:
            if (language == "en" or language.startswith("en-")) and any(
                track.get("ext") == "vtt" for track in tracks[language]
            ):
                return kind, language
    raise SystemExit("No supported English VTT caption track is available")


def run_ytdlp(arguments: list[str]) -> str:
    completed = subprocess.run(["yt-dlp", "--ignore-config", *arguments], text=True, capture_output=True)
    if completed.returncode:
        raise SystemExit(completed.stderr.strip() or completed.stdout.strip() or "yt-dlp failed")
    return completed.stdout


def download_vtt(url: str, directory: Path) -> tuple[Path, dict[str, object]]:
    if shutil.which("yt-dlp") is None:
        raise SystemExit("yt-dlp is required for YouTube URLs but was not found in PATH")
    video_id = youtube_id(url)
    if video_id is None:
        raise SystemExit("Unsupported YouTube URL")
    canonical = f"https://www.youtube.com/watch?v={video_id}"
    info = json.loads(run_ytdlp(["--dump-single-json", "--skip-download", "--no-playlist", canonical]))
    if info.get("id") != video_id:
        raise SystemExit("YouTube metadata did not match the requested video ID")
    kind, language = select_caption_track(info)
    arguments = [
        "--write-subs" if kind == "manual" else "--write-auto-subs",
        "--sub-langs", "^" + re.escape(language) + "$", "--sub-format", "vtt",
        "--skip-download", "--no-playlist", "-o", str(directory / "%(id)s.%(ext)s"), canonical,
    ]
    run_ytdlp(arguments)
    path = directory / f"{video_id}.{language}.vtt"
    if not path.is_file() or not path.stat().st_size:
        raise SystemExit("Selected caption track was not downloaded; no artifacts prepared")
    info["caption_provenance"] = {
        "kind": kind, "language": language, "format": "vtt",
        "yt_dlp_version": run_ytdlp(["--version"]).strip(),
        "arguments": arguments, "canonical_url": canonical,
    }
    return path, info


def iso_date(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    digits = value.replace("-", "")
    if len(digits) == 8 and digits.isdigit():
        try:
            return date(int(digits[:4]), int(digits[4:6]), int(digits[6:])).isoformat()
        except ValueError:
            return None
    return None


def select_video_metadata(info: dict[str, object]) -> dict[str, object]:
    """Keep useful, human-readable metadata without copying yt-dlp internals."""
    release_date = iso_date(info.get("release_date"))
    upload_date = iso_date(info.get("upload_date"))
    service_date_candidate = release_date or upload_date
    date_source = "release_date" if release_date else "upload_date" if upload_date else None
    return {
        "title": info.get("title"),
        "description": info.get("description"),
        "channel": info.get("channel") or info.get("uploader"),
        "webpage_url": info.get("webpage_url") or info.get("original_url"),
        "live_status": info.get("live_status"),
        "release_date": release_date,
        "upload_date": upload_date,
        "service_date_candidate": service_date_candidate,
        "service_date_source": date_source,
    }


def safe_stem(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"\.(?:en(?:-[A-Za-z]+)?|en-orig)$", "", stem)
    return re.sub(r"[^A-Za-z0-9._ -]+", "", stem).strip() or "transcript"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download or parse captions into timestamp-linked transcript artifacts."
    )
    parser.add_argument("source", help="YouTube URL or local .vtt file")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd())
    parser.add_argument("--paragraph-sentences", type=int, default=5, metavar="N")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.paragraph_sentences < 1:
        raise SystemExit("--paragraph-sentences must be at least 1")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    video_id = youtube_id(args.source)
    video_metadata: dict[str, object] = {}
    caption_provenance = {"kind": "local", "language": None, "format": "vtt"}

    with tempfile.TemporaryDirectory(prefix="sermon-transcript-") as temporary:
        source_path = Path(args.source).expanduser()
        if source_path.is_file():
            vtt_path = source_path
        elif video_id:
            vtt_path, raw_metadata = download_vtt(args.source, Path(temporary))
            video_metadata = select_video_metadata(raw_metadata)
            caption_provenance = raw_metadata["caption_provenance"]
        else:
            raise SystemExit(f"Not a local VTT file or recognized YouTube URL: {args.source}")

        cues = parse_vtt(vtt_path)
        segments = build_segments(cues)
        if not segments:
            raise SystemExit("No caption text could be extracted from the VTT file")
        stem = safe_stem(vtt_path)
        json_path = args.output_dir / f"{stem}.segments.json"
        markdown_path = args.output_dir / f"{stem}.cleaned.md"
        raw_path = args.output_dir / f"{stem}.raw.vtt"
        evidence = vtt_path.read_bytes()
        # Do not overwrite an earlier run or the user's source file.
        for target in (raw_path, json_path, markdown_path):
            if target.exists():
                raise SystemExit(f"Output already exists: {target}; choose a fresh output directory")
        metadata = {
            "schema_version": 2,
            "provenance": {
                "raw_vtt": raw_path.name,
                "raw_sha256": hashlib.sha256(evidence).hexdigest(),
                "source_identifier": video_id or str(vtt_path.resolve()),
                "caption_track": caption_provenance,
                "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
                "cleanup_version": "timed-whole-word-v1",
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "paragraph_sentences": args.paragraph_sentences,
            },
            "cues": [{
                "id": i + 1,
                "start_ms": round(cue.start_seconds * 1000),
                "end_ms": round(cue.end_seconds * 1000),
                "lines": cue.lines,
            } for i, cue in enumerate(cues)],
            "source": args.source,
            "video_id": video_id,
            "video_metadata": video_metadata,
            "segment_count": len(segments),
            "segments": segments,
        }
        raw_path.write_bytes(evidence)
        json_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        markdown_path.write_text(
            paragraph_markdown(segments, args.paragraph_sentences), encoding="utf-8"
        )

    print(f"Segments: {json_path}")
    print(f"Cleaned transcript: {markdown_path}")


if __name__ == "__main__":
    main()
