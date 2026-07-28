# Stage 1: Install dependencies
FROM node:20-alpine AS deps
WORKDIR /next

COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Production image
FROM node:20-alpine AS runner
ARG NODE_ENV=production
ENV NODE_ENV=$NODE_ENV

WORKDIR /next

RUN apk add --no-cache netcat-openbsd dos2unix

COPY --from=deps /next/node_modules ./node_modules
COPY . .
COPY entrypoint.sh /

RUN dos2unix /entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["sh", "/entrypoint.sh"]
CMD ["npm", "run", "dev"]
