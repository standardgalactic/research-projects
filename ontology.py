ONTOLOGY = {
    "dimensions":[
        {"name":"optionality","description":"Future relevance under uncertainty","polarity":"positive"},
        {"name":"derivability","description":"Can be reconstructed from axioms","polarity":"negative"},
        {"name":"generativity","description":"Spawns new hypotheses","polarity":"positive"},
        {"name":"actionability","description":"Changes decisions or outcomes","polarity":"positive"},
        {"name":"provenance_depth","description":"Historical lineage strength","polarity":"positive"},
        {"name":"compression_ratio","description":"Size after formal reduction","polarity":"negative"},
        {"name":"tension_index","description":"Unresolved paradoxes","polarity":"positive"},
        {"name":"leverage_potential","description":"Real-world impact magnitude","polarity":"positive"}
    ],
    "persona_projection":{
        "archivist":["optionality","provenance_depth"],
        "formalist":["derivability","compression_ratio"],
        "synthesist":["generativity","tension_index"],
        "strategist":["actionability","leverage_potential"]
    }
}
