#!/usr/bin/env python3

"""
This file is part of the LC framework for synthesizing high-speed parallel lossless and error-bounded lossy data compression and decompression algorithms for CPUs and GPUs.

BSD 3-Clause License

Copyright (c) 2021-2024, Noushin Azami, Alex Fallin, Brandon Burtchell, Andrew Rodriguez, Benila Jerald, Yiqian Liu, and Martin Burtscher
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

URL: The latest version of this code is available at https://github.com/burtscher/LC-framework.

Sponsor: This code is based upon work supported by the U.S. Department of Energy, Office of Science, Office of Advanced Scientific Research (ASCR), under contract DE-SC0022223.
"""

import re
import glob, os
from pathlib import Path
from os.path import exists
import math
import shutil
import sys

dir = os.path.dirname(os.path.abspath(__file__))
# read available components
cfiles = next(os.walk(os.path.join(dir, 'components')))[2]
cpucomps = []
for f in cfiles:
  if f.startswith("h_"):
    cpucomps.append(f[:-2])
cpucomps.sort()

# read available preprocessors
pfiles = next(os.walk(os.path.join(dir, 'preprocessors')))[2]
cpupres = []
for f in pfiles:
  if f.startswith("h_"):
    cpupres.append(f[:-2])
cpupres.sort()

if len(sys.argv) != 3:
    print("Usage: {} \"[preprocessor_name ...]\" \"component_name [component_name ...]\"".format(sys.argv[0]))
    print("\nAvailable components are:")
    for c in cpucomps:
        print(c[2:], end = ' ')
    print("\n\nAvailable preprocessors are: ")
    for p in cpupres:
        print(p[2:], end = ' ')
    print("\n\n")
    sys.exit()
else:
    # Extract preprocessor names enclosed in double quotes
    preprocessor_names_str = sys.argv[1].strip('"')
    preprocessor_names = preprocessor_names_str.split()
    component_names_str = sys.argv[2].strip('"')
    component_names = component_names_str.split()
preprocessor_params = {}
pattern = r'\(([^)]+)\)'

# Iterate through preprocessor names
for name in preprocessor_names:
    match = re.search(pattern, name)
    if match:
        values = match.group(1).split(',')
        paramc = len(values)
        paramv = values
    else:
        paramc = 0
        paramv = []
    preprocessor_params[name] = {"paramc": paramc, "paramv": paramv}
#component_names = [arg.strip('"') for arg in sys.argv[2:]]

# generate lc framework
shutil.copyfile(os.path.join(dir, 'compressor-framework.cpp'), os.path.join(dir, 'compressor-standalone.cpp'))
shutil.copyfile(os.path.join(dir, 'decompressor-framework.cpp'), os.path.join(dir, 'decompressor-standalone.cpp'))

comp_list = []
for f in component_names:
  comp_list.append("h_" + f)

pre_list = []
for preprocessor in preprocessor_params.keys():
    preprocessor_name = re.sub(r'\(.*\)', '', preprocessor).strip()
    pre_list.append("h_" + preprocessor_name)

# check if user components exist in component list
for f in comp_list:
  if f not in cpucomps:
    print(f, ": Component does not exist. Try again.")
    quit()

# check if user preprocessor exists in preprocessor list
for f in pre_list:
    if f not in cpupres:
        print(f, "Preprocessor does nor exist. Try again.")
        quit()

# find unique comp names
comp_uni = []
for x in comp_list:
  if x not in comp_uni:
    comp_uni.append(x)

# find unique pre names
pre_uni = []
for x in pre_list:
  if x not in pre_uni:
    pre_uni.append(x)

# update include list
with open(os.path.join(dir, "compressor-standalone.cpp"), "r+") as f:
  contents = f.read()
  m = re.search(r"##include-beg##[\s\S]*##include-end##", contents)
  str_to_add = ''
  for c in pre_uni:
    str_to_add += "#include \"preprocessors/" + str(c) + ".h\"\n"
  for c in comp_uni:
    str_to_add += "#include \"components/" + str(c) + ".h\"\n"

  contents = contents[:m.span()[0]] + "##include-beg##*/\n" + str_to_add + "/*##include-end##" + contents[m.span()[1]:]
  f.seek(0)
  f.truncate()
  f.write(contents)

with open(os.path.join(dir, "decompressor-standalone.cpp"), "r+") as f:
  contents = f.read()
  m = re.search(r"##include-beg##[\s\S]*##include-end##", contents)
  str_to_add = ''
  for c in pre_uni:
    str_to_add += "#include \"preprocessors/" + str(c) + ".h\"\n"
  for c in comp_uni:
    str_to_add += "#include \"components/" + str(c) + ".h\"\n"
  contents = contents[:m.span()[0]] + "##include-beg##*/\n" + str_to_add + "/*##include-end##" + contents[m.span()[1]:]
  f.seek(0)
  f.truncate()
  f.write(contents)

# update print
with open(os.path.join(dir, "compressor-standalone.cpp"), "r+") as f:
  contents = f.read()
  m = re.search(r"##print-beg##[\s\S]*##print-end##", contents)
  str_to_add = '  printf(\"CPU LC 1.2 Algorithm:'
  for c in pre_uni:
      str_to_add += " " + str(c[2:])
  for c in comp_uni:
      str_to_add += " " + str(c[2:])
  str_to_add += "\\n\");\n"

  contents = contents[:m.span()[0]] + "##print-beg##*/\n" + str_to_add + "/*##print-end##" + contents[m.span()[1]:]
  f.seek(0)
  f.truncate()
  f.write(contents)

