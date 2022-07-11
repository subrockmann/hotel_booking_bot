# hotel_booking_bot
Rasa implementation of a hotel booking chatbot

This chatbot requires the "DucklingEntityExtractor" that is running as a separate docker container. To start it you have to use:
```
docker run -p 8000:8000 rasa/duckling
```


# - I need [a]{"entity": "amount"} [single room]{"entity":"single_room"}
    # - [1]{"entity": "amount", "group": "1"} [single]{"entity":"single_room", "group":"1"} and [2]{"entity": "amount", "group": "2"} [doubles]{"entity":"double_room", "group":"2"}
    # - [2]{"entity": "amount"} [double rooms]{"entity":"double_room"}
    # - [A] {"entity": "amount"} [double]{"entity":"double_room"}
    # - We want to book [5]{"entity": "amount", "group": "1"} [doubles]{"entity":"double_room", "group":"1"} and [1]{"entity": "amount", "group": "2"} [single]{"entity":"single_room", "group":"2"}