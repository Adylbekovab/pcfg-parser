# PCFG Parser Technical Documentation

## Introduction

This document provides technical details about the PCFG (Probabilistic Context-Free Grammar) Parser implementation. The project creates a system that can analyze sentences according to grammatical rules where each rule has a probability attached to it.

## How to Use

### Setup and Installation

1. **Prerequisites**:
   - Python 3.6 or higher
   - No external dependencies required

2. **Download the Project**:
   ```bash
   git clone https://github.com/Adylbekovab/pcfg-parser.git
   cd pcfg-parser
   ```

### Step 1: Training the Grammar

Train the parser on a treebank corpus to extract grammar rules:

```bash
python train.py wsj-train.mrg --rules rules.txt --lexicon lexicon.txt
```

**Parameters**:
- `wsj-train.mrg`: Path to the training treebank file
- `--rules rules.txt`: Output file for grammar rules
- `--lexicon lexicon.txt`: Output file for lexical rules

**Output**:
- Two files will be created: `rules.txt` and `lexicon.txt`

### Step 2: Parsing Sentences

Parse new sentences using the trained grammar:

**Create an input file** (e.g., `input_sentences.txt`) with one sentence per line:
```
The stock market fell sharply today .
Investors remain cautious about future prospects .
The company announced record profits last quarter .
```

**Run the parser**:
```bash
python pcyk.py input_sentences.txt --grammar_file rules.txt --vocab_file lexicon.txt --beam_width 50 --max_length 25
```

**Parameters**:
- `input_sentences.txt`: File containing sentences to parse
- `--grammar_file rules.txt`: Grammar rules file from training
- `--vocab_file lexicon.txt`: Vocabulary file from training
- `--beam_width 50`: Number of sub-constituents to keep (higher values increase accuracy but reduce speed)
- `--max_length 25`: Maximum sentence length to parse

**Output**:
- For each sentence, displays the probability and parse tree structure

### Step 3: Evaluating Parser Performance

Evaluate the parser against a test set of gold-standard parse trees:

```bash
python eval.py wsj-test.mrg --rule_file rules.txt --vocab_file lexicon.txt --beam_width 50 --max_length 25
```

**Parameters**:
- `wsj-test.mrg`: Reference parse trees for evaluation
- `--rule_file rules.txt`: Grammar rules file
- `--vocab_file lexicon.txt`: Vocabulary file
- `--beam_width 50`: Beam width for parsing
- `--max_length 25`: Maximum sentence length to evaluate

**Output**:
- Average Labeled Precision (LP)
- Average Labeled Recall (LR)
- Total sentences parsed (coverage)

### Example Usage Workflow

1. **Train the grammar**:
   ```bash
   python train.py wsj-train.mrg
   ```

2. **Create a file with test sentences**:
   ```
   echo "The company announced new products ." > test.txt
   ```

3. **Parse the sentences**:
   ```bash
   python pcyk.py test.txt
   ```

4. **Evaluate against reference parses**:
   ```bash
   python eval.py wsj-test.mrg
   ```

### Adjusting Parameters for Different Needs

- **For faster parsing** (lower accuracy): Reduce beam width
  ```bash
  python pcyk.py test.txt --beam_width 10
  ```

- **For higher accuracy** (slower): Increase beam width
  ```bash
  python pcyk.py test.txt --beam_width 100
  ```

- **For shorter sentences only**: Reduce max length
  ```bash
  python pcyk.py test.txt --max_length 15
  ```
  
## Core Components

### 1. Tree Data Structure (`tree.py`)

The foundation of the project is the tree data structure that represents grammatical structures:

- **TreeNode Class**: Represents a node in a parse tree with:
  - `name`: The label of the node (like "NP", "VP", "S", etc.)
  - `descendants`: A list of child nodes

- **Key Methods**:
  - `is_leaf()`: Checks if a node is a terminal (has no children)
  - `is_preterminal()`: Checks if a node is directly above a terminal
  - `is_binary()`: Checks if a node is created during binarization
  - `get_terminals()`: Gets all terminal nodes
  - `get_nonterminals()`: Gets all non-terminal nodes

- **Tree Parsing Functions**:
  - `parse_input_string()`: Converts strings like "(S (NP the) (VP works))" into TreeNode objects

### 2. Grammar Training (`train.py`)

This component extracts grammar rules from example parse trees:

