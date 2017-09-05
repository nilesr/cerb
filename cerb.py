#!/usr/bin/env python
import glob, os, logging, json, subprocess
HTML = 0
PRINTING = 1
NONPRINTING = 2
PRE = 3
signatures = []
append = """
#define _GNU_SOURCE
#include <kore/kore.h>
#include <stdlib.h>
#include <stdio.h>
#ifndef _HAVE_CERB_APPEND
#define _HAVE_CERB_APPEND 1
#define Make_append(name, printer, type) void name(struct kore_buf* result, type new) { \\
    kore_buf_appendf(result, printer, new); \\
}
Make_append(append, "%s", char*);
Make_append(append_int, "%d", int);
Make_append(append_float, "%g", float);
Make_append(append_double, "%g", double);
#define Append(r, n) _Generic((n), char*: append, int: append_int, float: append_float, double: append_double, void*: /* hope for the best */ append)((r), (n))
void* _fetch_local(void*** all_locals, char* key) {
    if (!all_locals) return 0;
    int i = 0;
    while (1) {
        if (!all_locals[i]) return NULL;
        if (strcmp(all_locals[i][0], key) == 0) {
            return all_locals[i][1];
        }
        i++;
    }
}
#define Local(x) _fetch_local(_locals, #x)
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
    signature = "char* _cerb_" + os.path.basename(f[:-5]) + "(void*** _locals)"
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
locals_macro = """
// https://stackoverflow.com/questions/6707148/foreach-macro-on-macros-arguments
#define MAP_OUT
#define EVAL0(...) __VA_ARGS__
#define EVAL1(...) EVAL0 (EVAL0 (EVAL0 (__VA_ARGS__)))
#define EVAL2(...) EVAL1 (EVAL1 (EVAL1 (__VA_ARGS__)))
#define EVAL3(...) EVAL2 (EVAL2 (EVAL2 (__VA_ARGS__)))
#define EVAL4(...) EVAL3 (EVAL3 (EVAL3 (__VA_ARGS__)))
#define EVAL(...)  EVAL4 (EVAL4 (EVAL4 (__VA_ARGS__)))
#define MAP_END(...)
#define MAP_GET_END() 0, MAP_END
#define MAP_NEXT0(item, next, ...) next MAP_OUT
#define MAP_NEXT1(item, next) MAP_NEXT0 (item, next, 0)
#define MAP_NEXT(item, next)  MAP_NEXT1 (MAP_GET_END item, next)
//
#define MAP0(f, x, peek, ...) Make_second(x) MAP_NEXT (peek, MAP1) (f, peek, __VA_ARGS__)
#define MAP1(f, x, peek, ...) Make_pair(x) MAP_NEXT (peek, MAP0) (f, peek, __VA_ARGS__)
#define MAP(f, ...) EVAL (MAP1 (f, __VA_ARGS__, (), 0))

#define Make_second(x) x
#define Make_pair(x) (char*[]) x,

#define Cerb(view, ...) _cerb_##view ((void**[]){MAP(Make_pair, __VA_ARGS__), 0})
"""
open("src/views.h", "w").write("".join(signatures) + locals_macro)
