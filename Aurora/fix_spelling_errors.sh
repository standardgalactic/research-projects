#!/usr/bin/env bash
# Preview: bash fix_spelling_errors.sh [directory]
# Apply:   bash fix_spelling_errors.sh --apply [directory]
# Requires Python 3. Processes only immediate *.txt and *.vtt files.
set -euo pipefail
exec python3 - "$@" <<'PY'
import argparse
import difflib
import os
from pathlib import Path
import re
import shutil
import tempfile
from datetime import datetime

parser = argparse.ArgumentParser(description='Preview explicit transcription corrections; --apply saves backups and writes changes.')
parser.add_argument('--apply', action='store_true')
parser.add_argument('directory', nargs='?', default='.')
args = parser.parse_args()
root = Path(args.directory).resolve()
if not root.is_dir():
    parser.error('directory does not exist')

# (filename prefix or '*', incorrect phrase, corrected phrase)
# Add only reviewed phrases. No fuzzy matching or general spellchecker.
RULES = [
    ('*', 'Flickagin', 'Flyxion'),
    ('*', 'Flickshenian', 'Flyxion'),
    ('*', 'Amplet-Whisk', 'Amplitwist'),
    ('*', 'Amplit-Whisk', 'Amplitwist'),
    ('*', 'ampli-list cascade', 'Amplitwist cascade'),
    ('*', 'amplit width', 'Amplitwist'),
    ('*', 'sphere-pop', 'Spherepop'),
    ('*', 'sphere pop', 'Spherepop'),
    ('*', 'Bing Chulhan', 'Byung-Chul Han'),
    ('*', 'James Munkers', 'James Munkres'),
    ('*', 'Guy D. Board', 'Guy Debord'),
    ('The_Physics_of_Recomposable_Fragmentation', 'Flyxion, Sykes,', 'Flyxion cites'),
    ('The_Physics_of_the_Clip_Economy', 'staler field', 'scalar field'),
    ('The_Physics_of_the_Clip_Economy', 'context law', 'context loss'),
    ('The_Physics_of_the_Clip_Economy', 'copological spaced repetition', 'topological spaced repetition'),
    ('The_secret_geometric_dance_of_typing', 'corded ballet', 'chorded ballet'),
    ('The_secret_geometric_dance_of_typing', 'corded keyboards', 'chorded keyboards'),
    ('The_secret_geometric_dance_of_typing', 'cord structure', 'chord structure'),
    ('The_secret_geometric_dance_of_typing', 'In answer that', 'To answer that'),
    ('Your_hands_are_not_typing_symbols', 'sequence the cords', 'sequence the chords'),
    ('Your_hands_are_not_typing_symbols', 'hand is Flyxion', 'hand is flying'),
    ('Your_hands_are_not_typing_symbols', 'hand was Flyxion', 'hand was flying'),
]

def compile_rule(old):
    # Permit phrase matches over subtitle line wraps, but never cue boundaries.
    parts = re.split(r'\s+', old)
    return re.compile(r'(?<!\w)' + r'\s+'.join(map(re.escape, parts)) + r'(?!\w)', re.I)

compiled = [(scope, compile_rule(old), new) for scope, old, new in RULES]

def correct_segment(segment, filename):
    # Token offsets allow replacement across line wraps while keeping ALL original
    # whitespace, including line endings. Replacement words occupy existing slots.
    tokens = list(re.finditer(r'\S+', segment))
    if not tokens:
        return segment
    flat = ' '.join(t.group() for t in tokens)
    slots = list(re.finditer(r'\S+', flat))
    edits = []
    occupied = set()
    for scope, pattern, replacement in compiled:
        if scope != '*' and not filename.startswith(scope):
            continue
        for match in pattern.finditer(flat):
            indexes = [i for i, t in enumerate(slots) if t.start() < match.end() and t.end() > match.start()]
            if not indexes or occupied.intersection(indexes):
                continue
            first, last = indexes[0], indexes[-1]
            prefix = flat[slots[first].start():match.start()]
            suffix = flat[match.end():slots[last].end()]
            words = replacement.split()
            # Extra words go into the final slot; surplus slots become empty.
            for j, idx in enumerate(indexes):
                value = words[j] if j < len(words) else ''
                if j == len(indexes)-1 and len(words) > len(indexes):
                    value = ' '.join(words[j:])
                if j == 0:
                    value = prefix + value
                if j == len(indexes)-1:
                    value += suffix
                edits.append((tokens[idx].start(), tokens[idx].end(), value))
            occupied.update(indexes)
    for start, end, value in sorted(edits, reverse=True):
        segment = segment[:start] + value + segment[end:]
    return segment

def transform(text, path):
    if path.suffix.lower() != '.vtt':
        # Paragraphs remain separate; phrases may cross ordinary TXT line wraps.
        return ''.join(part if re.fullmatch(r'(?:\r?\n[ \t]*){2,}', part) else correct_segment(part, path.name)
                       for part in re.split(r'((?:\r?\n[ \t]*){2,})', text))
    parts = re.split(r'((?:\r?\n[ \t]*){2,})', text)
    for i, block in enumerate(parts):
        lines = block.splitlines(keepends=True)
        # Only cue payloads are eligible; headers, NOTE, STYLE, REGION,
        # identifiers, timestamps, settings, and markup remain byte-for-byte.
        timing = next((j for j, line in enumerate(lines) if '-->' in line), None)
        if timing is None or block.lstrip().startswith(('NOTE', 'STYLE', 'REGION', 'WEBVTT')):
            continue
        payload = ''.join(lines[timing+1:])
        payload = ''.join(piece if piece.startswith('<') else correct_segment(piece, path.name)
                          for piece in re.split(r'(<[^>]*>)', payload))
        parts[i] = ''.join(lines[:timing+1]) + payload
    return ''.join(parts)

changes = []
for path in sorted(root.iterdir()):
    if path.is_symlink() or not path.is_file() or path.suffix.lower() not in {'.txt', '.vtt'}:
        continue
    try:
        original = path.read_bytes().decode('utf-8')
    except UnicodeDecodeError:
        raise SystemExit(f'Invalid UTF-8; no files changed: {path}')
    corrected = transform(original, path)
    if corrected != original:
        changes.append((path, original, corrected))
        print(''.join(difflib.unified_diff(original.splitlines(True), corrected.splitlines(True),
                                         fromfile=path.name, tofile=path.name + ' (corrected)')), end='')

if not changes:
    print('No matching corrections.')
elif not args.apply:
    print(f'\nPreview only: {len(changes)} file(s). Run again with --apply to save changes.')
else:
    backup = Path(tempfile.mkdtemp(prefix='transcription_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '_', dir=root))
    # Back up every affected file before making the first change.
    for path, _, _ in changes:
        shutil.copy2(path, backup / path.name)
    for path, _, corrected in changes:
        fd, temp = tempfile.mkstemp(prefix='.' + path.name + '.', dir=root)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(corrected.encode('utf-8'))
            shutil.copymode(path, temp)
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
    print(f'\nUpdated {len(changes)} file(s). Originals: {backup}')
PY

