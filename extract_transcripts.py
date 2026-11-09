"""
Find every *_TRANSCRIPT.csv inside the "conversations" folder on the Desktop
and copy them, one file each, into ~/Downloads/all_csv_nlp.

Works with both zip files (300_P.zip) and folders that are already unzipped.
Only the transcript is pulled out of each zip, so the large audio and video
files are never written to disk.

Usage:
    python extract_transcripts.py
"""
import shutil
import zipfile
from pathlib import Path

SOURCE_DIR = Path.home() / "Desktop" / "conversations"
OUT_DIR = Path.home() / "Downloads" / "all_csv_nlp"
SUFFIX = "_TRANSCRIPT.csv"


def is_transcript(name):
    base = Path(name).name
    # skip macOS junk such as __MACOSX/._300_TRANSCRIPT.csv
    return base.endswith(SUFFIX) and not base.startswith("._") and "__MACOSX" not in name


def main():
    if not SOURCE_DIR.is_dir():
        raise SystemExit(f"Folder not found: {SOURCE_DIR}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    saved, problems = set(), []

    # 1) zip files
    zips = sorted(SOURCE_DIR.rglob("*.zip"))
    print(f"Found {len(zips)} zip files.")
    for z in zips:
        try:
            with zipfile.ZipFile(z) as zf:
                members = [m for m in zf.namelist() if is_transcript(m)]
                if not members:
                    problems.append(f"{z.name}: no {SUFFIX} inside")
                    continue
                for m in members:
                    target = OUT_DIR / Path(m).name
                    with zf.open(m) as src, open(target, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    saved.add(target.name)
        except zipfile.BadZipFile:
            problems.append(f"{z.name}: not a valid zip (incomplete download?)")

    # 2) folders that are already unzipped
    for f in sorted(SOURCE_DIR.rglob(f"*{SUFFIX}")):
        if is_transcript(str(f)):
            shutil.copy2(f, OUT_DIR / f.name)
            saved.add(f.name)

    print(f"\nDone. {len(saved)} transcripts saved in: {OUT_DIR}")
    if problems:
        print("\nProblems:")
        for p in problems:
            print("  -", p)


if __name__ == "__main__":
    main()
