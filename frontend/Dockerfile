FROM node:18-alpine

WORKDIR /app

# We are using python to serve static files for this minimal infrastructure phase
# to avoid setting up a full React build chain just to prove connectivity.
RUN apk add --no-cache python3

COPY package.json .
COPY index.html .

CMD ["npm", "start"]
