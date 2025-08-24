
#!/usr/bin/env python3
"""
rename_docusaurus_units.py

Safe, reversible script to insert a new minor unit into a Docusaurus-style documentation tree
by incrementing following unit numbers, renaming image folders, and updating internal references
and frontmatter 'sidebar_position', 'id', and 'slug' fields.

HOW IT WORKS (summary)
- You specify the docs root directory, the major unit number (e.g. 8) and the minor index to insert (e.g. 2).
  That will *insert* a new unit between X.Y-1 and X.Y by incrementing all existing units with minor >= insertion_minor.
  Example: major=8, insert_minor=2 will make 8.2 become 8.3, 8.5 -> 8.6, and 8.5.1 -> 8.6.1, etc.
- The script:
  1. optionally makes a backup copy of the docs_root (recommended)
  2. finds all directories and files whose names begin with "<major>.<minor>" where minor >= insertion_minor
     and renames them to increment the minor by 1 (rename done in descending order to avoid collisions)
  3. scans all .md/.mdx/.mdown files and updates:
     - occurrences of "<major>.<minor>" in filenames, slugs, ids, and image-folder paths (only when not part of a larger number)
     - image folder names like "8.5-Images" -> "8.6-Images"
     - YAML frontmatter: sidebar_position (if >= sidebar_threshold) is incremented
     - frontmatter id and slug values if they start with the numbering prefix
  4. writes changes, or prints them if --dry-run

USAGE
    python3 rename_docusaurus_units.py --docs_root path/to/docs --major 8 --insert_minor 2 [--backup True] [--dry-run]

IMPORTANT NOTES & SAFETY
- Default behavior creates a backup copy of the entire docs_root in docs_root__backup__TIMESTAMP.
  If your docs folder is large, set --backup False but only do that if you have your own backups (git).
- Always run with --dry-run first to inspect planned renames and replacements.
- This script tries to be conservative when replacing text: it only replaces number tokens that are not part of a bigger number
  (so "8.5" will be replaced but "128.5" won't accidentally match).
- The script does NOT attempt to reorder complex frontmatter structures beyond simple id/slug/sidebar_position numeric updates.
  Review output after running.

LIMITATIONS
- It assumes numbering uses a dotted numeric format like "8.5" at the start of filenames/folders or inside paths.
- It may still require some manual cleanup (links deep inside HTML, JS or unrecognized patterns).
- If you use git, run this in a clean working tree so you can inspect and revert easily.

"""

import argparse
import os
import re
import shutil
import time
from pathlib import Path

def backup_folder(src: Path):
    ts = time.strftime("%Y%m%d-%H%M%S")
    dest = src.parent / (src.name + "__backup__" + ts)
    print(f"Creating backup copy: {dest}")
    shutil.copytree(src, dest)
    return dest

def find_targets(root: Path, major: int, insert_minor: int):
    """
    Find file and directory paths that start with "<major>.<minor>" where minor >= insert_minor.
    Returns list of Paths to rename.
    """
    pattern = re.compile(rf'^{re.escape(str(major))}\.(\d+)([.\-\w].*)?$')
    targets = []
    for p in root.rglob('*'):
        # consider only files/directories whose basename matches the pattern
        name = p.name
        m = pattern.match(name)
        if m:
            minor = int(m.group(1))
            if minor >= insert_minor:
                targets.append((p, minor))
    # sort so we rename highest minors first (descending) to avoid collisions
    targets.sort(key=lambda x: (x[1], len(str(x[0]))), reverse=True)
    return targets

def compute_new_name(old_name: str, major: int, minor: int):
    """
    Replace the leading '<major>.<minor>' with '<major>.<minor+1>' preserving the rest of the name.
    """
    prefix = f"{major}.{minor}"
    new_prefix = f"{major}.{minor+1}"
    if old_name.startswith(prefix):
        return new_prefix + old_name[len(prefix):]
    # fallback - shouldn't happen
    return old_name

def rename_filesystem(targets, dry_run=False):
    """
    Rename the filesystem entries. Targets should be list of (Path, minor) sorted descending.
    Operates by moving paths.
    """
    ops = []
    for p, minor in targets:
        old = p
        new_name = compute_new_name(p.name, args.major, minor)
        new_path = p.with_name(new_name)
        ops.append((old, new_path))
    # perform operations
    for old, new in ops:
        print(f"Rename: {old} -> {new}")
    if not dry_run:
        for old, new in ops:
            # ensure parent exists
            if new.exists():
                raise FileExistsError(f"Target path already exists: {new}. Aborting to avoid data loss.")
        for old, new in ops:
            old.rename(new)
    return ops

