cp ../configs/prodenvvar.sh .
zip -r txbot-prod.zip *

scp txbot-prod.zip droplet:~/txbot-prod.zip
# TODO: set bot API token with environment variable

ssh droplet << EOF
    
    if [ -d "txbot-prod" ]; then
        rm -rf txbot-prod-old
        mv txbot-prod txbot-prod-old
    fi
    unzip txbot-prod.zip -d txbot-prod
    cd ~/txbot-prod
    sh run.sh prodenvvar.sh

    echo "Script completed. Server should be running"
EOF