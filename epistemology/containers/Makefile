PROJECT := flyxion-manuscripts

.PHONY: build-alpine build-arch build-fedora build-nix run-alpine run-arch run-fedora run-nix

build-alpine:
	docker build -f containers/alpine.Dockerfile -t $(PROJECT):alpine .

build-arch:
	docker build -f containers/arch.Dockerfile -t $(PROJECT):arch .

build-fedora:
	docker build -f containers/fedora.Dockerfile -t $(PROJECT):fedora .

build-nix:
	docker build -f containers/nix.Dockerfile -t $(PROJECT):nix .

run-alpine:
	docker run -it --rm -v $$PWD:/opt/project $(PROJECT):alpine

run-arch:
	docker run -it --rm -v $$PWD:/opt/project $(PROJECT):arch

run-fedora:
	docker run -it --rm -v $$PWD:/opt/project $(PROJECT):fedora

run-nix:
	docker run -it --rm -v $$PWD:/opt/project $(PROJECT):nix

