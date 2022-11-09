# What is this?

Make it easier to plan multi-city trips.

Given a set of flights for a given month, find the cheapest route that covers some of the cities given the flights graph.

The flights can be passed as a csv file. By default uses a list of images (screenshots on google flights), runs OCR on the image and creates flights based on the screenshot.

# Setup

```bash
mkvirtual env trip-planner
workon trip-planner
pip install -r requirements.txt
python main.py
```
