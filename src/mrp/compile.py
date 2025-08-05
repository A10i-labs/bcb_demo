# compile.py
import sys
from pathlib import Path
import textwrap

TEMPLATES = {
    # Exact string → DSL YAML
    "run the biological data processing given the data": textwrap.dedent("""\
        job: bio_hello
        description: "Demo: uppercase + filter length>=5, then aggregate stats"
        map:
          agent: process_bio
          params:
            min_len: 5
          data:
            - ["ATCG","GCTA","TGCA","CGAT","AATG"]
            - ["PROTEIN_A","ENZYME_B","RECEPTOR_C","KINASE_D"]
            - ["ATP","NADH","GLUCOSE","GLYCOGEN","LACTATE"]
            - ["HEMOGLOBIN","INSULIN","COLLAGEN","KERATIN"]
        reduce:
          op: stats
        produce:
          op: print
        """),
    
    "save biological data processing to json": textwrap.dedent("""\
        job: bio_hello
        description: "Demo: uppercase + filter length>=5, then aggregate stats"
        map:
          agent: process_bio
          params:
            min_len: 5
          data:
            - ["ATCG","GCTA","TGCA","CGAT","AATG"]
            - ["PROTEIN_A","ENZYME_B","RECEPTOR_C","KINASE_D"]
            - ["ATP","NADH","GLUCOSE","GLYCOGEN","LACTATE"]
            - ["HEMOGLOBIN","INSULIN","COLLAGEN","KERATIN"]
        reduce:
          op: stats
        produce:
          op: save_json
          path: outputs/bio_results.json
        """),
    
    "save biological data processing to markdown": textwrap.dedent("""\
        job: bio_hello
        description: "Demo: uppercase + filter length>=5, then aggregate stats"
        map:
          agent: process_bio
          params:
            min_len: 5
          data:
            - ["ATCG","GCTA","TGCA","CGAT","AATG"]
            - ["PROTEIN_A","ENZYME_B","RECEPTOR_C","KINASE_D"]
            - ["ATP","NADH","GLUCOSE","GLYCOGEN","LACTATE"]
            - ["HEMOGLOBIN","INSULIN","COLLAGEN","KERATIN"]
        reduce:
          op: stats
        produce:
          op: save_markdown
          path: outputs/bio_results.md
        """)
}

USAGE = """\
Usage:
  python compile.py "<QUERY>" [OUTPUT_YML]

Available Queries:
  • "run the biological data processing given the data" - Print results to console
  • "save biological data processing to json" - Save results to JSON file
  • "save biological data processing to markdown" - Save results to Markdown file

Notes:
  • This is a stub translator: it just maps exact strings to DSL YAML.
  • Default output file is ./job.yml if none is provided.
"""

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    query = sys.argv[1].strip()
    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path("job.yml")

    if query not in TEMPLATES:
        print(f"[ERROR] No template for query: {query!r}")
        print("Hint: try the exact string above.")
        sys.exit(2)

    out_path.write_text(TEMPLATES[query], encoding="utf-8")
    print(f"[OK] Wrote DSL spec to: {out_path}")

if __name__ == "__main__":
    main()