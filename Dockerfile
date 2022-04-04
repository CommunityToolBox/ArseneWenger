# Use an official Python runtime as a parent image
FROM python:3
ADD . /arseneWenger
# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r arseneWenger/requirements.txt
WORKDIR /arseneWenger


# Run app.py when the container launches
CMD ["python", "./src/bot.py"]
