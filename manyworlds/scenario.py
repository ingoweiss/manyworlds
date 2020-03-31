'''Defines the Scenario Class'''
class Scenario:
    '''A BDD scenario'''

    def __init__(self, name, level=None, id=None):
        '''
        Init method for the Scenario Class

        Parameters:
        name (string): The name of the scenario
        level (integer): The indentation level of the scenario
        id (integer): The unique numeric ID of the scenario

        Returns:
        Instance of Scenario
        '''

        self.id = id
        self.name = name
        self.level = level
        self.children = []
        self.actions = []
        self.assertions = []
        self.parent = None
        self.given = False

    def is_root(self):
        '''Returns True if scenario is a root scenario, False otherwise'''
        return self.level == 0

    def add_child(self, child):
        '''Adds a scenario to the scenario's children

        Parameters:
        child (Scenario instance): The child scenario to be added
        '''
        self.children.append(child)
        child.set_parent(self)

    def add_action(self, action):
        '''Adds an action to the scenario's actions

        Parameters:
        action (Step instance): The action to be added
        '''
        self.actions.append(action)

    def add_assertion(self, assertion):
        '''Adds an assertion to the scenario's actions

        Parameters:
        assertion (Step instance): The assertion to be added
        '''
        self.assertions.append(assertion)

    def set_parent(self, parent):
        '''Makes a scenario the parent scenario of this scenario

        Parameters:
        parent (Scenario instance): The parent scenario
        '''
        self.parent = parent

    def is_leaf(self):
        '''Returns True if scenario is a leaf scenario, False otherwise'''
        return len(self.children) == 0

    def mark_as_given(self):
        '''Marks a scenario as given

        'Given' in this context means that the scenario's assertions have been run once already,
        so if the scenario is run as part of another scenario chain, it's assertions don't need
        to be re-run and it's actions are run as 'Given' steps.

        This is used in the 'relaxed' flattening mode
        '''
        self.given = True

    def ancestors(self):
        '''Returns the chain of the scenario's ancestor scenarios

        The first scenario in the list is the scenario's root scenario
        The last scenario in the list is the scenario's parent scenario

        Returns: List of scenarios
        '''
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.insert(0, parent)
            parent = parent.parent
        return ancestors

    def lineage(self):
        '''Returns the scenario's lineage of scenarios

        The first scenario in the list is the scenario's root scenario
        The last scenario in the list is the scenario itself

        Returns: List of scenarios
        '''
        return self.ancestors() + [self]

    def long_name(self):
        '''Returns the names of all scenarios in the scenario's lineage, joined by " > "'''
        return ' > '.join([s.name for s in self.lineage()])

    def steps(self):
        '''Returns all steps of the scenario (actions and assertions), sorted by ID'''
        return sorted(self.actions + self.assertions, key=lambda s: s.id)
