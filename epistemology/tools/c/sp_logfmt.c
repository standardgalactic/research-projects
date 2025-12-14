#include <stdio.h>
#include <time.h>

/*
  sp-logfmt
  Wraps stdin lines into a simple timestamped log format.
  Usage:
    echo "POP node=123" | sp-logfmt >> logs/events.log
*/

static void iso8601(char *buf, size_t n) {
  time_t t = time(NULL);
  struct tm tm;
  gmtime_r(&t, &tm);
  strftime(buf, n, "%Y-%m-%dT%H:%M:%SZ", &tm);
}

int main(void) {
  char line[4096];
  char ts[64];

  while (fgets(line, sizeof(line), stdin)) {
    iso8601(ts, sizeof(ts));
    // Format: time=<...> msg="<...>"
    // Keep it intentionally minimal.
    printf("time=%s msg=\"%s\"", ts, line);
    // fgets keeps newline; avoid double newlines
    if (line[0] && line[0] != '\n' && line[strlen(line)-1] != '\n') putchar('\n');
  }
  return 0;
}

