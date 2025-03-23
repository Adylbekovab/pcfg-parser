import argparse
import math
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from tree import parse_input_string, TreeNode

# Global data structures
rule_counts = defaultdict(int)
rule_totals = defaultdict(int)
left_counts = defaultdict(int)
right_counts = defaultdict(int)
word_counts = defaultdict(int)

grammar_rules = set()
vocabulary = set()
terminal_usage = defaultdict(int)


def train_model(args):
    with open(args.trees) as file:  # Use args.trees instead of args.tree_file
        parsed_trees = [parse_input_string(line) for line in file]

        for parsed_tree in parsed_trees:
            extract_rules(parsed_tree)

    handle_oov()
    binarize_rules()
    with open(args.rules, 'w') as rule_file:
        for rule in grammar_rules:
            left_side = rule.split(" -> ")[0]
            assert rule_counts[rule] > 0

            probability = math.log(rule_counts[rule] / left_counts[left_side])
            rule_file.write(rule + "\t" + str(probability) + "\n")

    with open(args.lexicon, 'w') as lexicon_file:
        for vocab_entry in vocabulary:
            left_side, right_side = vocab_entry.split(" -> ")

            assert left_counts[left_side] > 0

            probability = math.log(rule_counts[vocab_entry] / left_counts[left_side])
            lexicon_file.write(vocab_entry + "\t" + str(probability) + "\n")

def extract_rules(node: TreeNode):
    stack = [node]

    while len(stack) != 0:
        current_node = stack.pop()

        if current_node.is_leaf():
            word_counts[current_node.name] += 1
        else:
            rule = current_node.name + " ->"

            expansion = ""
            for child_node in current_node.descendants:
                expansion += " " + child_node.name

            right_counts[expansion.strip()] += 1
            rule += expansion

            rule_counts[rule] += 1
            rule_totals[rule] += 1
            left_counts[current_node.name] += 1

            if current_node.is_preterminal():
                vocabulary.add(rule)
            else:
                grammar_rules.add(rule)

        stack.extend(current_node.descendants)


def binarize_rules():
    for rule in set(grammar_rules):
        left, right = rule.split(" -> ")
        right_elements = right.split()
        if len(right_elements) <= 2:
            continue
        new_rules = split_rule(left, right_elements)

        for i in range(0, len(new_rules)):
            new_rule = new_rules[i]

            if i == len(new_rules) - 1:
                rule_counts[new_rules[-1]] = rule_counts[rule]
            else:
                assert new_rule not in rule_counts
                rule_counts[new_rule] = 1

            grammar_rules.add(new_rule)

        grammar_rules.remove(rule)


def generate_terminal_name(first_part, second_part):
    new_terminal = first_part + "+" + second_part
    terminal_usage[new_terminal] += 1

    new_terminal += str(terminal_usage[new_terminal]) + "'"
    left_counts[new_terminal] += 1

    return new_terminal


def split_rule(left_part, elements):
    stack = [(left_part, elements, [])]
    new_rules = []

    while len(stack) != 0:
        rule_fragment = stack.pop()

        left = rule_fragment[1]
        right = rule_fragment[2]

        if len(right) == 0 and len(left) > 2:
            new_terminal = generate_terminal_name(left[0], left[1])

            stack.append((rule_fragment[0], new_terminal, left[-1]))
            stack.append((new_terminal, left[:len(left) - 1], []))
        else:
            if isinstance(left, list):
                if len(left) > 0:
                    rule_fragment = (rule_fragment[0], " ".join(left), rule_fragment[2])
                else:
                    rule_fragment = (rule_fragment[0], "", rule_fragment[2])

            if isinstance(right, list):
                if len(right) > 0:
                    rule_fragment = (rule_fragment[0], rule_fragment[1], right[0])
                else:
                    rule_fragment = (rule_fragment[0], rule_fragment[1], "")

            if rule_fragment[2] == "":
                new_rules.append(rule_fragment[0] + " -> " + rule_fragment[1])
            else:
                new_rules.append(rule_fragment[0] + " -> " + rule_fragment[1] + " " + rule_fragment[2])

    return new_rules


def handle_oov():
    global vocabulary
    for vocab_entry in set(vocabulary):
        parts = vocab_entry.split(" -> ")

        if word_counts[parts[1]] == 1:
            vocabulary.remove(vocab_entry)

            new_rule = parts[0] + " -> " + "OOV"
            vocabulary.add(new_rule)

            rule_counts[new_rule] += rule_counts[vocab_entry]
            rule_counts[vocab_entry] -= 1

            if rule_counts[vocab_entry] == 0:
                del rule_counts[vocab_entry]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rules', type=str, default='rules.txt')
    parser.add_argument('--lexicon', type=str, default='lexicon.txt')
    parser.add_argument('trees', type=str)
    train_model(parser.parse_args())