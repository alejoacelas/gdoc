# transcript — rewrite-tab-after-ui-bullet (command track)

gdoc 0.21.0, account from config.yaml. No agent: the runner executed the fixture build and the
single command under test.

## Commands

```
fidelity-tests/write/v01/build.sh                                  → DOC=185pW… TAB=t.oe1hhddciuj0 (seed written; terminal paragraph 56–57 bulleted)
gdt capture DOC before/                                            → drive revision 10
gdoc write --account A --tab t.oe1hhddciuj0 DOC rewrite.md          → OK wrote "Repro"
gdt capture DOC after/                                             → drive revision 11
gdoc pull --account A DOC out.md                                   → every paragraph of the tab is "* "-prefixed
```

## Pulled tab after the write (verbatim)

```
# Repro

* # Rewritten heading

*   
* Plain paragraph after the heading.  
*   
* first bullet  
* second bullet  
*   
* Closing plain paragraph.  
*
```

Control, same session: with the terminal paragraph left plain (the state right after
`gdoc write --tab … seed.md`, before `createParagraphBullets`), the identical `write --tab
… rewrite.md` rendered correctly. The bullet on the terminal paragraph is the only difference.
