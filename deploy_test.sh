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

    #tmux kill-session -t bottest
    #tmux new-session -d -s "bottest" ""
    mv docker-compose.yml docker-compose.yml.backup
    mv docker-compose-prod.yml docker-compose.yml
    export PROD=false && docker-compose build && docker-compose up -d --no-deps && docker-compose logs bot
    
    echo "Run Tmux ls to see running sessions"
    echo ""
    tmux ls
    echo "Script completed. Server should be running"
EOF