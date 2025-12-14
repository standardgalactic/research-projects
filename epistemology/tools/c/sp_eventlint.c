#include <stdio.h>
#include <string.h>
#include <ctype.h>

/*
  sp-eventlint
  Very conservative checks for a Spherepop-ish event line:
    - starts with an ALLCAPS opcode token (e.g., POP, MERGE, LINK, COLLAPSE)
    - contains key=value pairs separated by spaces (optional)
  Usage:
    sp-eventlint < logs/events.log
  Exit code nonzero if any lines fail checks.
*/

static int is_allcaps_token(const char *s) {
  if (!s || !*s) return 0;
  for (const char *p = s; *p; p++) {
    if (*p == ' ' || *p == '\t' || *p == '\n') break;
    if (!isupper((unsigned char)*p) && *p != '_') return 0;
  }
  return 1;
}

static int looks_like_kv(const char *s) {
  // token must contain '=' and have non-empty key
  const char *eq = strchr(s, '=');
  return (eq && eq != s);
}

int main(void) {
  char line[4096];
  int bad = 0;
  long lineno = 0;

  while (fgets(line, sizeof(line), stdin)) {
    lineno++;
    if (line[0] == '\n' || line[0] == '#') continue;

    // Extract first token
    char *p = line;
    while (*p && isspace((unsigned char)*p)) p++;
    if (!is_allcaps_token(p)) {
      fprintf(stderr, "bad:%ld reason=missing_opcode line=%s", lineno, line);
      bad = 1;
      continue;
    }

    // Check remaining tokens (if any) for key=value shape
    // Skip opcode
    while (*p && !isspace((unsigned char)*p)) p++;
    while (*p) {
      while (*p && isspace((unsigned char)*p)) p++;
      if (!*p || *p=='\n') break;

      char tok[512];
      int i = 0;
      while (*p && !isspace((unsigned char)*p) && i < (int)sizeof(tok)-1) tok[i++] = *p++;
      tok[i] = '\0';

      if (!looks_like_kv(tok)) {
        fprintf(stderr, "bad:%ld reason=bad_token token=%s\n", lineno, tok);
        bad = 1;
      }
    }
  }

  return bad ? 1 : 0;
}

