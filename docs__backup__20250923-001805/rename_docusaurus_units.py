#!/usr/bin/env python3
"""
rename_docusaurus_units_safe.py

Improved version of rename_docusaurus_units.py that avoids FileExistsError collisions
by performing a two-step rename:
  1) rename every matched path -> temporary unique name (so there are no conflicts)
  2) rename each temporary name -> final target name

Also performs checks to detect external collisions (final target exists but wasn't scheduled for rename).

Key changes vs previous script:
- Two-step rename with uuid-based temp suffix.
- Pre-check for conflicting final targets that are not part of the rename set.
- Clear dry-run mode that prints both temp and final planned moves.
- All filesystem renames happen BEFORE modifying markdown contents (safer).
- Improved ordering (rename deepest paths first for temp step).

Usage (example dry-run):
  python3 rename_docusaurus_units_safe.py --docs_root /path/to/docs --major 8 --insert_minor 2 --dry-run

CAUTION:
  Still strongly recommend running in a git-clean tree or having a backup.
"""

import argparse, shutil, time, uuid, os, sys, re
from pathlib import Path

def compute_new_name(old_name: str, major: int, minor: int):
    prefix = f"{major}.{minor}"
    new_prefix = f"{major}.{minor+1}"
    if old_name.startswith(prefix):
        return new_prefix + old_name[len(prefix):]
    return old_name

def find_targets(root: Path, major: int, insert_minor: int):
    pattern = re.compile(rf'^{re.escape(str(major))}\.(\d+)([.\-\w].*)?$')
    targets = []
    for p in root.rglob('*'):
        m = pattern.match(p.name)
        if m:
            minor = int(m.group(1))
            if minor >= insert_minor:
                targets.append((p, minor))
    # sort by path depth descending so deeper files/dirs are renamed before parents
    targets.sort(key=lambda x: (len(x[0].parts), str(x[0])), reverse=True)
    return targets

def plan_moves(targets, major, insert_minor):
    """
    Build mapping: original_path -> final_path
    """
    orig_to_final = {}
    for p, minor in targets:
        new_name = compute_new_name(p.name, major, minor)
        final = p.with_name(new_name)
        orig_to_final[p] = final
    return orig_to_final

def check_external_collisions(orig_to_final):
    """
    Ensure none of the final targets exist on disk unless they are part of the orig set.
    """
    originals = set(orig_to_final.keys())
    collisions = []
    for orig, final in orig_to_final.items():
        if final.exists() and final not in originals:
            collisions.append((orig, final))
    return collisions

def two_step_rename(orig_to_final, dry_run=False):
    """
    1) Rename each original -> temp name
    2) Rename each temp -> final
    Return list of performed ops
    """
    ts = time.strftime("%Y%m%d-%H%M%S")
    temp_map = {}  # orig -> temp
    ops = []

    # Step A: create temp names
    for orig in sorted(orig_to_final.keys(), key=lambda p: (len(p.parts), str(p)), reverse=True):
        parent = orig.parent
        suffix = f".__tmp__{ts}__{uuid.uuid4().hex}"
        temp_name = orig.name + suffix
        temp_path = parent / temp_name
        temp_map[orig] = temp_path

    # Show planned temp renames
    print("Planned temporary renames (original -> temp):")
    for orig, temp in temp_map.items():
        print(f"  {orig} -> {temp}")

    if dry_run:
        print("Dry-run: skipping filesystem changes (temp renames).")
    else:
        # ensure no temp path already exists (very unlikely) and perform actual temp renames
        for orig, temp in temp_map.items():
            if temp.exists():
                raise FileExistsError(f"Temporary path already exists: {temp}")
        for orig, temp in temp_map.items():
            print(f"Temporarily renaming: {orig} -> {temp}")
            orig.rename(temp)

    # Step B: rename temp -> final
    final_ops = []
    print("\nPlanned final renames (temp -> final):")
    for orig, final in orig_to_final.items():
        temp = temp_map[orig]
        print(f"  {temp} -> {final}")
        final_ops.append((temp, final))

    if dry_run:
        print("Dry-run: skipping final renames.")
        return []

    # perform final renames (ensure no unexpected final exists now)
    for temp, final in final_ops:
        if final.exists():
            # This should not happen because we moved originals to temp, but check anyway
            raise FileExistsError(f"Final path unexpectedly exists: {final}. Aborting to avoid data loss.")
    for temp, final in final_ops:
        print(f"Final rename: {temp} -> {final}")
        # ensure final parent exists
        final.parent.mkdir(parents=True, exist_ok=True)
        temp.rename(final)
    return final_ops

