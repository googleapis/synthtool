# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY ./ .

# install and link project
RUN python setup.py install

# copy the content of the local src directory to the working directory

# command to run on container start
CMD [ "python", "/code/synthtool", "template" ]
