#!/bin/bash

DOCKER_LABEL=localhost/text_adventure_testing
if [ "$(docker images -q "${DOCKER_LABEL}")"x == ""x ]; then
  docker build -t "${DOCKER_LABEL}" test_docker/
fi
docker run --rm -it -v $(pwd):/app "${DOCKER_LABEL}" "${@}"
