[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/a-lamloum/pcfg-parser)
[![NLP](https://img.shields.io/badge/NLP-PCFG%20Parser-orange.svg)](https://github.com/Adylbekovab/pcfg-parser)
[![Algorithm](https://img.shields.io/badge/Algorithm-CYK-brightgreen.svg)](https://github.com/Adylbekovab/pcfg-parser)
[![Treebank](https://img.shields.io/badge/Data-Wall%20Street%20Journal-blue.svg)](https://github.com/Adylbekovab/pcfg-parser)

# PCFG Parser Implementation

## Project Overview

This repository contains a complete implementation of a Probabilistic Context-Free Grammar (PCFG) parser using the CYK (Cocke-Younger-Kasami) algorithm. The parser can extract grammar rules from treebanks, convert them to Chomsky Normal Form (CNF), parse sentences efficiently, and evaluate parsing performance.

## Features

- **Grammar Extraction**: Extract PCFG rules from treebank data
- **Chomsky Normal Form Conversion**: Automatically convert grammar rules to CNF
- **Efficient Parsing**: CYK algorithm with optimizations for faster parsing
- **Beam Search**: Configurable beam width to balance accuracy and speed
- **Unknown Word Handling**: OOV (Out Of Vocabulary) handling for improved coverage
- **Evaluation**: Tools to measure Labeled Precision and Labeled Recall

## Repository Structure

```
.
├── train.py          # Grammar extraction from treebanks
├── pcyk.py           # CYK parser implementation
├── eval.py           # Evaluation tools
├── tree.py           # Tree data structure and utilities
├── wsj-train.mrg     # Wall Street Journal training data
├── wsj-test.mrg      # Wall Street Journal test data
├── README.md         # This documentation
```

## Prerequisites

- Python 3.6+
- Standard Python libraries (no external dependencies)

## Usage Guide

### 1. Training a Grammar

The first step is to extract a PCFG from a treebank corpus:

```bash
python train.py wsj-train.mrg --rules rules.txt --lexicon lexicon.txt
```

Parameters:
- `wsj-train.mrg`: Input treebank file
- `--rules rules.txt`: Output file for grammar rules
- `--lexicon lexicon.txt`: Output file for lexical rules

This will generate two files:
- `rules.txt`: Contains non-lexical rules with probabilities
- `lexicon.txt`: Contains lexical rules with probabilities

During this process, the code:
1. Extracts rules from the parse trees
2. Counts rule frequencies
3. Calculates probabilities
4. Converts rules to Chomsky Normal Form
5. Handles rare words by replacing them with OOV

### 2. Parsing Sentences

To parse sentences using the trained grammar:

```bash
python pcyk.py input_sentences.txt --grammar_file rules.txt --vocab_file lexicon.txt --beam_width 50 --max_length 25
```

Parameters:
- `input_sentences.txt`: File containing sentences to parse
- `--grammar_file rules.txt`: Grammar rules file from training
- `--vocab_file lexicon.txt`: Vocabulary file from training
- `--beam_width 50`: Number of sub-constituents to keep (higher values increase accuracy but reduce speed)
- `--max_length 25`: Maximum sentence length to parse

The parser will output for each sentence:
- The probability of the most likely parse
- The parse tree in bracket notation

### 3. Evaluating the Parser

To evaluate parser performance:

```bash
python eval.py wsj-test.mrg --rule_file rules.txt --vocab_file lexicon.txt --beam_width 50 --max_length 25
```

Parameters:
- `wsj-test.mrg`: Reference parse trees for evaluation
- `--rule_file rules.txt`: Grammar rules file
- `--vocab_file lexicon.txt`: Vocabulary file
- `--beam_width 50`: Beam width for parsing
- `--max_length 25`: Maximum sentence length to evaluate

The evaluation outputs:
- Average Labeled Precision (LP)
- Average Labeled Recall (LR)
- Total sentences parsed (coverage)

## Technical Details

### Grammar Extraction

Rules are extracted by identifying subtrees of depth 1 in the training data. Each rule is assigned a probability based on its relative frequency.

### Chomsky Normal Form

All rules are converted to CNF, where each rule has either:
- Exactly one terminal symbol, or
- Exactly two non-terminal symbols

Rules with more than two symbols are binarized using intermediate non-terminals.

### Performance Optimizations

Two key optimizations improve parser efficiency:
1. **Data Structure Optimization**: Grammar rules are stored in nested dictionaries for faster lookup
2. **Beam Search**: Only the n most probable sub-constituents are kept in each cell

### Unknown Word Handling

Words that appear only once in training data are replaced with an "OOV" (Out Of Vocabulary) token. At parsing time, unknown words are treated as OOV, allowing the parser to handle words not seen during training.

### Evaluation Metrics

- **Labeled Precision (LP)**: Proportion of constituents in the parser output that match the reference parse
- **Labeled Recall (LR)**: Proportion of constituents in the reference parse that are found in the parser output
- **Coverage**: Percentage of sentences for which a parse was found

## Performance

With a beam width of 50, the parser achieves:
- LP ≈ 0.88
- LR ≈ 0.87
- 100% coverage on the test set

These metrics make it comparable to state-of-the-art PCFG parsers.

## Implementation Notes

### The TreeNode Class

The `TreeNode` class in `tree.py` provides the core data structure for representing parse trees. It supports:
- Traversal through iterators
- Node type checking (leaf, preterminal, nonterminal)
- Tree manipulation and comparison

### Parsing Algorithm

The CYK algorithm works bottom-up:
1. Fill in the diagonal of the chart with lexical rules
2. Fill in the upper triangular portion by combining adjacent spans
3. Select the highest probability parse for the entire sentence

### Binarization

Rules are binarized using a left-binarization strategy, creating new non-terminals of the form "X+Y" to preserve the original tree structure as much as possible.

## License

[MIT License](https://opensource.org/licenses/MIT)

## Contributors

This project was developed for a computational linguistics course assignment by Begzada Adylbekova.
