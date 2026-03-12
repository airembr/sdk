# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
from airembr.sdk.service.parser.eql.eql_parser import EQLParser

# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cases = {
        "Simple entity":
            'WHO Person(name: "Alice", age: 30)',

        "OR with return":
            'WHERE Pet(type: "cat") OR Pet(type: "dog") RETURN Pet',

        "AND with nested OR + return":
            'WHEN Person(age: 30) AND (Address(city: "Paris") OR Address(city: "Rome")) RETURN Person, Address',

        "NOT entity":
            'WHERE NOT Person(active: false) RETURN Person',

        "NOT compound expression":
            'WHERE NOT (Person(active: false) OR Person(banned: true))',

        "Dot notation properties":
            'Person(address.city: "Berlin", address.zip: 10115)',

        "Equals sign assignment":
            'Person(name = "Carol")',

        "Unquoted string value":
            'Person(status: active)',

        "Boolean values":
            'Person(active: true, verified: false)',

        "No clause, no return":
            'Person(name: "Bob")',

        "Deeply nested logic":
            'WHEN (A(x: 1) AND B(y: 2)) OR (C(z: 3) AND NOT D(w: 4)) RETURN A, C',

        "Multiple ANDs flattened":
            'WHERE A(x: 1) AND B(y: 2) AND C(z: 3)',

        "Multiple ORs flattened":
            'WHERE A(x.a: true) OR B(y.c.d: -2.23) OR C(z: 3)',
    }

    for label, query in cases.items():
        print(f"┌─ {label}")
        print(f"│  Input:  {query}")
        try:
            result = EQLParser().parse(query)
            print(type(result))
            print(f"│  Clause: {result.clause}")
            print(f"│  Query:  {result.query}")
            if result.returns:
                names = [e for e in result.returns]
                print(f"│  Return: {names}")
        except Exception as e:
            print(f"│  ERROR:  {e}")
        print()