- **Rule Extraction**:
  - Walks through each tree, identifying all subtrees of depth 1
  - Counts how often each rule appears
  - Calculates probabilities for each rule
  
- **Out-of-Vocabulary Handling**:
  - Identifies rare words (appearing only once)
  - Replaces them with a special "OOV" token

- **Binarization**:
  - Converts rules with more than two symbols on the right-hand side to binary form
  - Creates new non-terminal symbols like "X+Y" to represent intermediate states
  - Preserves the original rule probabilities

- **Output**:
  - `rules.txt`: Contains non-lexical rules with log probabilities
  - `lexicon.txt`: Contains lexical rules with log probabilities

### 3. Parser Implementation (`pcyk.py`)

The core parsing algorithm that uses the trained grammar:

- **Data Structures**:
  - `grammar`: A nested dictionary for efficient rule lookup
  - `vocab`: A dictionary mapping words to possible parts of speech
  - `probabilities`: A chart storing best probabilities for each span
  - `trees`: A chart storing corresponding parse trees

- **CYK Algorithm**:
  - **Initialization**: Fill diagonal cells with lexical rules
  - **Chart Filling**: For each span length and position, find the best ways to build larger constituents
  - **Optimization**: Uses efficient data structures and beam search
  
- **Beam Search**:
  - Only keeps the top N most probable constituents for each cell
  - Significantly improves speed while maintaining accuracy

### 4. Evaluation System (`eval.py`)

Measures parser performance against reference parse trees:

- **Metrics**:
  - **Labeled Precision (LP)**: Percentage of correct constituents in the parser output
  - **Labeled Recall (LR)**: Percentage of reference constituents found by the parser
  
- **Constituent Matching**:
  - Extracts constituents from both parsed and reference trees
  - Ignores binary nodes created during binarization
  - Counts matching constituents

- **Coverage Calculation**:
  - Reports the percentage of sentences successfully parsed

## Technical Processes

### Grammar Extraction Process

1. Read each tree from the training data
2. For each subtree of depth 1, extract a rule
3. Count occurrences of each rule
4. Calculate probabilities: P(rule) = count(rule) / count(left-hand-side)
5. Apply binarization to rules with more than 2 right-hand side symbols
6. Handle rare words by replacing with OOV token
7. Save rules and lexicon with probabilities

### Parsing Process

1. Load grammar and vocabulary
2. Initialize the CYK chart with lexical rules
3. Fill the chart bottom-up:
   - For each span length
   - For each starting position
   - For each possible split point
   - Combine constituents from smaller spans
   - Keep only the best constituents (beam search)
4. Extract the best parse tree for the full sentence

### Evaluation Process

1. Parse each sentence from the test set
2. Compare the resulting tree with the reference tree:
   - Remove binarization artifacts
   - Extract constituents from both trees
   - Count matching constituents
3. Calculate LP, LR, and coverage metrics
4. Report average scores

## Optimization Details

### Data Structure Optimization

Instead of linear search through rules, the grammar uses nested dictionaries:
```python
grammar[right_side_1][right_side_2] = [(probability, left_side), ...]
```
This allows O(1) lookup of applicable rules when two constituents are being combined.

### Beam Search Implementation

For each cell in the chart:
1. Find all possible constituents and their probabilities
2. Sort by probability
3. Keep only the top N (beam width)
4. Discard the rest

This reduces the exponential growth of possibilities to a linear function of the beam width.

### Left Binarization

Rules like A → B C D are converted to:
- A → B+C D
- B+C → B C

This preserves the original tree structure while adapting to the CYK algorithm's binary constraint.

## Example Walkthrough

1. **Training**:
   - Input: "(S (NP (Det the) (N student)) (VP (V works)))"
   - Extracted rules: S → NP VP, NP → Det N, VP → V, etc.
   - Rule probabilities calculated based on frequencies

2. **Parsing**:
   - Input: "the student works"
   - CYK chart filled bottom-up
   - Final output: "(S (NP (Det the) (N student)) (VP (V works)))"

3. **Evaluation**:
   - Compare parser output with reference
   - Calculate LP and LR
   - Report coverage

## Conclusion

The PCFG Parser implementation provides an efficient and accurate way to analyze sentences according to probabilistic grammar rules. Through careful optimization and clever data structures, it achieves good performance while maintaining high accuracy.