def update_markdown_contents(root: Path, major: int, insert_minor: int, sidebar_threshold: int, dry_run=False):
    """
    Update in-file references inside markdown/mdx files:
      - replace occurrences of major.minor where minor >= insert_minor with minor+1
      - rename image-folder references like '8.5-Images'
      - update frontmatter sidebar_position, id, slug if necessary
    """
    md_exts = {'.md', '.mdx', '.markdown', '.mdown'}
    # prepare replacement map for quick checking
    # We'll build pairs like ('8.5', '8.6') for all minors >= insert_minor up to a sensible max found in files.
    # First, scan files for existing minors so we target actual ones.
    minors_found = set()
    number_token_pattern = re.compile(rf'(?<!\d)({major})\.(\d+)(?!\d)')
    for p in root.rglob('*'):
        if p.suffix.lower() in md_exts:
            text = p.read_text(encoding='utf-8', errors='ignore')
            for m in number_token_pattern.finditer(text):
                minors_found.add(int(m.group(2)))
    # Only consider minors >= insert_minor
    minors_to_change = sorted([m for m in minors_found if m >= insert_minor], reverse=True)
    repl_pairs = [(f"{major}.{m}", f"{major}.{m+1}") for m in minors_to_change]

    # compile regex patterns
    # replace tokens where the numeric token is not part of a larger number (using lookarounds)
    token_patterns = [(re.compile(rf'(?<!\d){re.escape(old)}(?!\d)'), new) for old, new in repl_pairs]
    # also prepare image-folder pattern (e.g. "8.5-Images" or "8.5_images")
    img_patterns = [(re.compile(re.escape(old) + r'(?=[_\-\/])'), new) for old, new in repl_pairs]

    # frontmatter handling
    fm_pattern = re.compile(r'^---\s*\n(.*?\n?)^---\s*\n', re.DOTALL | re.MULTILINE)
    sidebar_pattern = re.compile(r'(^\s*sidebar_position\s*:\s*)(\d+)\s*$', re.MULTILINE)
    id_pattern = re.compile(r'(^\s*id\s*:\s*[\'"]?)([^\'"\n]+)([\'"]?\s*$)', re.MULTILINE)
    slug_pattern = re.compile(r'(^\s*slug\s*:\s*[\'"]?)([^\'"\n]+)([\'"]?\s*$)', re.MULTILINE)

    files_changed = []

    for p in root.rglob('*'):
        if p.suffix.lower() in md_exts:
            text = p.read_text(encoding='utf-8', errors='ignore')
            orig_text = text

            # frontmatter block
            mfm = fm_pattern.search(text)
            if mfm:
                fm = mfm.group(1)
                new_fm = fm

                # update sidebar_position if value >= sidebar_threshold
                def sidebar_repl(m):
                    val = int(m.group(2))
                    if val >= sidebar_threshold:
                        newval = val + 1
                        print(f"  Updating sidebar_position in {p}: {val} -> {newval}")
                        return m.group(1) + str(newval)
                    return m.group(0)
                new_fm = sidebar_pattern.sub(sidebar_repl, new_fm)

                # update id if it starts with the numbered prefix
                def id_repl(m):
                    prefix = m.group(2)
                    for old, new in repl_pairs:
                        if prefix.startswith(old):
                            updated = new + prefix[len(old):]
                            print(f"  Updating id in {p}: {prefix} -> {updated}")
                            return m.group(1) + updated + m.group(3)
                    return m.group(0)
                new_fm = id_pattern.sub(id_repl, new_fm)

                # update slug if it starts with the numbered prefix
                def slug_repl(m):
                    prefix = m.group(2)
                    for old, new in repl_pairs:
                        if prefix.startswith(old):
                            updated = new + prefix[len(old):]
                            print(f"  Updating slug in {p}: {prefix} -> {updated}")
                            return m.group(1) + updated + m.group(3)
                    return m.group(0)
                new_fm = slug_pattern.sub(slug_repl, new_fm)

                if new_fm != fm:
                    text = text[:mfm.start(1)] + new_fm + text[mfm.end(1):]

            # generic token replacements (filenames, image folders, textual references)
            for pat, new in token_patterns:
                text, n = pat.subn(new, text)
                if n:
                    print(f"  Replaced {n} occurrences of token in {p} -> {pat.pattern} -> {new}")

            for pat, new in img_patterns:
                text, n = pat.subn(new, text)
                if n:
                    print(f"  Replaced {n} image-folder-like occurrences in {p} -> {pat.pattern} -> {new}")

            if text != orig_text:
                files_changed.append(p)
                if not dry_run:
                    p.write_text(text, encoding='utf-8')
    return files_changed

