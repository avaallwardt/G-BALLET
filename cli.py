# Run the analysis from the terminal, like balletanalysis.py did:
#   python3 cli.py tori-arabesque.jpg

import sys

from analysis import analyze

if len(sys.argv) < 2:
    print("usage: python3 cli.py <photo>")
    sys.exit(1)

for path in sys.argv[1:]:
    result = analyze(path)
    print(f"\n=== {path} ===")
    if not result["is_arabesque"]:
        print(result["message"])
        continue
    print(result["summary"]["working_leg"])
    print(result["summary"]["arm_position"])
    print(result["summary"]["count"])
    for element in result["elements"]:
        print(f"\n{element['title']}")
        for c in element["constraints"]:
            feature = f"  [{c['feature']}]" if c["feature"] else ""
            print(f"  - {c['constraint']}: {c['score_label']}{feature}")
            print(f"      {c['feedback']}")
            for label, value in c["geometry"]["math"]:
                print(f"        {label}: {value}")
