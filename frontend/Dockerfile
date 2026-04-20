FROM node:18-alpine

WORKDIR /app

# Instalar dependencias primero (capa cacheada)
COPY package.json .
RUN npm install

# Copiar el resto del proyecto
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]
