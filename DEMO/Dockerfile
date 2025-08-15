# Dockerfile para o aplicativo Next.js
FROM node:18-alpine AS base

# Instalar dependências apenas quando necessário
FROM base AS deps
# Verificar https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine para entender por que libc6-compat pode ser necessário.
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Instalar dependências baseadas no arquivo de lock preferido
# Ver https://docs.npmjs.com/cli/v7/configuring-npm#package-lock-json-only
COPY package.json package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f package-lock.json ]; then npm ci --only=production; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Reconstruir o código fonte quando necessário
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Próxima etapa: coletar informações de telemetria sobre o processo de build
# https://nextjs.org/telemetry
ENV NEXT_TELEMETRY_DISABLED 1

RUN \
  if [ -f package-lock.json ]; then npm run build; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm run build; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Imagem de produção, copiar todos os arquivos e executar next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
# https://nextjs.org/docs/advanced-features/telemetry
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Definir o diretório correto para o arquivo .next
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copiar arquivos de build (standalone)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
# set hostname to localhost
ENV HOSTNAME "0.0.0.0"

# server.js é criado pelo next build na pasta standalone
CMD ["node", "server.js"] 