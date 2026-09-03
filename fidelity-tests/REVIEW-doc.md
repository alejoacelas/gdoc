# gdt REVIEW doc

Standalone Google Doc for manual review: one section per fixture, linking the frozen fixture
and, per run, the edit requested and the edited copy.

url: https://docs.google.com/document/d/1Pp6LLKYos97X0uhxQHfVJn5ER2J6vJ3YUa_xF_yD6XM/edit?usp=drivesdk

Regenerate and push after new runs:

```
bin/gdt-review && gdoc write --force --quiet --account $A https://docs.google.com/document/d/1Pp6LLKYos97X0uhxQHfVJn5ER2J6vJ3YUa_xF_yD6XM/edit?usp=drivesdk REVIEW.md
```
