import discord
import requests

from ColdOneCore import CoreColors

class JokeGetter:

    apiBaseUrl = "https://icanhazdadjoke.com/"

    # Gets a joke from the joke api
    @staticmethod
    def getJoke():
        joke = requests.get(JokeGetter.apiBaseUrl, headers = {"Accept": "application/json"})
        if joke.ok:
            return joke.json()['joke']
        else:
            return "Sorry, no jokes this time :cry:"

    # Creates a discord embed with a fresh joke
    @staticmethod
    def getJokeEmbed():
        joke = JokeGetter.getJoke()
        jokeEmbed = discord.Embed(color=CoreColors.MessageColor, title=joke)
        jokeEmbed.set_author(name="Joke:")
        return jokeEmbed
