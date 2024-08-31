# Discord Bot (Arsene Wenger)

[![Contributors][contributors-shield]][contributors-url]
[![Open Issues][open-issues-shield]][open-issues-url]
[![Forks][forks-shield]][forks-url]


Welcome to the best bot named after a former Arsenal manager that lives in the /r/gunners Discord channel

## Setup
This guide assumes you've already setup git and your SSH keys with your personal GitHub account.

If not already setup, follow https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

1. Fork, and download the project locally, and follow https://dev.to/codesphere/create-a-discord-bot-in-minutes-with-python-2jgp to setup the bot.
2. Switch the tracking branch of your project to your personal fork
   1. `git remote rename origin upstream`
   2. `git remote add origin <URL_OF_YOUR_FORK>`
   3. `git fetch origin`
   4. `git branch --set-upstream-to origin/master master`
3. Happy coding!
4. Add your `config.json` file:

<pre>
{
  "prefix": "!"
  "token": "discord_token"
}
</pre>

## Commands

This bot works with many different slash commands, type a slash "/" to get started.
At any point you can also issue !help to get legacy commands listed.


### Suggestions

If you have any features you would like to suggest or need any support, please don't hesitate to open an issue!

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/AndyReifman/ArseneWenger.svg?style=for-the-badge
[contributors-url]: https://github.com/AndyReifman/ArseneWenger/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/AndyReifman/ArseneWenger.svg?style=for-the-badge
[forks-url]: https://github.com/AndyReifman/ArseneWenger/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[open-issues-shield]: https://img.shields.io/github/issues/AndyReifman/ArseneWenger.svg?style=for-the-badge
[open-issues-url]: https://github.com/AndyReifman/ArseneWenger/issues
[closed-issues-shield]: https://img.shields.io/github/issues-closed/AndyReifman/ArseneWenger.svg?style=for-the-badge
[closed-issues-url]: https://github.com/AndyReifman/ArseneWenger/issues?state=closed
[license-shield]: https://img.shields.io/github/license/AndyReifman/ArseneWenger.svg?style=for-the-badge
[license-url]: https://github.com/AndyReifman/ArseneWenger/blob/main/LICENSE
