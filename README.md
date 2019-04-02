
[![CircleCI](https://img.shields.io/circleci/project/github/NCAR/xdev-bot/master.svg?style=for-the-badge&logo=circleci)](https://circleci.com/gh/NCAR/xdev-bot/tree/master)
[![Codecoverage](https://img.shields.io/codecov/c/github/NCAR/xdev-bot.svg?style=for-the-badge)](https://codecov.io/gh/NCAR/xdev-bot)



# Xdev Bot 

This is a GitHub bot for tracking and managing **Xdev Team** work. It runs on Heroku and uses the [@xdev-bot](https://github.com/xdev-bot) GitHub user.

## Helpful Citations:

- GitHub Events Documentation:  see https://developer.github.com/v3/activity/events/types/
- Payload Examples: see https://github.com/NCAR/xdev-bot/tree/master/payloads_examples
- xdev-bot Webhook:  https://github.com/NCAR/xdev/settings/hooks/88451786
- xdev-bot Test Repo:  https://github.com/NCAR/xdev-bot-testing
- xdev Project Board: https://github.com/NCAR/xdev/projects/1

## Deployment 

- Login to your account on Heroku : https://dashboard.heroku.com/apps
- Click “New” > “Create a new app”. 
- Type in the app name, choose the United States region, and click “Create app” button and assign a name for the bot `xdev-bot`
- Once your web app has been created, go to the Deploy tab. Under “Deployment method”, choose GitHub. Connect your GitHub account if you haven’t done that.
- Under “Search for a repository to connect to”, enter your project name, e.g “xdev-bot”. Press “Search”. Once it found the right repo, press “Connect”
- Scroll down. Under Deploy a GitHub branch, choose “master”, and click “Deploy Branch”.

- Watch the build log, and wait until it finished.

- When you see “Your app was successfully deployed”, click on the “View” button.


**NOTE:** Install Heroku toolbelt to see your logs. Once you have Heroku toolbelt installed, you can read the logs by:

```console
heroku logs -a xdev-bot
```
