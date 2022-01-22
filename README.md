# ScamKicker

A simple bot which using an API , detects reported discord scams and kicks the user if possible while deleting the message. This bot was created using [dis-snek](https://github.com/Discord-Snake-Pit/Dis-Snek.git) (dev branch).

## How to Use?

---

Simply add the bot to your server and you're done, make sure that the bot has permissions to manage messages and kick users.

## FAQ

---

<details closed>
<summary> Is there a way to check if it works without kicking? </summary>
<p>

> Yes, just DM the bot the URL you want to inspect and if it's included in the database, then it will reply back that it was found. If you want to report an url, it's recommended to go to the [API's Discord server](https://discord.gg/cT6eQjWW8H)
</p>
</details>

<details closed>
<summary> If the owner of the server is affected by a scam </summary>
<p>

> In such case, as expected if the bot has permissions it will remove the messages but won't kick the user (it can't).
</p>
</details>
<details closed>
<summary> I sent part of a Fake Nitro URL but it wasn't detected </summary>
<p>

> The issue with nitro scam is more about the clickable urls than sending the directions themselves. This bot will detect the scams which start with `http://`, after all without that part, discord doesn't convert the message to an URL, which decreases its risk by default and prevents us to kick false positives. Additonally it's reliant on the API.
</p>
</details>

<details closed>
<summary> I added the bot after the scams, will it the delete messages? </summary>
<p>

> No, this bot activates upon messages and from there it makes decisions, if the bot wasn't there, then it won't delete the messages when it wasn't present.
</p>
</details>

<details closed>
<summary> That's a cool API, how can I use it? </summary>
<p>

> The API used in the bot, was designed by [nwunder](https://nwunder.com/).
> Feel free to check the following link for [more information](https://api.sinking.yachts/docs).
</p>
</details>
<br>

## License

---

ScamKicker is developed and distributed under the Apache 2.0 license.
