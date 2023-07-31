# Rasa implementation of a hotel booking chatbot

## 1. Setup procedure  

- Clone this repositiory
```
https://github.com/subrockmann/hotel_booking_bot.git
```
- Change into the repository
```
cd hotel_booking_bot
```
- Create a conda environement with all the necessary libraries
```
conda env create -f environment.yml
```
- Activate the environment
```
conda activate rasa
```
### Things that can go wrong
In case you get an error about watchdog events
```
pip install --upgrade watchdog
```
The chatbot requires [Docker](https://www.docker.com/), if you do not have installed it follow the installation guidelines at [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)


## 2. Run the chatbot
To run the rasa chatbot we need 3 terminals with activated rasa environment and Docker must be running on your machine.

1. Terminal: The chatbot requires the "DucklingEntityExtractor" that is running as a separate docker container. Start the docker container
```
docker run -p 8000:8000 rasa/duckling
```
2. Terminal: Start the rasa actions server
```
rasa run actions
```
3. Terminal: In this terminal you can interact with the chatbot on the command line
```
rasa shell
```
If you want to get more information about what is happening in the background, you can run the chatbot in ```--debug``` mode
```
rasa shell --debug
```
Once the rasa server is up and running it 
## 3. Running rasa in production
```
rasa run -m models --enable-api --cors "*" --debug
```

## 4. Extending the chatbot
When the chatbot is extended with additional training stories or intents, the underlying models have to be retrained. To check if the training data is consistent it is recommended to first validate the data

```
rasa data validate
```
and if no inconsitencies are found, continue to train the models
```
rasa train nlu
```
 
## 5. Making the chatbot robust
To make the chatbot robust it is recommended to use [interactive learning](https://rasa.com/docs/rasa/writing-stories/#using-interactive-learning)
```
rasa interactive
```
When running rasa in interactive learniing mode, the current conversation can be viewed at
[http://localhost:5005/visualization.html](http://localhost:5005/visualization.html)