# ColdOneBot

To build, `git clone` this repo and `cd` into it. Then:

    docker build . -t coldonebot:TAG
    
Where TAG is some semver (0.0.0, 0.0.1, 1.0.0, etc, basically whatever you want as long as it's unique).

When it's done

    docker run -d -e DISCORD_TOKEN=yourtoken --name ColdOneBot --mount type=bind,source="$(pwd)/coldone.db",target="/opt/ColdOneBot/coldone.db" coldonebot:TAG
    
(Assuming your discord token is `yourtoken`, the tag is `TAG`, and you are cd'd into the same path as your `coldone.db` sqlite db.

To stop it: 

    docker ps -a #note the container ID
    docker stop containerid #only need the first few chars of the id to work

To delete the container

    docker ps -a #note the container ID
    docker rm containerid #only need the first few chars of the id to work

If you messed up, you can delete the image with (after you have removed the container)

    docker images #to list images
    docker rmi coldonebot:TAG
    
    
