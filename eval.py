from argparse import ArgumentParser
from collections import defaultdict
from tree import parse_input_string
from pcyk import Parser
import sys


def evaluate(args):
    """
    Evaluate the parser on a set of gold-standard trees.
    """
    parser = Parser(args.rule_file, args.vocab_file, args.beam_width)
    total_lp = 0
    total_lr = 0
    sentence_count = 0

    with open(args.tree_file) as file:
        for line in file:
            gold_tree = parse_input_string(line)
            tokens = [node.name for node in gold_tree.get_terminals()]

            if args.max_length and len(tokens) <= args.max_length:
                parsed_result = parser.parse_sentence(tokens)
                if parsed_result:
                    parsed_tree = parsed_result[1]
                    print(parsed_tree)
                    remove_binary_nodes(parsed_tree)

                    correct_constituents = count_correct_constituents(parsed_tree, gold_tree)
                    lp = correct_constituents / len(parsed_tree.get_nonterminals())
                    lr = correct_constituents / len(gold_tree.get_nonterminals())

                    print(lp, lr, parsed_tree, gold_tree, sep='\t', flush=True)
                    total_lp += lp
                    total_lr += lr
                    sentence_count += 1
                else:
                    print('No parse found for "{}"'.format(' '.join(tokens)), file=sys.stderr)

    print('Average LP =', total_lp / sentence_count, file=sys.stderr)
    print('Average LR =', total_lr / sentence_count, file=sys.stderr)
    print('Total sentences =', sentence_count, file=sys.stderr)


def count_correct_constituents(parsed_tree, gold_tree):
    """
    Count the number of correct constituents in the parsed tree compared to the gold tree.
    """
    gold_constituents = extract_constituents(gold_tree)

    stack = [parsed_tree]
    correct_count = 0

    while len(stack) > 0:
        current_tree = stack.pop()

        constituent = ""
        for child in current_tree.descendants:
            constituent += str(child)

        if (current_tree.name, constituent) in gold_constituents:
            correct_count += 1

        stack.extend(current_tree.descendants)

    return correct_count


def extract_constituents(tree):
    """
    Extract all constituents from a tree.
    """
    constituents = set()
    stack = [tree]

    while len(stack) > 0:
        current_tree = stack.pop()

        constituent = ""
        for child in current_tree.descendants:
            constituent += str(child)

        if constituent != "":
            constituents.add((current_tree.name, constituent))

        stack.extend(current_tree.descendants)

    return constituents


def remove_binary_nodes(tree):
    """
    Remove binary nodes from the tree to simplify it.
    """
    stack = [tree]

    while len(stack) > 0:
        current_tree = stack.pop()

        new_descendants = []
        temp_stack = []
        temp_stack.extend(current_tree.descendants)

        while len(temp_stack) > 0:
            child = temp_stack.pop()

            if child.is_binary():
                temp_stack.extend(child.descendants)
            else:
                new_descendants.append(child)

        new_descendants.reverse()
        current_tree.descendants = new_descendants

        stack.extend(current_tree.descendants)


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('--rule_file', type=str, default='rules.txt')
    arg_parser.add_argument('--vocab_file', type=str, default='lexicon.txt')
    arg_parser.add_argument('--beam_width', type=int, default=100)
    arg_parser.add_argument('--max_length', type=int, default=25)
    arg_parser.add_argument('tree_file')
    evaluate(arg_parser.parse_args())