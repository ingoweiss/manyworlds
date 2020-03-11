class Scenario:
    
    def __init__(self, name, level=None, id=None):
        self.id = id
        self.name = name
        self.level = level
        self.children = []
        self.actions = []
        self.assertions = []
        self.parent = None

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
    