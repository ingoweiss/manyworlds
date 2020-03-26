class Scenario:

    def __init__(self, name, level=None, id=None):
        self.id = id
        self.name = name
        self.level = level
        self.children = []
        self.actions = []
        self.assertions = []
        self.parent = None
        self.given = False

    def is_root(self):
        return self.level == 0

    def add_child(self, child):
        self.children.append(child)
        child.set_parent(self)

    def add_action(self, action):
        self.actions.append(action)

    def add_assertion(self, assertion):
        self.assertions.append(assertion)

    def set_parent(self, parent):
        self.parent = parent

    def is_leaf(self):
        return len(self.children) == 0

    def mark_as_given(self):
        self.given = True

    def ancestors(self):
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.insert(0, parent)
            parent = parent.parent
        return ancestors

    def lineage(self):
        return self.ancestors() + [self]

    def long_name(self):
        return ' > '.join([s.name for s in self.lineage()])

    def steps(self):
        return sorted(self.actions + self.assertions, key=lambda s: s.id)