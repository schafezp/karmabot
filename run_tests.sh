docker build -f Dockerfile.integration_testing  -t integration_testing .
docker run --rm -it -v "${pwd}"/session/:/code/session integration_testing

