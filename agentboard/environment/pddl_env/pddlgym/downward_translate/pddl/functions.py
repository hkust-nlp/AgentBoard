class Function:
    def __init__(self, name, arguments, type_name):
        self.name = name
        self.arguments = arguments
        if type_name != "number":
            raise SystemExit("Error: object fluents not supported\n" +
                             "(function %s has type %s)" % (name, type_name))
        self.type_name = type_name

    def __str__(self):
        result = "%s(%s)" % (self.name, ", ".join(map(str, self.arguments)))
        if self.type_name:
            result += ": %s" % self.type_name
        return result
