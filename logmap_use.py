import subprocess

cmd = [
    "java",
    "--add-opens", "java.base/java.lang=ALL-UNNAMED",
    "-Xms500m",
    "-Xmx10g",
    "-DentityExpansionLimit=100000000",
    "-jar", "/mnt/c/Users/dconde/Desktop/Evol_Align/deeptontoenv/Lib/site-packages/deeponto/align/logmap/logmap-matcher-4.0.jar",
    "MATCHER",
    "file:///mnt/c/Users/dconde/Desktop/Evol_Align/animl_manual.owl",
    "file:///mnt/c/Users/dconde/Desktop/Evol_Align/skeleton_ontology_1.ttl",
    "/mnt/c/Users/dconde/Desktop/Evol_Align/output_logmap/",
    "true",
]

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

stdout, stderr = process.communicate()

print(stdout)
print(stderr)