with open(os.path.join(dir, "decompressor-standalone.cpp"), "r+") as f:
  contents = f.read()
  m = re.search(r"##print-beg##[\s\S]*##print-end##", contents)
  str_to_add = '  printf(\"CPU LC 1.2 Algorithm:'
  for c in pre_uni:
      str_to_add += " " + str(c[2:])
  for c in comp_uni:
      str_to_add += " " + str(c[2:])
  str_to_add += "\\n\");\n"
  contents = contents[:m.span()[0]] + "##print-beg##*/\n" + str_to_add + "/*##print-end##" + contents[m.span()[1]:]
  f.seek(0)
  f.truncate()
  f.write(contents)

# update comp encoder
with open(os.path.join(dir, "compressor-standalone.cpp"), "r+") as f:
  contents = f.read()
  m = re.search(r"##comp-encoder-beg##[\s\S]*##comp-encoder-end##", contents)
  str_to_add = ''
  for c in comp_list:
    c = c[2:]
    str_to_add += "    if (good) {\n      std::swap(in, out);\n      good = h_" + str(c) + "(csize, in, out);\n    }\n"
  contents = contents[:m.span()[0]] + "##comp-encoder-beg##*/\n" + str_to_add + "    /*##comp-encoder-end##" + contents[m.span()[1]:]
  f.seek(0)
  f.truncate()
  f.write(contents)

# update pre encoder
with open(os.path.join(dir, "compressor-standalone.cpp"), "r+") as f:
    contents = f.read()
    m = re.search(r"##pre-encoder-beg##[\s\S]*##pre-encoder-end##", contents)
    str_to_add = ''
    first_iteration = True
    for d in preprocessor_params.keys():
        preprocessor_params_c = preprocessor_params[d]
        paramc = preprocessor_params_c["paramc"]
        paramv = preprocessor_params_c["paramv"]
        c = re.sub(r'\(.*\)', '', d).strip()
        if first_iteration:
          params = "double paramv[] = {" + ", ".join(map(str, paramv)) + "};"
          first_iteration = False
        else:
          params = "paramv[] = {" + ", ".join(map(str, paramv)) + "};"
        str_to_add += f"  {params}\n"
        str_to_add += f"  h_{c}(hpreencsize, hpreencdata, {paramc}, paramv);\n"

    contents = contents[:m.span()[0]] + "##pre-encoder-beg##*/\n" + str_to_add + "  /*##pre-encoder-end##" + contents[m.span()[1]:]
    f.seek(0)
    f.truncate()
    f.write(contents)

comp_list.reverse()

# update pre decoder
with open(os.path.join(dir, "decompressor-standalone.cpp"), "r+") as f:
    contents = f.read()
    m = re.search(r"##pre-decoder-beg##[\s\S]*##pre-decoder-end##", contents)
    str_to_add = ''
    first_iteration = True
    for d in reversed(preprocessor_params.keys()):
        preprocessor_params_c = preprocessor_params[d]
        paramc = preprocessor_params_c["paramc"]
        paramv = preprocessor_params_c["paramv"]
        c = re.sub(r'\(.*\)', '', d).strip()
        if first_iteration:
          params = "double paramv[] = {" + ", ".join(map(str, paramv)) + "};"
          first_iteration = False
        else:
          params = "paramv[] = {" + ", ".join(map(str, paramv)) + "};"
        str_to_add += f"  {params}\n"
        str_to_add += f"  h_i{c}(hdecsize, hdecoded, {paramc}, paramv);\n"

    contents = contents[:m.span()[0]] + "##pre-decoder-beg##*/\n" + str_to_add + "  /*##pre-decoder-end##" + contents[m.span()[1]:]
    f.seek(0)
    f.truncate()
    f.write(contents)

# update comp decoder
with open(os.path.join(dir, "decompressor-standalone.cpp"), "r+") as f:
  contents = f.read()
  m = re.search(r"##comp-decoder-beg##[\s\S]*##comp-decoder-end##", contents)
  str_to_add = ''
  for c in comp_list:
    c = c[2:]
    str_to_add += "      std::swap(in, out);\n      h_i" + str(c) + "(csize, in, out);\n"
  contents = contents[:m.span()[0]] + "##comp-decoder-beg##*/\n" + str_to_add + "      /*##comp-decoder-end##" + contents[m.span()[1]:]
  f.seek(0)
  f.truncate()
  f.write(contents)

# Get rid of tags
enc_file_path = os.path.join(dir, "compressor-standalone.cpp")
with open(enc_file_path, "r") as file:
    cpp_code = file.readlines()
pattern = r'/\*##[^#]+##\*/'
cpp_code = [line for line in cpp_code if not re.match(pattern, line.strip())]
with open(enc_file_path, "w") as file:
    file.write("".join(cpp_code))

dec_file_path = os.path.join(dir, "decompressor-standalone.cpp")
with open(dec_file_path, "r") as file:
    cpp_code = file.readlines()
pattern = r'/\*##[^#]+##\*/'
cpp_code = [line for line in cpp_code if not re.match(pattern, line.strip())]
with open(dec_file_path, "w") as file:
    file.write("".join(cpp_code))
