from io import StringIO

import pddl
from pddl_to_prolog import Rule, PrologProgram

def test_normalization():
    prog = PrologProgram()
    prog.add_fact(pddl.Atom("at", ["foo", "bar"]))
    prog.add_fact(pddl.Atom("truck", ["bollerwagen"]))
    prog.add_fact(pddl.Atom("truck", ["segway"]))
    prog.add_rule(Rule([pddl.Atom("truck", ["?X"])], pddl.Atom("at", ["?X", "?Y"])))
    prog.add_rule(Rule([pddl.Atom("truck", ["X"]), pddl.Atom("location", ["?Y"])],
                  pddl.Atom("at", ["?X", "?Y"])))
    prog.add_rule(Rule([pddl.Atom("truck", ["?X"]), pddl.Atom("location", ["?Y"])],
                  pddl.Atom("at", ["?X", "?X"])))
    prog.add_rule(Rule([pddl.Atom("p", ["?Y", "?Z", "?Y", "?Z"])],
                  pddl.Atom("q", ["?Y", "?Y"])))
    prog.add_rule(Rule([], pddl.Atom("foo", [])))
    prog.add_rule(Rule([], pddl.Atom("bar", ["X"])))
    prog.normalize()
    output = StringIO()
    prog.dump(file=output)
    sorted_output = "\n".join(sorted(output.getvalue().splitlines()))
    assert sorted_output == """\
Atom @object(bar).
Atom @object(bollerwagen).
Atom @object(foo).
Atom @object(segway).
Atom at(foo, bar).
Atom bar(X).
Atom foo().
Atom truck(bollerwagen).
Atom truck(segway).
none Atom at(?X, ?X@0) :- Atom truck(?X), Atom location(?Y), Atom =(?X, ?X@0).
none Atom at(?X, ?Y) :- Atom truck(?X), Atom @object(?Y).
none Atom at(?X, ?Y) :- Atom truck(X), Atom location(?Y), Atom @object(?X).
none Atom q(?Y, ?Y@0) :- Atom p(?Y, ?Z, ?Y, ?Z), Atom =(?Y, ?Y@0), Atom =(?Y, ?Y@1), Atom =(?Z, ?Z@2)."""
