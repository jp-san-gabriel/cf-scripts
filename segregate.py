from os.path import join, exists, size
from os import mkdir
drive_names = {
    "1164": "IN133-1002",
    "1050": "IN11-120",
    "1083": "IN112-1001",
    "1734": "PS01-027",
    "1903": "SG001-1007",
    "4101": "UK001-0007",
}
# create the folder 'output' if it does not exist
if not exists('output'):
    mkdir('output')

# open the output files for writing and store them in a dictionary
out_files = {k: open(join('output', f"{v}.out"), "w") for k, v in drive_names.items()}

# open the bigtable.out file for reading
with open("col2_values_bigtable.out", "r") as file:
    # read each line and write them to the corresponding file
    for line in file:
        data = line.split('|')
        out_files[data[2]].write(line)
# close the output files
for file in out_files.values():
    file.close()
