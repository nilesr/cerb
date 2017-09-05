#!/usr/bin/env python
import glob, os, logging, json, subprocess
HTML = 0
PRINTING = 1
NONPRINTING = 2
PRE = 3
signatures = []
append = """
#include "../views.h"
#ifndef _HAVE_CERB_APPEND
#define _HAVE_CERB_APPEND 1
#define _GNU_SOURCE
#include <kore/kore.h>
#include <stdlib.h>
#include <stdio.h>
#define Make_append(name, printer, type) void name(struct kore_buf* result, type new) { \\
    kore_buf_appendf(result, printer, new); \\
}
Make_append(append, "%s", char*);
Make_append(append_int, "%d", int);
Make_append(append_float, "%g", float);
Make_append(append_double, "%g", double);
#define Append(r, n) _Generic((n), char*: append, int: append_int, float: append_float, double: append_double, void*: /* hope for the best */ append)((r), (n))
void* _fetch_local(cerb_local* all_locals, char* key) {
    if (!all_locals) return 0;
    int i = 0;
    while (1) {
        if (!all_locals[i].key) return 0;
        if (strcmp(all_locals[i].key, key) == 0) {
            return all_locals[i].value;
        }
        i++;
    }
}
#undef Local
#define Local(x) _fetch_local(_locals, #x)
#endif
"""
locals_macro = """
typedef struct cerb_local {
    char* key;
    void* value;
} cerb_local;
#define Cerb(view, ...) _cerb_##view ((cerb_local[]){__VA_ARGS__, (cerb_local){0, 0}})
#define Local(a, b) (cerb_local) {#a, b}
"""
if not os.path.exists("src/_views"): os.mkdir("src/_views")
open("src/views.h", "w").write(locals_macro)
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
    signature = "char* _cerb_" + os.path.basename(f[:-5]) + "(cerb_local* _locals)"
    result = signature + "{struct kore_buf* _result = kore_buf_alloc(1024);"
    signature += ";"
    for token in tokens:
        if token[0] == HTML:
            result += "Append(_result, " + json.dumps(token[1]) + ");\n"
        elif token[0] == PRINTING:
            result += "Append(_result, " + token[1] + ");\n"
        elif token[0] == NONPRINTING:
            result += token[1] + "\n"
        elif token[0] == PRE:
            pre += token[1] + "\n"
    result += "char* _result_str = kore_buf_stringify(_result, NULL); kore_buf_free(_result); return _result_str;}"
    result = append + pre + result;
    open(outfile, "w").write(result);
    subprocess.check_call(["gcc", "-fsyntax-only", outfile])
    signatures.append(signature);
open("src/views.h", "a").write("".join(signatures))
