import glob, os, logging, json
HTML = 0
PRINTING = 1
NONPRINTING = 2
signatures = []
append = """
#define _GNU_SOURCE
#include <stdlib.h>
#include <stdio.h>
#ifndef __HAVE_CERB_APPEND
#define __HAVE_CERB_APPEND
void append(char** result, char* new) {
    char* old = *result;
    asprintf(result, "%s%s", (*result ? *result : ""), new);
    if (old) free(old);
}
#endif
"""
if not os.path.exists("src/_views"): os.mkdir("src/_views")
for f in glob.glob("views/*.cerb"):
    outfile = "src/_" + f[:-5] + ".c"
    #if os.path.exists(outfile) and os.stat(f).st_mtime < os.stat(outfile).st_mtime:
        #logging.debug("File " + f + " is up to date, skipping")
        #continue
    contents = open(f).read()
    state = HTML
    tokens = [[HTML, ""]]
    i = 0
    while i < len(contents):
        if contents[i:i + 2] == "%>":
            state = HTML
            tokens.append([state, ""])
            i += 1
        elif contents[i:i + 3] == "<%=":
            state = PRINTING
            tokens.append([state, ""])
            i += 2
        elif contents[i:i + 2] == "<%":
            state = NONPRINTING
            tokens.append([state, ""])
            i += 1
        else:
            tokens[-1][1] += contents[i]
        i += 1
    signature = "char* cerb_" + os.path.basename(f[:-5]) + "(void** locals)"
    result = append + signature + "{"
    signature += ";"
    result += "char* __temp; char* result = NULL;"
    for token in tokens:
        if token[0] == HTML:
            result += "append(&result, " + json.dumps(token[1]) + ");"
        elif token[0] == PRINTING:
            result += "__temp = " + token[1] + ";"
            result += "append(&result, __temp);"
        else:
            result += token[1]
    result += "return result;}"
    open(outfile, "w").write(result);
    signatures.append(signature);
open("src/views.h", "w").write("".join(signatures))
