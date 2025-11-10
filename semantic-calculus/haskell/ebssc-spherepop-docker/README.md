# EBSSC SpherePop (Docker + Stack)

## Build
docker build -t ebssc-spherepop:stack .

## Run
docker run --rm -it ebssc-spherepop:stack

Inside container:
  stack repl
  stack exec ebssc-demo
