"""Offline regressions using authored synthetic captions; no service media."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'youtube-sermon-transcript/scripts/prepare_transcript.py'
spec = importlib.util.spec_from_file_location('prepare_transcript', SCRIPT)
p = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = p
spec.loader.exec_module(p)
FIXTURE = Path(__file__).parent / 'fixtures/transcripts/rolling.vtt'


class TranscriptTests(unittest.TestCase):
    def text(self, cues):
        return ' '.join(s['text'] for s in p.build_segments(cues))

    def test_repetition_and_word_boundaries(self):
        for a, b in [('Jesus', 'saves us'), ('We trust God', 'God is faithful'), ('Amen', 'Amen')]:
            with self.subTest(a=a):
                self.assertEqual(self.text([p.Cue(0, 1, [a]), p.Cue(1, 2, [b])]), a + ' ' + b)
        self.assertEqual(self.text([p.Cue(0, 3, ['Amen']), p.Cue(2, 4, ['Amen'])]), 'Amen Amen')

    def test_rolling(self):
        for caption, expected in [('trust God, always.', 'We trust God always.'), ('WE TRUST GOD', 'We trust God'), ('Something else', 'We trust God Something else')]:
            with self.subTest(caption=caption):
                self.assertEqual(self.text([p.Cue(0, 3, ['We trust God']), p.Cue(2, 4, [caption])]), expected)
        self.assertEqual(self.text([p.Cue(0, 1, ['We trust God']), p.Cue(2, 3, ['We trust God'])]), 'We trust God We trust God')

    def test_encoded_marker(self):
        self.assertEqual(p.clean_line('&gt;&gt; Welcome'), 'Welcome')

    def test_precision(self):
        cues = p.parse_vtt(FIXTURE)
        self.assertEqual(cues[0].start_seconds, 2057.125)
        self.assertEqual(cues[0].end_seconds, 2060.5)
        self.assertEqual(self.text(cues), 'We trust God always. Amen Amen')

    def test_urls(self):
        vid = 'Abc_def-123'
        for url in [f'https://youtube.com/watch?v={vid}', f'https://youtu.be/{vid}', f'https://www.youtube.com/live/{vid}', f'https://m.youtube.com/shorts/{vid}']:
            self.assertEqual(p.youtube_id(url), vid)
        for url in [f'https://evilyoutube.com/watch?v={vid}', f'https://youtube.com.evil/watch?v={vid}', f'ftp://youtube.com/watch?v={vid}', f'https://youtu.be/{vid}/extra', f'https://youtube.com/watch?v={vid}&v={vid}', 'https://youtu.be/short']:
            self.assertIsNone(p.youtube_id(url))

    def test_dates(self):
        meta = p.select_video_metadata({'release_date': '20260913', 'upload_date': '20260914'})
        self.assertEqual(meta['service_date_candidate'], '2026-09-13')
        self.assertIsNone(p.iso_date('20260230'))
        self.assertEqual(p.select_video_metadata({'upload_date': '20260914'})['service_date_source'], 'upload_date')

    def test_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, '-B', str(SCRIPT), str(FIXTURE), '--output-dir', tmp], check=True, capture_output=True)
            data = json.loads(next(Path(tmp).glob('*.segments.json')).read_text())
            self.assertEqual((Path(tmp) / data['provenance']['raw_vtt']).read_bytes(), FIXTURE.read_bytes())
            self.assertEqual(data['segments'][0]['source_cue_ids'], [1])
            self.assertEqual(data['cues'][0]['start_ms'], 2057125)
            self.assertEqual(data['segments'][1]['source_cue_ids'], [2])

    def test_track_selection(self):
        vtt = [{'ext': 'vtt'}]
        self.assertEqual(p.select_caption_track({'subtitles': {'en-GB': vtt}, 'automatic_captions': {'en': vtt}}), ('manual', 'en-GB'))
        self.assertEqual(p.select_caption_track({'automatic_captions': {'en-US': vtt, 'en-orig': vtt, 'en': vtt}}), ('automatic', 'en'))
        with self.assertRaises(SystemExit):
            p.select_caption_track({'subtitles': {'en': [{'ext': 'srt'}]}})

    def test_download_and_failure(self):
        vid = 'Abc_def-123'
        info = {'id': vid, 'subtitles': {'en': [{'ext': 'vtt'}]}, 'release_date': '20260913'}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def fake_run(args):
                if '--dump-single-json' in args:
                    return json.dumps(info)
                if '--version' in args:
                    return 'test-version'
                (root / f'{vid}.en.vtt').write_bytes(FIXTURE.read_bytes())
                return ''
            with patch.object(p.shutil, 'which', return_value='/fake/yt-dlp'), patch.object(p, 'run_ytdlp', side_effect=fake_run):
                path, metadata = p.download_vtt(f'https://youtube.com/live/{vid}', root)
            self.assertEqual(path.read_bytes(), FIXTURE.read_bytes())
            self.assertEqual(metadata['caption_provenance']['kind'], 'manual')
            self.assertEqual(metadata['caption_provenance']['yt_dlp_version'], 'test-version')
        with patch.object(p.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, '', 'network failed')):
            with self.assertRaisesRegex(SystemExit, 'network failed'):
                p.run_ytdlp([])

    def test_failed_acquisition_writes_no_artifacts(self):
        for failure in ['No supported English VTT caption track', 'network failed']:
            with tempfile.TemporaryDirectory() as tmp:
                args = p.argparse.Namespace(source='https://youtube.com/live/Abc_def-123', output_dir=Path(tmp), paragraph_sentences=5)
                with patch.object(p, 'parse_args', return_value=args), patch.object(p, 'download_vtt', side_effect=SystemExit(failure)):
                    with self.assertRaises(SystemExit):
                        p.main()
                self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_same_second_and_multiline_repetition(self):
        cues = [p.Cue(1.001, 1.2, ['Go now', 'Go now']), p.Cue(1.3, 1.9, ['Go now'])]
        segments = p.build_segments(cues)
        self.assertEqual(len(segments), 2)
        self.assertEqual(self.text(cues), 'Go now Go now Go now')
        self.assertEqual(segments[1]['start'], '00:00:01.300')

    def test_invalid_and_empty_vtt(self):
        for content in ['not VTT', 'WEBVTT\n\n00:00:aa.000 --> 00:00:02.000\nWords', 'WEBVTT\n']:
            with tempfile.TemporaryDirectory() as tmp:
                source = Path(tmp) / 'source.vtt'
                source.write_text(content)
                output = Path(tmp) / 'out'
                result = subprocess.run([sys.executable, '-B', str(SCRIPT), str(source), '--output-dir', str(output)], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(list(output.iterdir()), [])

    def test_existing_artifacts_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = [sys.executable, '-B', str(SCRIPT), str(FIXTURE), '--output-dir', tmp]
            subprocess.run(command, check=True, capture_output=True)
            before = {f.name: f.read_bytes() for f in Path(tmp).iterdir()}
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(before, {f.name: f.read_bytes() for f in Path(tmp).iterdir()})


if __name__ == '__main__':
    unittest.main()