def update_image_folder_names(root: Path, major: int, insert_minor: int, dry_run=False):
    """
    Rename image folders like '8.5-Images' -> '8.6-Images' if they start with the numbering prefix.
    """
    pattern = re.compile(rf'^({major})\.(\d+)([_\-].*)?$')
    # collect matching directories
    dirs = []
    for p in root.rglob('*'):
        if p.is_dir():
            m = pattern.match(p.name)
            if m:
                minor = int(m.group(2))
                if minor >= insert_minor:
                    dirs.append((p, minor))
    dirs.sort(key=lambda x: x[1], reverse=True)
    ops = []
    for p, minor in dirs:
        new_name = compute_new_name(p.name, major, minor)
        new_path = p.with_name(new_name)
        ops.append((p, new_path))
    for old, new in ops:
        print(f"Image folder rename: {old} -> {new}")
    if not dry_run:
        for old, new in ops:
            if new.exists():
                raise FileExistsError(f"Target path already exists: {new}. Aborting to avoid data loss.")
        for old, new in ops:
            old.rename(new)
    return ops

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Insert a new minor unit into a Docusaurus docs tree by renumbering following units.")
    parser.add_argument('--docs_root', required=True, help="Path to the docs root (folder containing unit directories).")
    parser.add_argument('--major', required=True, type=int, help="Major unit number (e.g. 8).")
    parser.add_argument('--insert_minor', required=True, type=int, help="The minor index to insert at (e.g. 2 to insert 8.2). All existing minors >= this will be incremented.")
    parser.add_argument('--backup', default='True', choices=['True','False'], help="Make a backup copy of docs_root before changes (default True).")
    parser.add_argument('--dry-run', action='store_true', help="Show planned changes but don't modify files.")
    parser.add_argument('--sidebar_threshold', type=int, default=None, help="If set, any frontmatter sidebar_position >= this will be incremented. Defaults to (insert_minor + 1).")
    args = parser.parse_args()

    args.docs_root = Path(args.docs_root).expanduser().resolve()
    if not args.docs_root.exists():
        raise FileNotFoundError(f"Docs root not found: {args.docs_root}")

    args.backup = (args.backup == 'True')
    if args.sidebar_threshold is None:
        args.sidebar_threshold = args.insert_minor + 1  # heuristic: sidebar_position = minor + 1, so update >= this

    print("Settings:")
    print(f"  docs_root: {args.docs_root}")
    print(f"  major: {args.major}")
    print(f"  insert_minor: {args.insert_minor}")
    print(f"  backup: {args.backup}")
    print(f"  dry_run: {args.dry_run}")
    print(f"  sidebar_threshold: {args.sidebar_threshold}")
    print()

    if args.backup and not args.dry_run:
        backup_folder(args.docs_root)
    elif args.backup and args.dry_run:
        print("Dry-run: skipping actual backup copy (would create a backup if not dry-run).")

    # 1) Rename filesystem entries (directories and files)
    targets = find_targets(args.docs_root, args.major, args.insert_minor)
    if not targets:
        print("No filesystem entries found to rename (no matching '<major>.<minor>' patterns with minor >= insert_minor).")
    else:
        print(f"Found {len(targets)} filesystem entries to rename.")
        rename_filesystem(targets, dry_run=args.dry_run)

    # 2) Rename image folders more specifically (in case they were not caught)
    image_ops = update_image_folder_names(args.docs_root, args.major, args.insert_minor, dry_run=args.dry_run)

    # 3) Update markdown/mdx file contents
    changed_files = update_markdown_contents(args.docs_root, args.major, args.insert_minor, args.sidebar_threshold, dry_run=args.dry_run)
    print()
    print(f"Files changed: {len(changed_files)}")
    if args.dry_run:
        print("Dry-run complete. No files were modified.")
    else:
        print("Done. Please review changes (and commit or revert backup if needed).")

