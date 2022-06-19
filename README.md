# hotel_booking_bot
Rasa implementation of a hotel booking chatbot

This chatbot requires the "DucklingEntityExtractor" that is running as a separate docker container. To start it you have to use:
```
docker run -p 8000:8000 rasa/duckling
```