docker build -f Dockerfile.integration_testing  -t integration_testing .
docker run --rm -it -v "${pwd}"/session/:/karmabot/session --env-file .env integration_testing

