import re

# Regular expressions for tokenizing and binary label matching
token_pattern = re.compile(r"(\(|\)|[^()\s]+)")
binary_label_pattern = re.compile(r"(.+)\+(.+)'")


class TreeNode:
    def __init__(self, name, descendants):
        self.name = name
        self.descendants = descendants

    def __str__(self):
        if self.descendants:
            return '(%s %s)' % (self.name, ' '.join(str(descendant) for descendant in self.descendants))
        else:
            return self.name

    def __repr__(self):
        return 'TreeNode(%r, %r)' % (self.name, self.descendants)

    def __eq__(self, other):
        return self.name == other.name and self.descendants == other.descendants

    def __iter__(self):
        return TreeNodeIterator(self)

    def get_terminals(self):
        return [node for node in self if node.is_leaf()]

    def get_preterminals(self):
        return [node for node in self if node.is_preterminal()]

    def get_nonterminals(self):
        return [node for node in self if node.is_nonterminal()]

    def is_nonterminal(self):
        return len(self.descendants) > 0

    def is_preterminal(self):
        return len(self.descendants) == 1 and self.descendants[0].is_leaf()

    def is_leaf(self):
        return self.descendants == []

    def is_binary(self):
        return binary_label_pattern.fullmatch(self.name)

    def get_nonterminals_excluding_binary(self):
        return [node for node in BinaryTreeNodeIterator(self) if node.is_nonterminal()]


class TreeNodeIterator:
    def __init__(self, node):
        self.stack = [node]

    def __iter__(self):
        return self

    def __next__(self):
        if not self.stack:
            raise StopIteration
        current_node = self.stack.pop()
        for child in reversed(current_node.descendants):
            self.stack.append(child)
        return current_node


class BinaryTreeNodeIterator:
    def __init__(self, node):
        self.stack = [node]

    def __iter__(self):
        return self

    def __next__(self):
        if not self.stack:
            raise StopIteration
        current_node = self.stack.pop()
        for child in reversed(current_node.descendants):
            if child.is_binary():
                self.stack.extend(child.descendants)
            else:
                self.stack.append(child)
        return current_node


class ParsingError(Exception):
    pass


def create_node(token, token_stream):
    if token == ')':
        raise ParsingError
    elif token == '(':
        return TreeNode(next(token_stream), create_nodes(token_stream))
    else:
        return TreeNode(token, [])


def create_nodes(token_stream):
    nodes = []
    for token in token_stream:
        if token == ')':
            return nodes
        nodes.append(create_node(token, token_stream))
    raise ParsingError


def parse_input_string(input_string):
    if not input_string:
        raise ParsingError

    token_stream = iter(token_pattern.findall(input_string))
    result = create_node(next(token_stream), token_stream)
    try:
        next(token_stream)
    except StopIteration:
        return result
    else:
        raise ParsingError


class FileParser:
    def __init__(self, file):
        self.token_stream = Tokenize_input_file(file)

    def __iter__(self):
        return self

    def __next__(self):
        return create_node(next(self.token_stream), self.token_stream)


class WSJParser:
    def __init__(self, file):
        self.token_stream = Tokenize_input_file(file)

    def __iter__(self):
        return self

    def __next__(self):
        if next(self.token_stream) != '(':
            raise ParsingError
        nodes = []
        for token in self.token_stream:
            if token == ')':
                return nodes
            nodes.append(create_node(token, self.token_stream))
        raise StopIteration


class Tokenize_input_file:
    def __init__(self, file):
        self.file = file
        self.buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        while not self.buffer:
            self.buffer = re.findall(r'(\(|\)|[^()\s]+)', next(self.file))
        return self.buffer.pop(0)