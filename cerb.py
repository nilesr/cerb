#!/usr/bin/env python
import glob, os, logging, json
HTML = 0
PRINTING = 1
NONPRINTING = 2
PRE = 3
signatures = []
append = """
#define _GNU_SOURCE
#include <kore/kore.h>
//#include <kore/http.h>
#include <stdlib.h>
#include <stdio.h>
#ifndef __HAVE_CERB_APPEND
#define __HAVE_CERB_APPEND
#define Make_append(name, printer, type) void name(struct kore_buf* result, type new) { \\
    kore_buf_appendf(result, printer, new); \\
}
Make_append(append, "%s", char*);
Make_append(append_int, "%d", int);
Make_append(append_float, "%g", float);
Make_append(append_double, "%g", double);
#define Append(r, n) _Generic((n), char*: append, int: append_int, float: append_float, double: append_double)((r), (n))
#endif
"""
if not os.path.exists("src/_views"): os.mkdir("src/_views")
for f in glob.glob("views/*.cerb"):
    outfile = "src/_" + f[:-5] + ".c"
    #if os.path.exists(outfile) and os.stat(f).st_mtime < os.stat(outfile).st_mtime:
        #logging.debug("File " + f + " is up to date, skipping")
        #continue
    pre = ""
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
        elif contents[i:i + 3] == "<%!":
            state = PRE
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
    result = signature + "{struct kore_buf* __result = kore_buf_alloc(1024);"
    signature += ";"
    for token in tokens:
        if token[0] == HTML:
            result += "Append(__result, " + json.dumps(token[1]) + ");\n"
        elif token[0] == PRINTING:
            result += "Append(__result, " + token[1] + ");\n"
        elif token[0] == NONPRINTING:
            result += token[1] + "\n"
        elif token[0] == PRE:
            pre += token[1] + "\n"
    result += "char* __result_str = kore_buf_stringify(__result, NULL); kore_buf_free(__result); return __result_str;}"
    result = append + pre + result;
    open(outfile, "w").write(result);
    signatures.append(signature);
open("src/views.h", "w").write("".join(signatures))
