To test the bot out you need to create your own telegram Bot and get the associated API token. Go to t.me/BotFather and use /newbot to create a telegram bot. Copy the token into test_env_vars.sh next to 
```
export BOT_TOKEN="TOKEN_GOES_HERE"
```
run 
```
sh scripts/server_setup.sh 
```
to setup docker.

Run 
````
sh run.sh test_env_vars.sh
```
to actually run the bot and pass in the appropriate environment variables.
