cp ../configs/prodenvvar.sh .
cp ../configs/proddotenv .
zip -r txbot-test.zip *

scp txbot-test.zip droplet:~/txbot-test.zip
# TODO: set bot API token with environment variable

ssh droplet << EOF
    
    if [ -d "txbot-test" ]; then
        rm -rf txbot-test-old
        mv txbot-test txbot-test-old
    fi
    unzip txbot-test.zip -d txbot-test
    cd ~/txbot-test
    rm .env
    mv proddotenv .env
    docker-compose up -d --build

    echo "Script completed. Server should be running"
EOF