#include <stdio.h>
#include <string.h>
#include <ctype.h>

/*
  semantic-impedance
  A toy, *non-semantic* proxy metric: counts redundancy + cross-links as "impedance".
  It is intentionally crude: it supports your essay tooling without pretending to judge truth.
  Usage: semantic-impedance < file.txt
*/

static int is_word_char(int c) { return isalnum(c) || c=='_' || c=='-'; }

int main(void) {
  long chars = 0, words = 0, lines = 0;
  long parens = 0, refs = 0, commas = 0;
  int c, in_word = 0;

  while ((c = getchar()) != EOF) {
    chars++;
    if (c == '\n') lines++;
    if (c == '(' || c == ')' || c == '[' || c == ']') parens++;
    if (c == ',') commas++;
    if (c == '\\') refs++; /* crude proxy for TeX macro density */

    if (is_word_char(c)) {
      if (!in_word) { in_word = 1; words++; }
    } else in_word = 0;
  }

  double density = (words > 0) ? ((double)refs + (double)parens + (double)commas) / (double)words : 0.0;

  printf("chars=%ld words=%ld lines=%ld\n", chars, words, lines);
  printf("signals: tex_macros=%ld parens=%ld commas=%ld\n", refs, parens, commas);
  printf("semantic_impedance_proxy=%.6f\n", density);
  return 0;
}

