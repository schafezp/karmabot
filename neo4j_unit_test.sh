#!/usr/bin/env bash
docker build -f Dockerfile.integration_testing  -t kbot_neo4j_testing . &&
docker run --rm -it -v "${pwd}"/session/:/karmabot/session --env-file .env integration_testing "python3 -m test.neo4j_unit_tests"