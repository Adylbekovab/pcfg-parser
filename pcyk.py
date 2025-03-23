import sys
from argparse import ArgumentParser
from collections import defaultdict
from tree import TreeNode


def load_vocabulary(file_path):
    """
    Load the vocabulary (lexicon) from a file.
    """
    vocab = defaultdict(list)

    with open(file_path, 'r') as file:
        for line in file:
            # Format: [word -> word\tprob]
            parts = line.strip().split(" -> ")

            left_side = parts[0]

            parts = parts[1].split("\t")
            right_side = parts[0]

            probability = parts[1]

            vocab[right_side].append((float(probability), left_side))

    return vocab


def load_grammar(file_path):
    """
    Load grammar rules from a file.
    """
    grammar = defaultdict(lambda: defaultdict(list))

    with open(file_path, 'r') as file:
        for line in file:
            # Format: [word -> word\tprob]
            parts = line.strip().split(" -> ")

            left_side = parts[0]

            parts = parts[1].split("\t")
            right_sides = parts[0].split()
            probability = parts[-1]

            grammar[right_sides[0]][right_sides[1]].append((float(probability), left_side))

    return grammar


class Parser:
    def __init__(self, grammar_file, vocab_file, beam_width):
        self.grammar = load_grammar(grammar_file)
        self.vocab = load_vocabulary(vocab_file)
        self.beam_width = beam_width

    def parse_sentence(self, tokens):
        """
        Parse a sentence using the CYK algorithm with beam search.
        """
        probabilities = defaultdict(dict)  # Probabilities for each cell
        trees = defaultdict(dict)  # Parse trees for each cell

        for i, word in enumerate(tokens, start=1):
            for prob, lhs in self.vocab.get(word, []) or self.vocab['OOV']:  # Use 'OOV' if word not in vocabulary
                probabilities[i - 1, i][lhs] = prob
                trees[i - 1, i][lhs] = TreeNode(lhs, [TreeNode(word, [])])

            for j in range(i - 2, -1, -1):
                for k in range(j + 1, i):
                    for rhs1 in probabilities[j, k]:
                        for rhs2 in probabilities[k, i]:
                            for rule_prob, lhs in self.grammar[rhs1][rhs2]:
                                total_prob = rule_prob + probabilities[j, k][rhs1] + probabilities[k, i][rhs2]
                                if lhs not in probabilities[j, i] or total_prob > probabilities[j, i][lhs]:
                                    if len(probabilities[j, i]) > self.beam_width:
                                        min_key = max(probabilities[j, i], key=probabilities[j, i].get)

                                        if total_prob < probabilities[j, i][min_key]:
                                            continue

                                        del probabilities[j, i][min_key]
                                        del trees[j, i][min_key]

                                    # Update probability
                                    probabilities[j, i][lhs] = total_prob
                                    # Update parse tree
                                    trees[j, i][lhs] = TreeNode(lhs, [trees[j, k][rhs1], trees[k, i][rhs2]])

        if "S" in probabilities[0, i]:
            return (probabilities[0, i]["S"], trees[0, i]["S"])
        else:
            return None


def run_parser(args):
    """
    Run the parser on the input file.
    """
    parser = Parser(args.grammar_file, args.vocab_file, args.beam_width)
    with open(args.input_file) as file:
        for sentence in file:
            tokens = sentence.split()
            if args.max_length and len(tokens) <= args.max_length:
                result = parser.parse_sentence(tokens)
                if result:
                    print(*result, sep='\t')
                else:
                    print('No parse found for "{}"'.format(' '.join(tokens)), file=sys.stderr)


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument('--grammar_file', type=str, default='rules.txt')
    arg_parser.add_argument('--vocab_file', type=str, default='lexicon.txt')
    arg_parser.add_argument('--beam_width', type=int, default=50)
    arg_parser.add_argument('--max_length', type=int, default=25)
    arg_parser.add_argument('input_file')
    run_parser(arg_parser.parse_args())