def update_markdown_contents(root: Path, orig_to_final: dict, major: int, insert_minor: int, sidebar_threshold: int, dry_run=False):
    md_exts = {'.md', '.mdx', '.markdown', '.mdown'}
    # Build repl_pairs deterministically from the planned filesystem renames (orig_to_final)
    # so markdown updates exactly match what was renamed on disk.
    pattern_name = re.compile(rf'^{re.escape(str(major))}\.(\d+)')
    minor_set = set()
    for orig_path in orig_to_final.keys():
        m = pattern_name.match(orig_path.name)
        if m:
            minor_set.add(int(m.group(1)))
    minors_to_change = sorted([m for m in minor_set if m >= insert_minor], reverse=True)
    repl_pairs = [(f"{major}.{m}", f"{major}.{m+1}") for m in minors_to_change]  

    token_patterns = [(re.compile(rf'(?<!\d){re.escape(old)}(?!\d)'), new) for old, new in repl_pairs]
    img_patterns = [(re.compile(re.escape(old) + r'(?=[_\-\/])'), new) for old, new in repl_pairs]

    fm_pattern = re.compile(r'^---\s*\n(.*?\n?)^---\s*\n', re.DOTALL | re.MULTILINE)
    sidebar_pattern = re.compile(r'(^\s*sidebar_position\s*:\s*)(\d+)\s*$', re.MULTILINE)
    id_pattern = re.compile(r'(^\s*id\s*:\s*[\'"]?)([^\'"\n]+)([\'"]?\s*$)', re.MULTILINE)
    slug_pattern = re.compile(r'(^\s*slug\s*:\s*[\'"]?)([^\'"\n]+)([\'"]?\s*$)', re.MULTILINE)

    files_changed = []
    for p in root.rglob('*'):
        if p.suffix.lower() in md_exts:
            try:
                text = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            orig_text = text
            mfm = fm_pattern.search(text)
            if mfm:
                fm = mfm.group(1)
                new_fm = fm
                def sidebar_repl(m):
                    val = int(m.group(2))
                    if val >= sidebar_threshold:
                        newval = val # + 1
                        # print(f"  Updating sidebar_position in {p}: {val} -> {newval}")
                        return m.group(1) + str(newval)
                    return m.group(0)
                new_fm = sidebar_pattern.sub(sidebar_repl, new_fm)

                def id_repl(m):
                    prefix = m.group(2)
                    for old, new in repl_pairs:
                        if prefix.startswith(old):
                            updated = new + prefix[len(old):]
                            print(f"  Updating id in {p}: {prefix} -> {updated}")
                            return m.group(1) + updated + m.group(3)
                    return m.group(0)
                new_fm = id_pattern.sub(id_repl, new_fm)

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
                    # ensure the frontmatter block ends with a newline so the closing '---' stays on its own line
                    if not new_fm.endswith('\n'):
                        new_fm += '\n'
                    text = text[:mfm.start(1)] + new_fm + text[mfm.end(1):]


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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--docs_root', required=True)
    parser.add_argument('--major', required=True, type=int)
    parser.add_argument('--insert_minor', required=True, type=int)
    parser.add_argument('--backup', default='True', choices=['True','False'])
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--sidebar_threshold', type=int, default=None)
    args = parser.parse_args()

    docs_root = Path(args.docs_root).expanduser().resolve()
    if not docs_root.exists():
        print("Docs root missing:", docs_root); sys.exit(1)
    backup = (args.backup == 'True')
    if args.sidebar_threshold is None:
        sidebar_threshold = args.insert_minor + 1
    else:
        sidebar_threshold = args.sidebar_threshold

    print("Settings:")
    print(f"  docs_root: {docs_root}")
    print(f"  major: {args.major}, insert_minor: {args.insert_minor}")
    print(f"  backup: {backup}, dry_run: {args.dry_run}")
    print(f"  sidebar_threshold: {sidebar_threshold}")

    if backup and not args.dry_run:
        ts = time.strftime("%Y%m%d-%H%M%S")
        backup_path = docs_root.parent / (docs_root.name + "__backup__" + ts)
        print("Creating backup:", backup_path)
        shutil.copytree(docs_root, backup_path)

    targets = find_targets(docs_root, args.major, args.insert_minor)
    if not targets:
        print("No matching targets to rename.")
        return
    print(f"Found {len(targets)} matching paths to rename. Example: {targets[0][0]}")

    orig_to_final = plan_moves(targets, args.major, args.insert_minor)
    collisions = check_external_collisions(orig_to_final)
    if collisions:
        print("ERROR: Found external collisions (final path exists but is not part of the rename set):")
        for orig, final in collisions:
            print(f"  {orig} -> {final} (conflict)")
        print("Resolve these conflicts or move the conflicting items out of the way, then rerun.")
        sys.exit(2)

    # Dry-run prints planned operations without changing filesystem
    if args.dry_run:
        print("\nDry-run planned final mapping (original -> final):")
        for orig, final in orig_to_final.items():
            print(f"  {orig} -> {final}")
        print("\nNo files modified during dry-run.")
        # still show planned temp & final sequences via two_step_rename(dry_run=True)
        two_step_rename(orig_to_final, dry_run=True)
        print("\nPlanned content edits (markdown):")
        changed_files = update_markdown_contents(docs_root, orig_to_final, args.major, args.insert_minor, sidebar_threshold, dry_run=True)
        print(f"  Markdown files that would be changed: {len(changed_files)}")
        return

    # Perform two-step rename
    two_step_rename(orig_to_final, dry_run=False)

    # After renames, update markdown files to reflect new numbering
    changed_files = update_markdown_contents(docs_root, orig_to_final, args.major, args.insert_minor, sidebar_threshold, dry_run=False)
    print(f"Completed. Markdown files modified: {len(changed_files)}")

if __name__ == '__main__':
    main()