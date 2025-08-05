# bio_hello

Demo: uppercase + filter length>=5, then aggregate stats

## Results Summary

- **Total Input Items**: 18
- **Total Kept Items**: 11
- **Filter Efficiency**: 61.1%

## Filtered Items (Length ≥ 5)

1. `PROTEIN_A`
2. `ENZYME_B`
3. `RECEPTOR_C`
4. `KINASE_D`
5. `GLUCOSE`
6. `GLYCOGEN`
7. `LACTATE`
8. `HEMOGLOBIN`
9. `INSULIN`
10. `COLLAGEN`
11. `KERATIN`

## Shard Details

| Shard | Input Size | Kept Size | Items |
|-------|------------|-----------|-------|
| 0 | 5 | 0 | *none* |
| 1 | 4 | 4 | `PROTEIN_A`, `ENZYME_B`, `RECEPTOR_C`, `KINASE_D` |
| 2 | 5 | 3 | `GLUCOSE`, `GLYCOGEN`, `LACTATE` |
| 3 | 4 | 4 | `HEMOGLOBIN`, `INSULIN`, `COLLAGEN`, `KERATIN` |

## Raw JSON Data

```json
{
  "total_input": 18,
  "total_kept": 11,
  "kept": [
    "PROTEIN_A",
    "ENZYME_B",
    "RECEPTOR_C",
    "KINASE_D",
    "GLUCOSE",
    "GLYCOGEN",
    "LACTATE",
    "HEMOGLOBIN",
    "INSULIN",
    "COLLAGEN",
    "KERATIN"
  ],
  "shards": [
    {
      "input_size": 5,
      "kept_size": 0,
      "kept": []
    },
    {
      "input_size": 4,
      "kept_size": 4,
      "kept": [
        "PROTEIN_A",
        "ENZYME_B",
        "RECEPTOR_C",
        "KINASE_D"
      ]
    },
    {
      "input_size": 5,
      "kept_size": 3,
      "kept": [
        "GLUCOSE",
        "GLYCOGEN",
        "LACTATE"
      ]
    },
    {
      "input_size": 4,
      "kept_size": 4,
      "kept": [
        "HEMOGLOBIN",
        "INSULIN",
        "COLLAGEN",
        "KERATIN"
      ]
    }
  ]
}
```
