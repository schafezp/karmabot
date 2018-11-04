#!/usr/bin/env bash

#docker build -f Dockerfile.neo4j_unittest  -t kbot_neo4j_testing . &&
#docker run --rm -it -v /Users/m80891/personal/karmabot/session/:/karmabot/session --env-file .env kbot_neo4j_testing
docker-compose -f neo4j_unit_tests.yml up -d --build --no-deps
docker-compose -f neo4j_unit_tests.yml logs test