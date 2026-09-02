import json,sys
d=json.load(open(sys.argv[1]))
body=d.get("body") or d["tabs"][0]["documentTab"]["body"]
for el in body["content"]:
    p=el.get("paragraph")
    if not p: continue
    txt="".join(e.get("textRun",{}).get("content","") for e in p["elements"])
    if "Ana’s note" in txt:
        print("== PARA style:", p.get("paragraphStyle",{}).get("namedStyleType"))
        for e in p["elements"]:
            tr=e.get("textRun")
            if not tr: continue
            st={k:v for k,v in tr.get("textStyle",{}).items() if k in("bold","italic","link","underline")}
            print("   ", repr(tr["content"]), st)
