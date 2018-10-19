docker build -f Dockerfile.integration_testing  -t integration_testing .
docker run --rm integration_testing

