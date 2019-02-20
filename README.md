# Xdev Bot 

This is a GitHub bot for Xdev Team. It will run on Heroku and uses the [@xdev-bot](https://github.com/xdev-bot) GitHub user.


## Deployment 

- Login to your account on Heroku : https://dashboard.heroku.com/apps
- Click “New” > “Create a new app”. 
- Type in the app name, choose the United States region, and click “Create app” button and assign a name for the bot `xdev-bot`
- Once your web app has been created, go to the Deploy tab. Under “Deployment method”, choose GitHub. Connect your GitHub account if you haven’t done that.
- Under “Search for a repository to connect to”, enter your project name, e.g “xdev-bot”. Press “Search”. Once it found the right repo, press “Connect”
- Scroll down. Under Deploy a GitHub branch, choose “master”, and click “Deploy Branch”.

- Watch the build log, and wait until it finished.

- When you see “Your app was successfully deployed”, click on the “View” button.

- You should see “Hello world.”. Copy the website URL.

**NOTE:** Install Heroku toolbelt to see your logs. Once you have Heroku toolbelt installed, you can read the logs by:

```console
heroku logs -a xdev-bot
```