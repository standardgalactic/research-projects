
SpherePOP Language Specifications Package
----------------------------------------

This archive contains:

- spherepop.bnf         : Classic BNF grammar
- spherepop.ebnf        : EBNF grammar
- spherepop.adt         : Abstract syntax (algebraic datatypes)
- spherepop.typing      : Typing rules (inference notation)
- spherepop.smallstep   : Small-step operational semantics
- spherepop.bigstep     : Big-step semantics
- spherepop.evalctx     : Evaluation contexts
- spherepop.safety      : Type soundness statement and sketch
- grammar.js            : Tree-sitter grammar scaffold (JavaScript)
- SpherePOP.g4          : ANTLR4 grammar scaffold

Usage notes:
- The tree-sitter grammar is a starting scaffold; tokenization and precedence may be refined.
- The ANTLR grammar is a runnable .g4 file for generating parsers.
- These artifacts were generated from the EBSSC/SpherePOP design notes.
