# pull official base image
FROM node:latest

RUN mkdir -p /usr/src/app

# set working directory
WORKDIR /usr/src/app

# install app dependencies
COPY ./ui/package.json /usr/src/app/

RUN npm install

# start app
CMD ["npm", "start"]