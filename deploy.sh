zip -r txbot-prod.zip *

scp txbot-prod.zip droplet:~/txbot-prod.zip
# TODO: set bot API token with environment variable

ssh droplet << EOF
    
    if [ -d "txbot-prod" ]; then
        rm -rf txbot-prod-old
        mv txbot-prod txbot-prod-old
    fi
    unzip txbot-prod.zip -d txbot-prod

    #restore the karma_dictionary
    if [ -d "txbot-prod-old" ]; then
        cp ~/txbot-prod-old/karma_dictionary.p txbot-prod/karma_dictionary.p
        cp ~/txbot-prod-old/karma_dictionary_test.p txbot-prod/karma_dictionary_test.p
    fi
    cd ~/txbot-prod

    tmux kill-session -t bot
    tmux new-session -d -s "bot" "export PROD=true && sh run.sh"
    echo "Run Tmux ls to see running sessions"
    echo ""
    tmux ls
    echo "Script completed. Server should be running"
EOF