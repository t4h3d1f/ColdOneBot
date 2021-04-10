# ColdOneBot

To build, `git clone` this repo and `cd` into it. Then:

    docker build . -t coldonebot:TAG
    
Where TAG is some semver (0.0.0, 0.0.1, 1.0.0, etc, basically whatever you want as long as it's unique).

When it's done

    docker run -d -e DISCORD_TOKEN=yourtoken --name ColdOneBot coldonebot:0.0.0

To stop it: 

    docker ps -a #note the container ID
    docker stop containerid #only need the first few chars of the id to work

To delete the container
    docker ps -a #note the container ID
    docker rm containerid #only need the first few chars of the id to work

If you messed up, you can delete the image with
    docker images #to list images
    docker rmi coldonebot:TAG
    
    
