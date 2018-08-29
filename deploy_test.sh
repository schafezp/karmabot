cp ../configs/prodenvvar.sh .
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
    sh run.sh prodenvvar.sh

    echo "Script completed. Server should be running"
EOF