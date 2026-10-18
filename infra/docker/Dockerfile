FROM node:24-alpine

WORKDIR /app
ARG APP_RELEASE=blue
ENV NODE_ENV=production PORT=8080 APP_RELEASE=${APP_RELEASE}
COPY --chown=node:node package.json ./
COPY --chown=node:node app/src ./app/src
COPY --chown=node:node app/public ./app/public
COPY --chown=node:node app/releases ./app/releases
USER node
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD node -e "fetch('http://127.0.0.1:8080/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"
CMD ["node", "app/src/server.js"]
