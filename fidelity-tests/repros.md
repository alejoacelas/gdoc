# Repros

One gdoc command per entry that reproduces a known failure on a fixture, without an agent
and without judging. Rerun after every CLI change. Format:

```
## <fixture> — <one-line failure>   (<date>, <outcome>, <issue or "no issue">)
gdoc <command> --account $A <doc> ...
Expect: <what a fixed CLI does>. Observed: <what happened>.
```

(none yet)
